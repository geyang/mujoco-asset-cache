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
python -m asset_cache.asset_cache your_file.xml --cache-dir ./my_cache --asset-dir ./assets
```

### As a Python Module

```python
from asset_cache import AssetCache

# Initialize the cache
cache = AssetCache(cache_dir="./my_cache")

# Process an XML file
transformed_xml = cache.process_xml("your_file.xml", asset_dir="./assets")
```

### Lower-level Functions

For more control, you can use the lower-level functions:

```python
from asset_cache import flatten_paths, extract_paths_from_xml, transform_xml_paths, create_asset_cache

# Extract paths from XML content
with open("your_file.xml", "r") as f:
    xml_content = f.read()
paths = extract_paths_from_xml(xml_content)

# Flatten paths
flattened_paths = flatten_paths(paths, base_dir="./assets")

# For complete processing including copying files
transformed_xml_path, copied_paths = create_asset_cache(
    "your_file.xml", 
    output_dir="./my_cache",
    asset_dir="./assets"
)
```

## How It Works

The flattening process works by:

1. Identifying the common prefix among all paths
2. Creating a flattened structure where:
   - Directory separators are replaced with underscores
   - The filename is preserved
   - The folder hierarchy is encoded in the filename prefix

For example:

```
assets/models/robot/hand.stl -> robot_hand.stl
assets/textures/wood.png -> textures_wood.png
```

This makes the structure as flat as possible while still preserving the relationships between files.

## Tests

Run the tests with pytest:

```bash
pytest
```

## License

MIT 