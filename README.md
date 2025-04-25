# Vibe XML Asset Cache

A utility for flattening asset file structures while preserving relative folder relationships. This package is specifically designed for XML files (such as MJCF) that reference multiple assets across a complex folder structure.

## Problem

When working with 3D scenes or simulations that reference assets from various locations, the original folder structure can become complicated. This utility helps by:

1. Extracting file paths from XML files
2. Creating a flattened structure that preserves the basic relationships between files
3. Copying the assets to a new location with the flattened paths
4. Updating the XML to reference the new paths

## Installation

Clone the repository and use directly:

```bash
git clone https://github.com/yourusername/vibe_xml.git
cd vibe_xml
```

## Usage

### Command Line Interface

```bash
python -m asset_cache.asset_cache your_file.xml --cache-dir ./my_cache --asset-dir ./assets --max-depth 2
```

### As a Python Module

```python
from asset_cache import AssetCache

# Initialize the cache
cache = AssetCache(cache_dir="./my_cache")

# Process an XML file
transformed_xml = cache.process_xml("your_file.xml", asset_dir="./assets", max_depth=2)
```

### Lower-level Functions

For more control, you can use the lower-level functions:

```python
from asset_cache import flatten_paths, extract_paths_from_xml, transform_xml_paths, create_asset_cache

# Extract paths from XML content
with open("your_file.xml", "r") as f:
    xml_content = f.read()
paths = extract_paths_from_xml(xml_content)

# Flatten paths with custom max_depth
flattened_paths = flatten_paths(paths, base_dir="./assets", max_depth=2)

# For complete processing including copying files
transformed_xml_path, copied_paths = create_asset_cache(
    "your_file.xml", 
    output_dir="./my_cache",
    asset_dir="./assets",
    max_depth=2
)
```

## How It Works

The flattening process works by:

1. Identifying the common prefix among all paths
2. Creating a flattened structure where:
   - Top-level directories are preserved according to max_depth
   - Remaining directories are joined with underscores
   - The filename is preserved

For example:

```
# Default behavior (no max_depth)
assets/models/robot/hand.stl -> robot_hand.stl
assets/textures/wood.png -> textures_wood.png

# With max_depth=1:
models/robots/arm/joints/elbow.stl -> models/robots_arm_joints_elbow.stl
models/robots/hand/fingers/index/tip.stl -> models/robots_hand_fingers_index_tip.stl

# With max_depth=2:
models/robots/arm/joints/elbow.stl -> models/robots/arm_joints_elbow.stl
repo/project1/modules/auth/login.py -> repo/project1/modules_auth_login.py
```

This makes the structure as flat as possible while still preserving the relationships between files.

### Controlling Directory Depth with max_depth

The `max_depth` parameter allows you to control how many top-level directories to preserve intact:

- `max_depth=0`: Flatten all directories with underscores (e.g., `models_robots_hand_index.stl`)
- `max_depth=1`: Keep the first directory level intact (e.g., `models/robots_hand_index.stl`)
- `max_depth=2`: Keep the first two directory levels intact (e.g., `models/robots/hand_index.stl`)
- `max_depth=None` (default): Flatten everything except the immediate parent (e.g., `index.stl`)

Increasing the `max_depth` helps maintain more of the original directory structure while still creating a flatter organization than the original. This approach is particularly useful for:

1. **Avoiding filename conflicts** - By preserving more of the path, you ensure files with the same name from different directories remain distinct
2. **Maintaining logical grouping** - You can keep important organizational structures while flattening less important ones
3. **Simplifying complex hierarchies** - Works well with very deep nested folders by preserving the most important top levels

## Tests

Run the tests with pytest:

```