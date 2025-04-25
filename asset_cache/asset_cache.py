"""
Asset cache module for flattening file structures while preserving relative paths.

This module provides functionality to:
1. Extract file paths from XML files
2. Flatten directory structures while preserving folder relationships
3. Create a cache of assets with flattened paths
4. Transform XML files to use the flattened paths
"""

import os
import sys
import shutil
import logging
from pathlib import Path
import xml.etree.ElementTree as ET

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


def create_asset_cache(xml_file, output_dir, asset_dir=None):
    """
    Create an asset cache from XML file by:
    1. Extracting file paths from XML
    2. Flattening the paths
    3. Copying files to output directory with flattened names
    4. Transforming the XML to use the new paths
    
    Args:
        xml_file: Path to XML file
        output_dir: Directory to store cached assets
        asset_dir: Optional base directory for resolving relative paths
        
    Returns:
        tuple: (Path to transformed XML file, dict mapping original paths to cached paths)
    """
    logger.info(f"Creating asset cache for {xml_file} in {output_dir}")
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Read the XML file
    with open(xml_file, 'r') as f:
        xml_content = f.read()
    
    # Extract paths from XML
    paths = extract_paths_from_xml(xml_content)
    logger.info(f"Found {len(paths)} paths in XML file")
    
    # Flatten paths
    flattened_paths = flatten_paths(paths, base_dir=asset_dir)
    
    # Copy files to output directory with flattened names
    copied_paths = {}
    for original_path, flattened_path in flattened_paths.items():
        # Handle both absolute and relative paths
        if os.path.isabs(original_path):
            source_path = Path(original_path)
        else:
            # If it's a relative path and we have an asset_dir, use it as base
            if asset_dir:
                source_path = Path(asset_dir) / original_path
            else:
                # Use the directory of the XML file as base
                source_path = Path(xml_file).parent / original_path
        
        # Create the destination path
        dest_path = output_dir / flattened_path
        
        # Check if source file exists (if not, we'll just update the XML without copying)
        if source_path.exists():
            # Create parent directories if needed
            dest_path.parent.mkdir(exist_ok=True, parents=True)
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            logger.info(f"Copied {source_path} to {dest_path}")
            
            # Record the new path (relative to output_dir)
            copied_paths[original_path] = str(flattened_path)
        else:
            # Keep the original path if we couldn't find the file
            copied_paths[original_path] = original_path
            logger.warning(f"Could not find source file {source_path}, keeping original path")
    
    # Transform XML to use new paths
    transformed_xml = transform_xml_paths(xml_content, copied_paths)
    
    # Write transformed XML to output directory
    xml_filename = Path(xml_file).name
    transformed_xml_path = output_dir / f"transformed_{xml_filename}"
    with open(transformed_xml_path, 'w') as f:
        f.write(transformed_xml)
    
    logger.info(f"Created transformed XML at {transformed_xml_path}")
    
    return transformed_xml_path, copied_paths


class AssetCache:
    """
    Class for managing asset caching operations.
    Provides a simplified interface to the asset caching functions.
    """
    
    def __init__(self, cache_dir=None):
        """
        Initialize the AssetCache.
        
        Args:
            cache_dir: Directory to store cached assets. Defaults to './asset_cache'
        """
        self.cache_dir = Path(cache_dir or './asset_cache')
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"Initialized AssetCache with cache directory: {self.cache_dir}")
    
    def process_xml(self, xml_file, asset_dir=None):
        """
        Process an XML file to create a cached version with flattened asset paths.
        
        Args:
            xml_file: Path to XML file
            asset_dir: Optional base directory for resolving relative paths
            
        Returns:
            Path: Path to the transformed XML file
        """
        xml_file = Path(xml_file)
        xml_name = xml_file.stem
        output_dir = self.cache_dir / xml_name
        
        transformed_xml_path, _ = create_asset_cache(xml_file, output_dir, asset_dir)
        
        return transformed_xml_path


def main():
    """
    Command-line interface for the asset cache.
    
    Usage: python -m asset_cache.asset_cache <xml_file> [--cache-dir CACHE_DIR] [--asset-dir ASSET_DIR]
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Cache assets from XML files with flattened paths")
    parser.add_argument("xml_file", help="Path to XML file containing asset references")
    parser.add_argument("--cache-dir", help="Directory to store cached assets", default="./asset_cache")
    parser.add_argument("--asset-dir", help="Base directory for resolving relative paths in XML")
    
    args = parser.parse_args()
    
    cache = AssetCache(args.cache_dir)
    transformed_xml = cache.process_xml(args.xml_file, args.asset_dir)
    
    logger.info(f"Successfully created asset cache. Transformed XML available at: {transformed_xml}")


if __name__ == "__main__":
    main()
