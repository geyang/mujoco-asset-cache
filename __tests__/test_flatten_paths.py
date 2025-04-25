import os
import sys

# Add the parent directory to sys.path to import from asset_cache
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import flatten_paths from the asset_cache module
from asset_cache import flatten_paths

def test_empty_list():
    """Test with an empty list of paths."""
    assert flatten_paths([]) == {}

def test_already_flat():
    """Test paths that are already flat (no directories)."""
    paths = ["file1.txt", "file2.txt", "file3.txt"]
    result = flatten_paths(paths)
    expected = {p: p for p in paths}
    assert result == expected

def test_simple_hierarchy():
    """Test simple folder hierarchy flattening."""
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

def test_nested_hierarchy():
    """Test nested folder hierarchy with common prefix removal."""
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
    assert result == expected

def test_real_xml_example():
    """Test with real-world XML file paths including absolute paths."""
    paths = [
        "/Users/ge/mit/robohive/robohive/simhive/furniture_sim/../furniture_sim/common/textures/wood1.png",
        "/Users/ge/mit/robohive/robohive/simhive/furniture_sim/../furniture_sim/common/textures/stone0.png",
        "/Users/ge/mit/robohive/robohive/simhive/furniture_sim/../furniture_sim/common/textures/stone1.png",
        "robotiq_2f85/base_mount.stl",
        "robotiq_2f85/base.stl",
        "robotiq_2f85/driver.stl"
    ]
    
    result = flatten_paths(paths)
    
    # Check correct handling of relative paths
    assert result["robotiq_2f85/base_mount.stl"] == "robotiq_2f85_base_mount.stl"
    assert result["robotiq_2f85/base.stl"] == "robotiq_2f85_base.stl"
    
    # Check correct handling of absolute paths
    assert "textures_wood1.png" in result[paths[0]]
    assert "textures_stone0.png" in result[paths[1]]

def test_mixed_paths():
    """Test handling of mixed absolute and relative paths."""
    current_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    paths = [
        os.path.join(parent_dir, "assets/robotiq_2f85/base.stl"),
        "assets/shadow_hand/index.stl",
        "/tmp/something.txt"
    ]
    
    result = flatten_paths(paths)
    
    # Special case paths should be preserved
    assert result["/tmp/something.txt"] == "/tmp/something.txt"
    
    # Asset paths should be flattened correctly
    assert "robotiq_2f85_base.stl" in result[paths[0]]
    assert "shadow_hand_index.stl" in result[paths[1]]

def test_with_base_dir():
    """Test using a specified base directory for flattening."""
    paths = [
        "assets/robotiq_2f85/base.stl",
        "assets/robotiq_2f85/driver.stl",
        "assets/shadow_hand/index.stl"
    ]
    
    result = flatten_paths(paths, base_dir="assets")
    expected = {
        "assets/robotiq_2f85/base.stl": "robotiq_2f85_base.stl",
        "assets/robotiq_2f85/driver.stl": "robotiq_2f85_driver.stl",
        "assets/shadow_hand/index.stl": "shadow_hand_index.stl"
    }
    assert result == expected

def test_max_depth_parameter():
    """Test preserving different levels of directory structure using max_depth."""
    paths = [
        "models/robots/hand/fingers/index/tip.stl",
        "models/robots/hand/fingers/thumb/tip.stl",
        "models/robots/arm/joints/shoulder.stl",
        "models/robots/arm/joints/elbow.stl",
    ]
    
    # Default behavior (flatten to immediate parent)
    result_default = flatten_paths(paths)
    expected_default = {
        "models/robots/hand/fingers/index/tip.stl": "index_tip.stl",
        "models/robots/hand/fingers/thumb/tip.stl": "thumb_tip.stl",
        "models/robots/arm/joints/shoulder.stl": "joints_shoulder.stl",
        "models/robots/arm/joints/elbow.stl": "joints_elbow.stl",
    }
    assert result_default == expected_default
    
    # Preserve top directory (models)
    result_depth1 = flatten_paths(paths, max_depth=1)
    expected_depth1 = {
        "models/robots/hand/fingers/index/tip.stl": "models/robots_hand_fingers_index_tip.stl",
        "models/robots/hand/fingers/thumb/tip.stl": "models/robots_hand_fingers_thumb_tip.stl",
        "models/robots/arm/joints/shoulder.stl": "models/robots_arm_joints_shoulder.stl",
        "models/robots/arm/joints/elbow.stl": "models/robots_arm_joints_elbow.stl",
    }
    assert result_depth1 == expected_depth1
    
    # Preserve two levels (models/robots)
    result_depth2 = flatten_paths(paths, max_depth=2)
    expected_depth2 = {
        "models/robots/hand/fingers/index/tip.stl": "models/robots/hand_fingers_index_tip.stl",
        "models/robots/hand/fingers/thumb/tip.stl": "models/robots/hand_fingers_thumb_tip.stl",
        "models/robots/arm/joints/shoulder.stl": "models/robots/arm_joints_shoulder.stl",
        "models/robots/arm/joints/elbow.stl": "models/robots/arm_joints_elbow.stl",
    }
    assert result_depth2 == expected_depth2

def test_conflicts_with_max_depth():
    """Test how max_depth helps resolve filename conflicts."""
    paths = [
        "project/models/hand/fingers/index/tip.stl",
        "project/models/foot/fingers/index/tip.stl",
    ]
    
    # With max_depth=1, both files have unique prefixes
    result_depth1 = flatten_paths(paths, max_depth=1)
    assert result_depth1["project/models/hand/fingers/index/tip.stl"] == "project/models_hand_fingers_index_tip.stl"
    assert result_depth1["project/models/foot/fingers/index/tip.stl"] == "project/models_foot_fingers_index_tip.stl"
    
    # With max_depth=2, we preserve two levels that differentiate the files
    result_depth2 = flatten_paths(paths, max_depth=2)
    assert result_depth2["project/models/hand/fingers/index/tip.stl"] == "project/models/hand_fingers_index_tip.stl"
    assert result_depth2["project/models/foot/fingers/index/tip.stl"] == "project/models/foot_fingers_index_tip.stl" 