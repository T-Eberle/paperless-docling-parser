#!/usr/bin/env python3
"""
Synchronize dependency versions in monorepo packages.

This script updates the pgx-docling-parser-core dependency version
in dependent packages to match the core package version.
"""

import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore


def update_dependency_version(package_dir: Path, dep_name: str, new_version: str) -> bool:
    """Update a dependency version in a package's pyproject.toml."""
    pyproject_path = package_dir / "pyproject.toml"
    
    if not pyproject_path.exists():
        print(f"❌ {pyproject_path} not found")
        return False
    
    # Read the file
    content = pyproject_path.read_text()
    
    # Replace the dependency line
    old_line = f'"{dep_name}"'
    new_line = f'"{dep_name}=={new_version}"'
    
    # Also handle if it already has a version
    import re
    pattern = f'"{dep_name}(==.*?)?"'
    replacement = f'"{dep_name}=={new_version}"'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        pyproject_path.write_text(new_content)
        print(f"✅ Updated {dep_name} to {new_version} in {package_dir.name}")
        return True
    else:
        print(f"ℹ️  No changes needed in {package_dir.name}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: sync_versions.py <version>")
        print("Example: sync_versions.py 1.2.3")
        sys.exit(1)
    
    version = sys.argv[1]
    repo_root = Path(__file__).parent.parent
    
    print(f"Synchronizing dependency versions to {version}...")
    
    # Update docling_serve package
    docling_serve_dir = repo_root / "packages" / "docling_serve"
    update_dependency_version(docling_serve_dir, "pgx-docling-parser-core", version)
    
    # Update local package (when implemented)
    local_dir = repo_root / "packages" / "local"
    if local_dir.exists():
        update_dependency_version(local_dir, "pgx-docling-parser-core", version)
    
    print("✅ Version synchronization complete")


if __name__ == "__main__":
    main()

# Made with Bob
