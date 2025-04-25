import os
import sys
import shutil
import pytest
from pathlib import Path
import tempfile

# Add the parent directory to sys.path to import from asset_cache
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions from asset_cache
from asset_cache.asset_cache import flatten_paths, extract_paths_from_xml, create_asset_cache

class TestAssetCache:
    @pytest.fixture
    def temp_dir(self):
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Clean up after tests
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_assets(self, temp_dir):
        """Create sample assets for testing."""
        assets_dir = Path(temp_dir) / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Create some directories and files for testing
        (assets_dir / "textures").mkdir(exist_ok=True)
        (assets_dir / "models").mkdir(exist_ok=True)
        (assets_dir / "models" / "robot").mkdir(exist_ok=True)
        
        # Create some dummy files
        with open(assets_dir / "textures" / "wood.png", 'w') as f:
            f.write("dummy texture data")
        
        with open(assets_dir / "models" / "robot" / "hand.stl", 'w') as f:
            f.write("dummy model data")
        
        return assets_dir
    
    @pytest.fixture
    def sample_xml(self, temp_dir, sample_assets):
        """Create a sample XML file for testing."""
        xml_path = Path(temp_dir) / "sample.xml"
        
        xml_content = f"""<?xml version="1.0" ?>
        <mujoco model="test">
          <compiler angle="radian" assetdir="{sample_assets}"/>
          <asset>
            <texture type="2d" name="wood" file="textures/wood.png"/>
            <mesh name="hand" file="models/robot/hand.stl"/>
          </asset>
        </mujoco>
        """
        
        with open(xml_path, 'w') as f:
            f.write(xml_content)
        
        return xml_path
    
    def test_create_asset_cache(self, temp_dir, sample_xml, sample_assets):
        """Test the full asset caching workflow."""
        # Set up the output directory
        cache_dir = Path(temp_dir) / "cache"
        
        # Run the asset caching function
        transformed_xml_path, copied_paths = create_asset_cache(
            sample_xml, 
            cache_dir,
            asset_dir=sample_assets
        )
        
        # Check that the transformed XML was created
        assert transformed_xml_path.exists()
        
        # Read the transformed XML content
        with open(transformed_xml_path, 'r') as f:
            transformed_content = f.read()
        
        # Check that paths were updated in the XML - updated to match new behavior
        assert 'file="textures_wood.png"' in transformed_content
        assert 'file="robot_hand.stl"' in transformed_content
        
        # Check that files were copied to the cache directory
        assert (cache_dir / "textures_wood.png").exists()
        assert (cache_dir / "robot_hand.stl").exists()
        
        # Verify file contents were preserved
        with open(cache_dir / "textures_wood.png", 'r') as f:
            assert f.read() == "dummy texture data"
        
        with open(cache_dir / "robot_hand.stl", 'r') as f:
            assert f.read() == "dummy model data"
    
    def test_missing_files_handling(self, temp_dir, sample_xml, sample_assets):
        """Test how the asset cache handles missing files."""
        # Set up the output directory
        cache_dir = Path(temp_dir) / "cache"
        
        # Modify the XML to include a non-existent file
        xml_path = Path(temp_dir) / "sample_with_missing.xml"
        
        xml_content = f"""<?xml version="1.0" ?>
        <mujoco model="test">
          <compiler angle="radian" assetdir="{sample_assets}"/>
          <asset>
            <texture type="2d" name="wood" file="textures/wood.png"/>
            <mesh name="hand" file="models/robot/hand.stl"/>
            <texture type="2d" name="nonexistent" file="textures/nonexistent.png"/>
          </asset>
        </mujoco>
        """
        
        with open(xml_path, 'w') as f:
            f.write(xml_content)
        
        # Run the asset caching function
        transformed_xml_path, copied_paths = create_asset_cache(
            xml_path, 
            cache_dir,
            asset_dir=sample_assets
        )
        
        # Check that the transformed XML was created
        assert transformed_xml_path.exists()
        
        # Read the transformed XML content
        with open(transformed_xml_path, 'r') as f:
            transformed_content = f.read()
        
        # Check that existing paths were updated in the XML - updated to match new behavior
        assert 'file="textures_wood.png"' in transformed_content
        assert 'file="robot_hand.stl"' in transformed_content
        
        # The nonexistent file should still have its original path
        assert 'file="textures/nonexistent.png"' in transformed_content
        
        # Check that only the existing files were copied
        assert (cache_dir / "textures_wood.png").exists()
        assert (cache_dir / "robot_hand.stl").exists()
        assert not (cache_dir / "textures_nonexistent.png").exists()
    
    def test_absolute_paths(self, temp_dir, sample_assets):
        """Test handling of absolute paths in XML."""
        # Create an XML with absolute paths
        xml_path = Path(temp_dir) / "absolute_paths.xml"
        
        wood_path = sample_assets / "textures" / "wood.png"
        hand_path = sample_assets / "models" / "robot" / "hand.stl"
        
        xml_content = f"""<?xml version="1.0" ?>
        <mujoco model="test">
          <compiler angle="radian"/>
          <asset>
            <texture type="2d" name="wood" file="{wood_path}"/>
            <mesh name="hand" file="{hand_path}"/>
          </asset>
        </mujoco>
        """
        
        with open(xml_path, 'w') as f:
            f.write(xml_content)
        
        # Set up the output directory
        cache_dir = Path(temp_dir) / "cache"
        
        # Extract paths from the XML
        with open(xml_path, 'r') as f:
            xml_content = f.read()
        
        paths = extract_paths_from_xml(xml_content)
        
        # Flatten paths - test directly to verify behavior
        flattened = flatten_paths(paths)
        
        # With our new implementation, absolute paths should be flattened to use 
        # the immediate parent directory name with the filename
        assert flattened[str(wood_path)].endswith("textures_wood.png")
        assert flattened[str(hand_path)].endswith("robot_hand.stl")
        
        # Run the asset caching function
        transformed_xml_path, copied_paths = create_asset_cache(
            xml_path, 
            cache_dir
        )
        
        # Check that the transformed XML was created
        assert transformed_xml_path.exists()
        
        # Read the transformed XML content
        with open(transformed_xml_path, 'r') as f:
            transformed_content = f.read()
        
        # Verify files were copied with flattened names
        assert (cache_dir / "textures_wood.png").exists()
        assert (cache_dir / "robot_hand.stl").exists() 