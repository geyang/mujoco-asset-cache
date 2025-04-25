import os
import sys

# Add the parent directory to sys.path to import from asset_cache
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions from asset_cache
from asset_cache.asset_cache import flatten_paths, extract_paths_from_xml, transform_xml_paths


class TestXMLPathHandling:
    def test_extract_paths(self):
        """Test extracting paths from XML."""
        xml = """
        <mujoco model="test">
          <asset>
            <texture name="tex1" type="2d" file="textures/wood1.png"/>
            <texture name="tex2" type="2d" file="textures/stone0.png"/>
            <mesh name="mesh1" file="models/mesh1.stl"/>
          </asset>
        </mujoco>
        """

        paths = extract_paths_from_xml(xml)
        expected = ["textures/wood1.png", "textures/stone0.png", "models/mesh1.stl"]

        assert sorted(paths) == sorted(expected)

    def test_transform_paths(self):
        """Test transforming paths in XML."""
        xml = """
        <mujoco model="test">
          <asset>
            <texture name="tex1" type="2d" file="textures/wood1.png"/>
            <texture name="tex2" type="2d" file="textures/stone0.png"/>
            <mesh name="mesh1" file="models/mesh1.stl"/>
          </asset>
        </mujoco>
        """

        path_map = {
            "textures/wood1.png": "textures_wood1.png",
            "textures/stone0.png": "textures_stone0.png",
            "models/mesh1.stl": "models_mesh1.stl",
        }

        transformed_xml = transform_xml_paths(xml, path_map)

        # Verify all paths were replaced
        assert 'file="textures_wood1.png"' in transformed_xml
        assert 'file="textures_stone0.png"' in transformed_xml
        assert 'file="models_mesh1.stl"' in transformed_xml

    def test_extract_and_flatten(self):
        """Test the complete workflow: extract, flatten, and transform."""
        xml = """
        <mujoco model="test">
          <asset>
            <texture name="tex1" type="2d" file="assets/textures/wood1.png"/>
            <texture name="tex2" type="2d" file="assets/textures/stone0.png"/>
            <mesh name="mesh1" file="assets/models/robot/mesh1.stl"/>
            <mesh name="mesh2" file="assets/models/robot/mesh2.stl"/>
            <mesh name="mesh3" file="assets/models/human/hand.stl"/>
          </asset>
        </mujoco>
        """

        # Extract paths
        paths = extract_paths_from_xml(xml)

        # Default behavior (max_depth=2)
        flattened_paths = flatten_paths(paths)
        transformed_xml = transform_xml_paths(xml, flattened_paths)

        # With max_depth=2, paths should be preserved with some structure
        assert 'file="assets/textures/wood1.png"' in transformed_xml
        assert 'file="assets/textures/stone0.png"' in transformed_xml
        assert 'file="assets/models/robot/mesh1.stl"' in transformed_xml
        assert 'file="assets/models/robot/mesh2.stl"' in transformed_xml
        assert 'file="assets/models/human/hand.stl"' in transformed_xml
        
        # Test with explicit flattening (max_depth=0)
        flattened_paths_flat = flatten_paths(paths, max_depth=0)
        transformed_xml_flat = transform_xml_paths(xml, flattened_paths_flat)

        # Check that the paths were flattened correctly
        assert 'file="textures_wood1.png"' in transformed_xml_flat
        assert 'file="textures_stone0.png"' in transformed_xml_flat
        assert 'file="robot_mesh1.stl"' in transformed_xml_flat
        assert 'file="robot_mesh2.stl"' in transformed_xml_flat
        assert 'file="human_hand.stl"' in transformed_xml_flat

    def test_real_world_xml_example(self):
        """Test with a more realistic XML example based on MJCF format."""
        # Fix the XML declaration to be at the start of the string
        xml = '<?xml version="1.0" ?>\n<mujoco model="dual UR5e setup">\n  <compiler angle="radian" autolimits="true" assetdir="assets" meshdir="assets" texturedir="assets"/>\n  <asset>\n    <texture type="2d" name="wood" file="/path/to/textures/wood1.png"/>\n    <texture type="2d" name="stone" file="/path/to/textures/stone0.png"/>\n    <mesh class="robot" file="robotiq_2f85/base.stl"/>\n    <mesh class="robot" file="robotiq_2f85/driver.stl"/>\n    <mesh class="hand" file="shadow_hand/index.stl"/>\n    <mesh class="hand" file="shadow_hand/thumb.stl"/>\n  </asset>\n</mujoco>'

        # Extract paths
        paths = extract_paths_from_xml(xml)
        
        # Default behavior (max_depth=2)
        flattened_paths = flatten_paths(paths)
        transformed_xml = transform_xml_paths(xml, flattened_paths)
        
        # Relative paths should be preserved with the original structure since depth is 2
        assert "robotiq_2f85/base.stl" in transformed_xml
        assert "robotiq_2f85/driver.stl" in transformed_xml
        assert "shadow_hand/index.stl" in transformed_xml
        assert "shadow_hand/thumb.stl" in transformed_xml
        
        # Absolute paths should be shortened with max_depth=2
        assert "/path/to/textures_wood1.png" in transformed_xml
        assert "/path/to/textures_stone0.png" in transformed_xml
        
        # Test with explicit flattening (max_depth=0)
        flattened_paths_flat = flatten_paths(paths, max_depth=0)
        transformed_xml_flat = transform_xml_paths(xml, flattened_paths_flat)
        
        # Verify the flattened paths appear in the transformed XML
        assert "robotiq_2f85_base.stl" in transformed_xml_flat
        assert "robotiq_2f85_driver.stl" in transformed_xml_flat
        assert "shadow_hand_index.stl" in transformed_xml_flat
        assert "shadow_hand_thumb.stl" in transformed_xml_flat
        assert "textures_wood1.png" in transformed_xml_flat
        assert "textures_stone0.png" in transformed_xml_flat
