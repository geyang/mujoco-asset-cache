import os
import sys

# Add the parent directory to sys.path to import from asset_cache
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import flatten_paths from the asset_cache module
from asset_cache.asset_cache import flatten_paths


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
    paths = ["dir1/file1.txt", "dir1/file2.txt", "dir2/file3.txt"]

    # With default (max_depth=2)
    result = flatten_paths(paths)
    # Since these paths don't exceed max_depth, they should be preserved as-is
    expected = {
        "dir1/file1.txt": "dir1/file1.txt",
        "dir1/file2.txt": "dir1/file2.txt",
        "dir2/file3.txt": "dir2/file3.txt",
    }
    assert result == expected
    
    # With max_depth=0 (explicit flattening)
    result_flat = flatten_paths(paths, max_depth=0)
    expected_flat = {
        "dir1/file1.txt": "dir1_file1.txt",  # Uses parent_filename format
        "dir1/file2.txt": "dir1_file2.txt",  # Uses parent_filename format
        "dir2/file3.txt": "dir2_file3.txt",  # Uses parent_filename format
    }
    assert result_flat == expected_flat


def test_nested_hierarchy():
    """Test nested folder hierarchy with common prefix removal."""
    paths = [
        "assets/robotiq_2f85/base.stl",
        "assets/robotiq_2f85/driver.stl",
        "assets/shadow_hand/index.stl",
        "assets/table/wooden_table.obj",
    ]

    # With default (max_depth=2)
    result = flatten_paths(paths)
    expected = {
        "assets/robotiq_2f85/base.stl":   "robotiq_2f85/base.stl",
        "assets/robotiq_2f85/driver.stl": "robotiq_2f85/driver.stl",
        "assets/shadow_hand/index.stl":   "shadow_hand/index.stl",
        "assets/table/wooden_table.obj":  "table/wooden_table.obj",
    }
    assert result == expected
    
    # With max_depth=0 (explicit flattening)
    result_flat = flatten_paths(paths, max_depth=0)
    expected_flat = {
        "assets/robotiq_2f85/base.stl":   "robotiq_2f85_base.stl",
        "assets/robotiq_2f85/driver.stl": "robotiq_2f85_driver.stl",
        "assets/shadow_hand/index.stl":   "shadow_hand_index.stl",
        "assets/table/wooden_table.obj":  "table_wooden_table.obj",
    }
    assert result_flat == expected_flat


def test_real_xml_example():
    """Test with real-world XML file paths including absolute paths."""
    paths = [
        "/Users/ge/mit/robohive/robohive/simhive/furniture_sim/../furniture_sim/common/textures/wood1.png",
        "/Users/ge/mit/robohive/robohive/simhive/furniture_sim/../furniture_sim/common/textures/stone0.png",
        "/Users/ge/mit/robohive/robohive/simhive/furniture_sim/../furniture_sim/common/textures/stone1.png",
        "robotiq_2f85/base_mount.stl",
        "robotiq_2f85/base.stl",
        "robotiq_2f85/driver.stl",
    ]

    # Test with max_depth=0 for explicit flattening
    result = flatten_paths(paths, max_depth=0)

    # Check correct handling of relative paths
    assert result["robotiq_2f85/base_mount.stl"] == "robotiq_2f85_base_mount.stl"
    assert result["robotiq_2f85/base.stl"] ==      "robotiq_2f85_base.stl"

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
        "/tmp/something.txt",
    ]

    # Test with max_depth=0 for explicit flattening
    result = flatten_paths(paths, max_depth=0)

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
        "assets/shadow_hand/index.stl",
    ]

    # Test with max_depth=0 and base_dir
    result = flatten_paths(paths, base_dir="assets", max_depth=0)
    expected = {
        "assets/robotiq_2f85/base.stl": "robotiq_2f85_base.stl",
        "assets/robotiq_2f85/driver.stl": "robotiq_2f85_driver.stl",
        "assets/shadow_hand/index.stl": "shadow_hand_index.stl",
    }
    assert result == expected


def test_max_depth_parameter():
    """Test preserving different levels of directory structures using max_depth."""
    paths = [
        "models/robots/hand/fingers/index/tip.stl",
        "models/robots/hand/fingers/thumb/tip.stl",
        "models/robots/arm/joints/shoulder.stl",
        "models/robots/arm/joints/elbow.stl",
    ]

    # Default behavior (max_depth=2)
    result_default = flatten_paths(paths)
    expected_default = {
        "models/robots/hand/fingers/index/tip.stl": "fingers/index/tip.stl",
        "models/robots/hand/fingers/thumb/tip.stl": "fingers/thumb/tip.stl",
        "models/robots/arm/joints/shoulder.stl": "arm/joints/shoulder.stl",
        "models/robots/arm/joints/elbow.stl":    "arm/joints/elbow.stl",
    }
    assert result_default == expected_default

    # With max_depth=0 (flatten everything)
    result_flat = flatten_paths(paths, max_depth=0)
    expected_flat = {
        "models/robots/hand/fingers/index/tip.stl": "index_tip.stl",
        "models/robots/hand/fingers/thumb/tip.stl": "thumb_tip.stl",
        "models/robots/arm/joints/shoulder.stl": "joints_shoulder.stl",
        "models/robots/arm/joints/elbow.stl": "joints_elbow.stl",
    }
    assert result_flat == expected_flat

    # Preserve deepest 1 level + filename
    result_depth1 = flatten_paths(paths, max_depth=1)
    expected_depth1 = {
        "models/robots/hand/fingers/index/tip.stl": "fingers/index/tip.stl",
        "models/robots/hand/fingers/thumb/tip.stl": "fingers/thumb/tip.stl",
        "models/robots/arm/joints/shoulder.stl":    "arm/joints/shoulder.stl",
        "models/robots/arm/joints/elbow.stl":       "arm/joints/elbow.stl",
    }
    assert result_depth1 == expected_depth1

    # Preserve deepest 3 levels + filename
    result_depth3 = flatten_paths(paths, max_depth=3)
    expected_depth3 = {
        "models/robots/hand/fingers/index/tip.stl": "hand/fingers/index/tip.stl",
        "models/robots/hand/fingers/thumb/tip.stl": "hand/fingers/thumb/tip.stl",
        "models/robots/arm/joints/shoulder.stl": "robots/arm/joints/shoulder.stl",
        "models/robots/arm/joints/elbow.stl": "robots/arm/joints/elbow.stl",
    }
    assert result_depth3 == expected_depth3


def test_conflicts_with_max_depth():
    """Test how max_depth helps resolve filename conflicts."""
    paths = [
        "project/models/hand/fingers/index/tip.stl",
        "project/models/foot/fingers/index/tip.stl",
    ]
    
    # Default behavior (max_depth=2)
    result_default = flatten_paths(paths)
    # With default max_depth=2, both paths preserve the deepest 2 directories + filename
    assert (
        result_default["project/models/hand/fingers/index/tip.stl"]
        == "hand/fingers/index/tip.stl"
    )
    assert (
        result_default["project/models/foot/fingers/index/tip.stl"]
        == "foot/fingers/index/tip.stl"
    )

    # With max_depth=0, we handle the conflict by adding the distinguishing directory
    result_flat = flatten_paths(paths, max_depth=0)
    assert (
        result_flat["project/models/hand/fingers/index/tip.stl"]
        == "hand_index_tip.stl"
    )
    assert (
        result_flat["project/models/foot/fingers/index/tip.stl"]
        == "foot_index_tip.stl"  # Note: conflict is resolved with distinguishing directory
    )

    # With max_depth=1, both files use a combined approach to avoid conflicts
    result_depth1 = flatten_paths(paths, max_depth=1)
    assert (
        result_depth1["project/models/hand/fingers/index/tip.stl"]
        == "hand_fingers_index_tip.stl"
    )
    assert (
        result_depth1["project/models/foot/fingers/index/tip.stl"]
        == "foot_fingers_index_tip.stl"  # This ensures unique names
    )


def test_common_prefix_removal():
    """Test handling of paths with similar structures."""
    paths = [
        "project/assets/models/robot1/hand.stl",
        "project/assets/models/robot1/arm.stl",
        "project/assets/models/robot1/leg.stl",
        "project/assets/models/robot2/hand.stl",
        "project/assets/textures/wood.png",
        "project/assets/textures/metal.png",
    ]
    
    # With max_depth=0, files use parent_filename format
    result = flatten_paths(paths, max_depth=0)
    
    # Check that each file uses its parent directory in the flattened name
    assert result["project/assets/models/robot1/hand.stl"] == "robot1_hand.stl"
    assert result["project/assets/models/robot1/arm.stl"] == "robot1_arm.stl"
    assert result["project/assets/models/robot1/leg.stl"] == "robot1_leg.stl"
    assert result["project/assets/models/robot2/hand.stl"] == "robot2_hand.stl"
    assert result["project/assets/textures/wood.png"] == "textures_wood.png"
    assert result["project/assets/textures/metal.png"] == "textures_metal.png"
    
    # With max_depth=2, we preserve the deepest 2 directory levels
    result_depth2 = flatten_paths(paths, max_depth=2)
    
    # Check that with max_depth=2, we preserve the deepest 2 levels while removing common prefixes
    assert result_depth2["project/assets/models/robot1/hand.stl"] == "robot1/hand.stl"
    assert result_depth2["project/assets/models/robot1/arm.stl"] == "robot1/arm.stl"
    assert result_depth2["project/assets/models/robot2/hand.stl"] == "robot2/hand.stl"
    assert result_depth2["project/assets/textures/wood.png"] == "textures/wood.png"
    assert result_depth2["project/assets/textures/metal.png"] == "textures/metal.png"
