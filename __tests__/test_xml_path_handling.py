import os
import sys
import pytest
from pathlib import Path
import xml.etree.ElementTree as ET

# Add the parent directory to sys.path to import from asset_cache
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the flatten_paths function from the other test file
from tests.test_flatten_paths import flatten_paths

def extract_paths_from_xml(xml_string):
    """
    Extract file paths from XML string, focusing on file attributes.
    
    Args:
        xml_string: XML content as string
        
    Returns:
        list: List of file paths found in the XML
    """
    paths = []
    root = ET.fromstring(xml_string)
    
    # Find all elements with 'file' attribute
    for elem in root.findall('.//*[@file]'):
        file_path = elem.get('file')
        if file_path:
            paths.append(file_path)
    
    return paths

def transform_xml_paths(xml_string, path_map):
    """
    Replace file paths in XML with their flattened versions.
    
    Args:
        xml_string: XML content as string
        path_map: Dictionary mapping original paths to flattened paths
        
    Returns:
        str: XML content with updated paths
    """
    root = ET.fromstring(xml_string)
    
    # Find all elements with 'file' attribute
    for elem in root.findall('.//*[@file]'):
        file_path = elem.get('file')
        if file_path and file_path in path_map:
            elem.set('file', path_map[file_path])
    
    return ET.tostring(root, encoding='unicode')

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
        expected = [
            "textures/wood1.png",
            "textures/stone0.png",
            "models/mesh1.stl"
        ]
        
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
            "models/mesh1.stl": "models_mesh1.stl"
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
        
        # Flatten paths
        flattened_paths = flatten_paths(paths)
        
        # Transform XML with flattened paths
        transformed_xml = transform_xml_paths(xml, flattened_paths)
        
        # Check that the paths were flattened correctly
        assert 'file="textures_wood1.png"' in transformed_xml
        assert 'file="textures_stone0.png"' in transformed_xml
        assert 'file="robot_mesh1.stl"' in transformed_xml
        assert 'file="robot_mesh2.stl"' in transformed_xml
        assert 'file="human_hand.stl"' in transformed_xml
    
    def test_real_world_xml_example(self):
        """Test with a more realistic XML example based on MJCF format."""
        xml = """
        <?xml version="1.0" ?>
        <mujoco model="dual UR5e setup">
          <compiler angle="radian" autolimits="true" assetdir="assets" meshdir="assets" texturedir="assets"/>
          <asset>
            <texture type="2d" name="wood" file="/path/to/textures/wood1.png"/>
            <texture type="2d" name="stone" file="/path/to/textures/stone0.png"/>
            <mesh class="robot" file="robotiq_2f85/base.stl"/>
            <mesh class="robot" file="robotiq_2f85/driver.stl"/>
            <mesh class="hand" file="shadow_hand/index.stl"/>
            <mesh class="hand" file="shadow_hand/thumb.stl"/>
          </asset>
        </mujoco>
        """
        
        # Extract paths
        paths = extract_paths_from_xml(xml)
        
        # Flatten paths
        flattened_paths = flatten_paths(paths)
        
        # Transform XML with flattened paths
        transformed_xml = transform_xml_paths(xml, flattened_paths)
        
        # Verify the flattened paths appear in the transformed XML
        assert "robotiq_2f85_base.stl" in transformed_xml
        assert "robotiq_2f85_driver.stl" in transformed_xml
        assert "shadow_hand_index.stl" in transformed_xml
        assert "shadow_hand_thumb.stl" in transformed_xml 