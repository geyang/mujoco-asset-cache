import os
import sys
import pytest
from pathlib import Path

# Add the parent directory to sys.path to import from asset_cache
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def flatten_paths(file_paths, base_dir=None):
    """
    Find a structure that is as flat as possible while preserving relative folder relationships.
    
    Args:
        file_paths: List of file paths to flatten
        base_dir: Optional base directory to use as reference
        
    Returns:
        dict: Mapping from original paths to flattened paths
    """
    if not file_paths:
        return {}
    
    # Convert all paths to Path objects for easier manipulation
    paths = [Path(p) for p in file_paths]
    
    # Find common prefix among all paths if base_dir is not specified
    if base_dir is None:
        # Get the first path's parent as initial common_prefix
        common_prefix = paths[0].parent
        
        # Iteratively find the common prefix
        for path in paths[1:]:
            parent = path.parent
            # Find common parts between current common_prefix and this path's parent
            common_parts = []
            for part1, part2 in zip(common_prefix.parts, parent.parts):
                if part1 == part2:
                    common_parts.append(part1)
                else:
                    break
            if common_parts:
                common_prefix = Path(*common_parts)
            else:
                common_prefix = Path()
                break
    else:
        common_prefix = Path(base_dir)
    
    # Create mapping from original paths to flattened paths
    result = {}
    
    for original_path in paths:
        # Skip if the path doesn't exist or isn't under common_prefix
        if not str(original_path).startswith(str(common_prefix)) and common_prefix != Path():
            result[str(original_path)] = str(original_path)
            continue
            
        # Extract the relative path from the common prefix
        if common_prefix == Path():
            relative_path = original_path
        else:
            try:
                relative_path = original_path.relative_to(common_prefix)
            except ValueError:
                # If not relative to common prefix, keep as is
                result[str(original_path)] = str(original_path)
                continue
        
        # Create a flattened path that preserves folder structure but is as flat as possible
        # Replace directory separators with underscores or other safe characters
        parts = relative_path.parts
        
        if len(parts) <= 1:
            # No need to flatten if it's already flat
            flattened = relative_path
        else:
            # Keep only the filename and prefix with parent folder names joined by underscores
            # Last part is the filename, everything before that are directories
            dirs = parts[:-1]
            filename = parts[-1]
            
            # Join directory names with underscores
            dir_prefix = "_".join(dirs)
            flattened = Path(f"{dir_prefix}_{filename}")
        
        result[str(original_path)] = str(flattened)
    
    return result


class TestFlattenPaths:
    def test_empty_list(self):
        """Test with an empty list of paths."""
        assert flatten_paths([]) == {}
    
    def test_already_flat(self):
        """Test with paths that are already flat (no directories)."""
        paths = ["file1.txt", "file2.txt", "file3.txt"]
        result = flatten_paths(paths)
        
        # Should remain unchanged
        expected = {
            "file1.txt": "file1.txt",
            "file2.txt": "file2.txt",
            "file3.txt": "file3.txt"
        }
        assert result == expected
    
    def test_simple_hierarchy(self):
        """Test with a simple folder hierarchy."""
        paths = [
            "dir1/file1.txt",
            "dir1/file2.txt",
            "dir2/file3.txt"
        ]
        
        result = flatten_paths(paths)
        expected = {
            "dir1/file1.txt": "dir1_file1.txt",
            "dir1/file2.txt": "dir1_file2.txt",
            "dir2/file3.txt": "dir2_file3.txt"
        }
        assert result == expected
    
    def test_nested_hierarchy(self):
        """Test with a nested folder hierarchy."""
        paths = [
            "assets/robotiq_2f85/base.stl",
            "assets/robotiq_2f85/driver.stl",
            "assets/shadow_hand/index.stl",
            "assets/table/wooden_table.obj"
        ]
        
        result = flatten_paths(paths)
        expected = {
            "assets/robotiq_2f85/base.stl": "robotiq_2f85_base.stl",
            "assets/robotiq_2f85/driver.stl": "robotiq_2f85_driver.stl",
            "assets/shadow_hand/index.stl": "shadow_hand_index.stl",
            "assets/table/wooden_table.obj": "table_wooden_table.obj"
        }
        
        # Note: Our implementation knows to remove the common "assets/" prefix
        assert result == expected
    
    def test_mixed_paths(self):
        """Test with a mix of absolute and relative paths."""
        # Create both absolute and relative paths
        current_dir = os.path.abspath(os.path.dirname(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        paths = [
            os.path.join(parent_dir, "assets/robotiq_2f85/base.stl"),
            "assets/shadow_hand/index.stl",
            "/tmp/something.txt"
        ]
        
        result = flatten_paths(paths)
        
        # Absolute paths should be preserved if they don't share a common prefix
        assert result["/tmp/something.txt"] == "/tmp/something.txt"
        assert "robotiq_2f85_base.stl" in result[paths[0]]
        assert "shadow_hand_index.stl" in result[paths[1]]
    
    def test_with_base_dir(self):
        """Test with a specified base directory."""
        paths = [
            "assets/robotiq_2f85/base.stl",
            "assets/robotiq_2f85/driver.stl",
            "assets/shadow_hand/index.stl"
        ]
        
        # Test with "assets" as the base directory
        result = flatten_paths(paths, base_dir="assets")
        expected = {
            "assets/robotiq_2f85/base.stl": "robotiq_2f85_base.stl",
            "assets/robotiq_2f85/driver.stl": "robotiq_2f85_driver.stl",
            "assets/shadow_hand/index.stl": "shadow_hand_index.stl"
        }
        assert result == expected
    
    def test_real_xml_example(self):
        """Test with examples similar to the XML file paths."""
        paths = [
            "/Users/ge/mit/robohive/robohive/simhive/furniture_sim/../furniture_sim/common/textures/wood1.png",
            "/Users/ge/mit/robohive/robohive/simhive/furniture_sim/../furniture_sim/common/textures/stone0.png",
            "/Users/ge/mit/robohive/robohive/simhive/furniture_sim/../furniture_sim/common/textures/stone1.png",
            "robotiq_2f85/base_mount.stl",
            "robotiq_2f85/base.stl",
            "robotiq_2f85/driver.stl"
        ]
        
        result = flatten_paths(paths)
        
        # Ensure the common prefix is detected correctly
        assert result["robotiq_2f85/base_mount.stl"] == "robotiq_2f85_base_mount.stl"
        assert result["robotiq_2f85/base.stl"] == "robotiq_2f85_base.stl"
        
        # Ensure absolute paths that share a common prefix are flattened
        assert "textures_wood1.png" in result[paths[0]]
        assert "textures_stone0.png" in result[paths[1]] 