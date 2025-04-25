import os
import sys
import pytest
from pathlib import Path

# Add the parent directory to sys.path to import from asset_cache
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def flatten_paths(file_paths, base_dir=None, max_depth=None):
    """
    Find a structure that is as flat as possible while preserving relative folder relationships.
    
    Args:
        file_paths: List of file paths to flatten
        base_dir: Optional base directory to use as reference
        max_depth: Maximum depth of parent directories to preserve (None for unlimited)
        
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
            
            # Apply max_depth if specified
            if max_depth is not None and len(dirs) > max_depth:
                # Keep only max_depth levels of directories
                dirs = dirs[-max_depth:]
            
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
    
    def test_max_depth_parameter(self):
        """Test preserving parent hierarchy up to max_depth."""
        # Deep nested structure
        paths = [
            "models/robots/hand/fingers/index/tip.stl",
            "models/robots/hand/fingers/thumb/tip.stl",
            "models/robots/arm/joints/shoulder.stl",
            "models/robots/arm/joints/elbow.stl",
        ]
        
        # Default behavior (no max_depth) should preserve just the last component of the path
        result_default = flatten_paths(paths)
        expected_default = {
            "models/robots/hand/fingers/index/tip.stl": "index_tip.stl",
            "models/robots/hand/fingers/thumb/tip.stl": "thumb_tip.stl",
            "models/robots/arm/joints/shoulder.stl": "joints_shoulder.stl",
            "models/robots/arm/joints/elbow.stl": "joints_elbow.stl",
        }
        assert result_default == expected_default
        
        # With max_depth=1, should keep only the immediate parent
        result_depth1 = flatten_paths(paths, max_depth=1)
        expected_depth1 = {
            "models/robots/hand/fingers/index/tip.stl": "index_tip.stl",
            "models/robots/hand/fingers/thumb/tip.stl": "thumb_tip.stl",
            "models/robots/arm/joints/shoulder.stl": "joints_shoulder.stl",
            "models/robots/arm/joints/elbow.stl": "joints_elbow.stl",
        }
        assert result_depth1 == expected_depth1
        
        # With max_depth=2, should keep two levels of parents
        result_depth2 = flatten_paths(paths, max_depth=2)
        expected_depth2 = {
            "models/robots/hand/fingers/index/tip.stl": "fingers_index_tip.stl",
            "models/robots/hand/fingers/thumb/tip.stl": "fingers_thumb_tip.stl",
            "models/robots/arm/joints/shoulder.stl": "arm_joints_shoulder.stl",
            "models/robots/arm/joints/elbow.stl": "arm_joints_elbow.stl",
        }
        assert result_depth2 == expected_depth2
        
        # With max_depth=3, should keep three levels of parents
        result_depth3 = flatten_paths(paths, max_depth=3)
        expected_depth3 = {
            "models/robots/hand/fingers/index/tip.stl": "hand_fingers_index_tip.stl",
            "models/robots/hand/fingers/thumb/tip.stl": "hand_fingers_thumb_tip.stl",
            "models/robots/arm/joints/shoulder.stl": "robots_arm_joints_shoulder.stl",
            "models/robots/arm/joints/elbow.stl": "robots_arm_joints_elbow.stl",
        }
        assert result_depth3 == expected_depth3
        
        # With max_depth=4, should keep four levels of parents
        result_depth4 = flatten_paths(paths, max_depth=4)
        expected_depth4 = {
            "models/robots/hand/fingers/index/tip.stl": "models_robots_hand_fingers_index_tip.stl",
            "models/robots/hand/fingers/thumb/tip.stl": "models_robots_hand_fingers_thumb_tip.stl",
            "models/robots/arm/joints/shoulder.stl": "models_robots_arm_joints_shoulder.stl",
            "models/robots/arm/joints/elbow.stl": "models_robots_arm_joints_elbow.stl",
        }
        assert result_depth4 == expected_depth4
        
        # With max_depth=0, should act as if all directory structure is flattened (just the filename)
        result_depth0 = flatten_paths(paths, max_depth=0)
        expected_depth0 = {
            "models/robots/hand/fingers/index/tip.stl": "tip.stl",
            "models/robots/hand/fingers/thumb/tip.stl": "tip.stl",  # Note: this will conflict!
            "models/robots/arm/joints/shoulder.stl": "shoulder.stl",
            "models/robots/arm/joints/elbow.stl": "elbow.stl",
        }
        assert result_depth0 == expected_depth0
    
    def test_deep_nested_structure(self):
        """Test with a deeply nested structure where each level has multiple children."""
        paths = [
            "project/category1/subcategory1/group1/item1.txt",
            "project/category1/subcategory1/group2/item2.txt",
            "project/category1/subcategory2/group1/item3.txt",
            "project/category2/subcategory1/group1/item4.txt",
        ]
        
        # With max_depth=None (default), should flatten to just the immediate parent
        result_default = flatten_paths(paths)
        expected_default = {
            "project/category1/subcategory1/group1/item1.txt": "group1_item1.txt",
            "project/category1/subcategory1/group2/item2.txt": "group2_item2.txt",
            "project/category1/subcategory2/group1/item3.txt": "group1_item3.txt",
            "project/category2/subcategory1/group1/item4.txt": "group1_item4.txt",
        }
        assert result_default == expected_default
        
        # With max_depth=2, preserve two levels
        result_depth2 = flatten_paths(paths, max_depth=2)
        expected_depth2 = {
            "project/category1/subcategory1/group1/item1.txt": "subcategory1_group1_item1.txt",
            "project/category1/subcategory1/group2/item2.txt": "subcategory1_group2_item2.txt",
            "project/category1/subcategory2/group1/item3.txt": "subcategory2_group1_item3.txt",
            "project/category2/subcategory1/group1/item4.txt": "subcategory1_group1_item4.txt",
        }
        assert result_depth2 == expected_depth2
        
        # With max_depth=3, preserve three levels
        result_depth3 = flatten_paths(paths, max_depth=3)
        expected_depth3 = {
            "project/category1/subcategory1/group1/item1.txt": "category1_subcategory1_group1_item1.txt",
            "project/category1/subcategory1/group2/item2.txt": "category1_subcategory1_group2_item2.txt",
            "project/category1/subcategory2/group1/item3.txt": "category1_subcategory2_group1_item3.txt",
            "project/category2/subcategory1/group1/item4.txt": "category2_subcategory1_group1_item4.txt",
        }
        assert result_depth3 == expected_depth3
        
        # With max_depth=4, preserve all levels (project + category + subcategory + group)
        result_depth4 = flatten_paths(paths, max_depth=4)
        expected_depth4 = {
            "project/category1/subcategory1/group1/item1.txt": "project_category1_subcategory1_group1_item1.txt",
            "project/category1/subcategory1/group2/item2.txt": "project_category1_subcategory1_group2_item2.txt",
            "project/category1/subcategory2/group1/item3.txt": "project_category1_subcategory2_group1_item3.txt",
            "project/category2/subcategory1/group1/item4.txt": "project_category2_subcategory1_group1_item4.txt",
        }
        assert result_depth4 == expected_depth4
    
    def test_conflict_resolution_with_max_depth(self):
        """Test how conflicts are handled with different max_depth values."""
        paths = [
            "project/models/hand/fingers/index/tip.stl",
            "project/models/foot/fingers/index/tip.stl",
        ]
        
        # With max_depth=1, we'll have a conflict as both end up with index_tip.stl
        result_depth1 = flatten_paths(paths, max_depth=1)
        assert result_depth1["project/models/hand/fingers/index/tip.stl"] == "index_tip.stl"
        assert result_depth1["project/models/foot/fingers/index/tip.stl"] == "index_tip.stl"
        # This is a name conflict that would need resolution in a real implementation
        
        # With max_depth=2, the files still have the same pattern
        result_depth2 = flatten_paths(paths, max_depth=2)
        assert result_depth2["project/models/hand/fingers/index/tip.stl"] == "fingers_index_tip.stl"
        assert result_depth2["project/models/foot/fingers/index/tip.stl"] == "fingers_index_tip.stl"
        # Still a conflict, need to go deeper to resolve
        
        # With max_depth=3, the conflict is fully resolved by including the parent directory
        result_depth3 = flatten_paths(paths, max_depth=3)
        assert result_depth3["project/models/hand/fingers/index/tip.stl"] == "hand_fingers_index_tip.stl"
        assert result_depth3["project/models/foot/fingers/index/tip.stl"] == "foot_fingers_index_tip.stl"
        # No more conflicts
    
    def test_conflict_detection_examples(self):
        """Test with examples that demonstrate how to detect and potentially resolve conflicts."""
        paths = [
            "repo/project1/modules/auth/login.py",
            "repo/project2/modules/auth/login.py",
            "repo/project1/modules/profile/avatar.png",
            "repo/project2/modules/profile/avatar.png",
        ]
        
        # With default behavior, these files will have conflicts
        result_default = flatten_paths(paths)
        
        # Same filenames for different projects
        assert result_default["repo/project1/modules/auth/login.py"] == "auth_login.py"
        assert result_default["repo/project2/modules/auth/login.py"] == "auth_login.py"
        assert result_default["repo/project1/modules/profile/avatar.png"] == "profile_avatar.png"
        assert result_default["repo/project2/modules/profile/avatar.png"] == "profile_avatar.png"
        
        # With max_depth=3, we can resolve these conflicts
        result_depth3 = flatten_paths(paths, max_depth=3)
        assert result_depth3["repo/project1/modules/auth/login.py"] == "project1_modules_auth_login.py"
        assert result_depth3["repo/project2/modules/auth/login.py"] == "project2_modules_auth_login.py"
        assert result_depth3["repo/project1/modules/profile/avatar.png"] == "project1_modules_profile_avatar.png"
        assert result_depth3["repo/project2/modules/profile/avatar.png"] == "project2_modules_profile_avatar.png"
        
        # A real implementation might need to detect conflicts and automatically increase max_depth
        # or add a unique suffix to resolve conflicts 