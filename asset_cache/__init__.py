"""
Asset cache package for flattening file structures while preserving relative paths.

This package provides functionality to cache assets referenced in XML files
into a flattened directory structure, while preserving the relative folder relationships.
"""

from .asset_cache import (
    flatten_paths,
    extract_paths_from_xml,
    transform_xml_paths,
    create_asset_cache,
    AssetCache
)

__all__ = [
    'flatten_paths',
    'extract_paths_from_xml',
    'transform_xml_paths',
    'create_asset_cache',
    'AssetCache'
] 