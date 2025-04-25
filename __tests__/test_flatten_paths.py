import os
import sys
import pytest
from pathlib import Path

# Add the parent directory to sys.path to import from asset_cache
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import flatten_paths from asset_cache module
from asset_cache import flatten_paths

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
        """Test preserving top-level parent hierarchy up to max_depth."""
        # Deep nested structure
        paths = [
            "models/robots/hand/fingers/index/tip.stl",
            "models/robots/hand/fingers/thumb/tip.stl",
            "models/robots/arm/joints/shoulder.stl",
            "models/robots/arm/joints/elbow.stl",
        ]
        
        # Default behavior (no max_depth) should flatten everything to a single level
        result_default = flatten_paths(paths)
        expected_default = {
            "models/robots/hand/fingers/index/tip.stl": "index_tip.stl",
            "models/robots/hand/fingers/thumb/tip.stl": "thumb_tip.stl",
            "models/robots/arm/joints/shoulder.stl": "joints_shoulder.stl",
            "models/robots/arm/joints/elbow.stl": "joints_elbow.stl",
        }
        assert result_default == expected_default
        
        # With max_depth=1, preserve the top directory ("models")
        result_depth1 = flatten_paths(paths, max_depth=1)
        expected_depth1 = {
            "models/robots/hand/fingers/index/tip.stl": "models/robots_hand_fingers_index_tip.stl",
            "models/robots/hand/fingers/thumb/tip.stl": "models/robots_hand_fingers_thumb_tip.stl",
            "models/robots/arm/joints/shoulder.stl": "models/robots_arm_joints_shoulder.stl",
            "models/robots/arm/joints/elbow.stl": "models/robots_arm_joints_elbow.stl",
        }
        assert result_depth1 == expected_depth1
        
        # With max_depth=2, preserve two levels ("models/robots")
        result_depth2 = flatten_paths(paths, max_depth=2)
        expected_depth2 = {
            "models/robots/hand/fingers/index/tip.stl": "models/robots/hand_fingers_index_tip.stl",
            "models/robots/hand/fingers/thumb/tip.stl": "models/robots/hand_fingers_thumb_tip.stl",
            "models/robots/arm/joints/shoulder.stl": "models/robots/arm_joints_shoulder.stl",
            "models/robots/arm/joints/elbow.stl": "models/robots/arm_joints_elbow.stl",
        }
        assert result_depth2 == expected_depth2
        
        # With max_depth=3, preserve three levels ("models/robots/hand" or "models/robots/arm")
        result_depth3 = flatten_paths(paths, max_depth=3)
        expected_depth3 = {
            "models/robots/hand/fingers/index/tip.stl": "models/robots/hand/fingers_index_tip.stl",
            "models/robots/hand/fingers/thumb/tip.stl": "models/robots/hand/fingers_thumb_tip.stl",
            "models/robots/arm/joints/shoulder.stl": "models/robots/arm/joints_shoulder.stl",
            "models/robots/arm/joints/elbow.stl": "models/robots/arm/joints_elbow.stl",
        }
        assert result_depth3 == expected_depth3
        
        # With max_depth=4, preserve four levels (almost the entire path)
        result_depth4 = flatten_paths(paths, max_depth=4)
        expected_depth4 = {
            "models/robots/hand/fingers/index/tip.stl": "models/robots/hand/fingers/index_tip.stl",
            "models/robots/hand/fingers/thumb/tip.stl": "models/robots/hand/fingers/thumb_tip.stl",
            "models/robots/arm/joints/shoulder.stl": "models/robots/arm/joints/shoulder.stl",
            "models/robots/arm/joints/elbow.stl": "models/robots/arm/joints/elbow.stl",
        }
        assert result_depth4 == expected_depth4
        
        # With max_depth=0, default behavior (just flatten everything)
        result_depth0 = flatten_paths(paths, max_depth=0)
        expected_depth0 = {
            "models/robots/hand/fingers/index/tip.stl": "models_robots_hand_fingers_index_tip.stl",
            "models/robots/hand/fingers/thumb/tip.stl": "models_robots_hand_fingers_thumb_tip.stl",
            "models/robots/arm/joints/shoulder.stl": "models_robots_arm_joints_shoulder.stl",
            "models/robots/arm/joints/elbow.stl": "models_robots_arm_joints_elbow.stl",
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
        
        # With max_depth=1, preserve the top directory
        result_depth1 = flatten_paths(paths, max_depth=1)
        expected_depth1 = {
            "project/category1/subcategory1/group1/item1.txt": "project/category1_subcategory1_group1_item1.txt",
            "project/category1/subcategory1/group2/item2.txt": "project/category1_subcategory1_group2_item2.txt",
            "project/category1/subcategory2/group1/item3.txt": "project/category1_subcategory2_group1_item3.txt",
            "project/category2/subcategory1/group1/item4.txt": "project/category2_subcategory1_group1_item4.txt",
        }
        assert result_depth1 == expected_depth1
        
        # With max_depth=2, preserve two levels
        result_depth2 = flatten_paths(paths, max_depth=2)
        expected_depth2 = {
            "project/category1/subcategory1/group1/item1.txt": "project/category1/subcategory1_group1_item1.txt",
            "project/category1/subcategory1/group2/item2.txt": "project/category1/subcategory1_group2_item2.txt",
            "project/category1/subcategory2/group1/item3.txt": "project/category1/subcategory2_group1_item3.txt",
            "project/category2/subcategory1/group1/item4.txt": "project/category2/subcategory1_group1_item4.txt",
        }
        assert result_depth2 == expected_depth2
        
        # With max_depth=3, preserve three levels
        result_depth3 = flatten_paths(paths, max_depth=3)
        expected_depth3 = {
            "project/category1/subcategory1/group1/item1.txt": "project/category1/subcategory1/group1_item1.txt",
            "project/category1/subcategory1/group2/item2.txt": "project/category1/subcategory1/group2_item2.txt",
            "project/category1/subcategory2/group1/item3.txt": "project/category1/subcategory2/group1_item3.txt",
            "project/category2/subcategory1/group1/item4.txt": "project/category2/subcategory1/group1_item4.txt",
        }
        assert result_depth3 == expected_depth3
        
        # With max_depth=4, preserve all levels (just the filename is separated)
        result_depth4 = flatten_paths(paths, max_depth=4)
        expected_depth4 = {
            "project/category1/subcategory1/group1/item1.txt": "project/category1/subcategory1/group1/item1.txt",
            "project/category1/subcategory1/group2/item2.txt": "project/category1/subcategory1/group2/item2.txt",
            "project/category1/subcategory2/group1/item3.txt": "project/category1/subcategory2/group1/item3.txt",
            "project/category2/subcategory1/group1/item4.txt": "project/category2/subcategory1/group1/item4.txt",
        }
        assert result_depth4 == expected_depth4
    
    def test_conflict_resolution_with_max_depth(self):
        """Test how conflicts are handled with different max_depth values."""
        paths = [
            "project/models/hand/fingers/index/tip.stl",
            "project/models/foot/fingers/index/tip.stl",
        ]
        
        # With max_depth=1, we still have a conflict since it only preserves the first level
        result_depth1 = flatten_paths(paths, max_depth=1)
        assert result_depth1["project/models/hand/fingers/index/tip.stl"] == "project/models_hand_fingers_index_tip.stl"
        assert result_depth1["project/models/foot/fingers/index/tip.stl"] == "project/models_foot_fingers_index_tip.stl"
        
        # With max_depth=2, we preserve two levels which differentiates the files
        result_depth2 = flatten_paths(paths, max_depth=2)
        assert result_depth2["project/models/hand/fingers/index/tip.stl"] == "project/models/hand_fingers_index_tip.stl"
        assert result_depth2["project/models/foot/fingers/index/tip.stl"] == "project/models/foot_fingers_index_tip.stl"
        
        # With max_depth=3, we can see more of the path structure
        result_depth3 = flatten_paths(paths, max_depth=3)
        assert result_depth3["project/models/hand/fingers/index/tip.stl"] == "project/models/hand/fingers_index_tip.stl"
        assert result_depth3["project/models/foot/fingers/index/tip.stl"] == "project/models/foot/fingers_index_tip.stl"
    
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
        
        # With max_depth=1, we preserve the repo directory
        result_depth1 = flatten_paths(paths, max_depth=1)
        assert result_depth1["repo/project1/modules/auth/login.py"] == "repo/project1_modules_auth_login.py"
        assert result_depth1["repo/project2/modules/auth/login.py"] == "repo/project2_modules_auth_login.py"
        assert result_depth1["repo/project1/modules/profile/avatar.png"] == "repo/project1_modules_profile_avatar.png"
        assert result_depth1["repo/project2/modules/profile/avatar.png"] == "repo/project2_modules_profile_avatar.png"
        
        # With max_depth=2, we preserve repo/project1 and repo/project2 directories
        result_depth2 = flatten_paths(paths, max_depth=2)
        assert result_depth2["repo/project1/modules/auth/login.py"] == "repo/project1/modules_auth_login.py"
        assert result_depth2["repo/project2/modules/auth/login.py"] == "repo/project2/modules_auth_login.py"
        assert result_depth2["repo/project1/modules/profile/avatar.png"] == "repo/project1/modules_profile_avatar.png"
        assert result_depth2["repo/project2/modules/profile/avatar.png"] == "repo/project2/modules_profile_avatar.png"
        
        # With max_depth=3, we preserve even more structure
        result_depth3 = flatten_paths(paths, max_depth=3)
        assert result_depth3["repo/project1/modules/auth/login.py"] == "repo/project1/modules/auth_login.py"
        assert result_depth3["repo/project2/modules/auth/login.py"] == "repo/project2/modules/auth_login.py"
        assert result_depth3["repo/project1/modules/profile/avatar.png"] == "repo/project1/modules/profile_avatar.png"
        assert result_depth3["repo/project2/modules/profile/avatar.png"] == "repo/project2/modules/profile_avatar.png" 