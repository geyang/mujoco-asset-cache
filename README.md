# 🗂️ Mujoco Asset Cache 

A smart utility that flattens complex asset structures for XML files (like MJCF) while preserving folder relationships. Perfect for 3D scenes and simulations!

## ✨ Features

- 🔍 Extracts file paths from XML files
- 📁 Creates a flattened but meaningful file structure 
- 📋 Copies assets to the new location with organized names
- 🔄 Updates XML references automatically

## 🚀 Installation

```bash
pip install git+https://github.com/vuer-ai/mujoco-asset-cache.git
```

## 💻 Usage

### Command Line

```bash
python -m asset_cache.asset_cache your_file.xml --cache-dir ./my_cache --asset-dir ./assets --max-depth 2
```

### Python Module

```python
from asset_cache.asset_cache import AssetCache

# Simple usage
cache = AssetCache(cache_dir="./my_cache")
transformed_xml = cache.process_xml("your_file.xml", asset_dir="./assets", max_depth=2)
```

## 🛠️ How It Works

The flattening process preserves file relationships while making the structure simpler:

```
# Original paths:
assets/models/robot/hand.stl
assets/textures/wood.png

# Flattened (default):
robot_hand.stl
textures_wood.png
```

### 📊 Control Directory Depth

Use `max_depth` to preserve specific levels of directory structure:

```python
# With max_depth=1:
# models/robots/arm/joints/elbow.stl → models/robots_arm_joints_elbow.stl

# With max_depth=2:
# models/robots/arm/joints/elbow.stl → models/robots/arm_joints_elbow.stl
```

This helps:

- 🔒 Avoid filename conflicts
- 🗂️ Maintain logical grouping
- 🧹 Simplify complex hierarchies

## 🧪 Examples

Working with deep nested structures:

```python
paths = [
    "models/robots/hand/fingers/index/tip.stl",
    "models/robots/hand/fingers/thumb/tip.stl",
]

# Default (flat):
# "index_tip.stl", "thumb_tip.stl"

# With max_depth=2:
# "models/robots/hand_fingers_index_tip.stl", "models/robots/hand_fingers_thumb_tip.stl" 
```

### Handling Absolute Paths

The library intelligently handles absolute paths, preserving the immediate parent directory:

```python
# Original:
# /path/to/assets/models/robot/hand.stl

# Flattened:
# robot_hand.stl
```

## 📝 Testing

Run tests with pytest:

```bash
python -m pytest
```

## 🤝 Contributing

Contributions welcome! Feel free to open issues or submit PRs.

---

Made with ❤️ by [Ge Yang](https://github.com/geyang)