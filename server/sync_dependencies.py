#!/usr/bin/env python3
"""
Dependency synchronization script for Vocabloom server.

This script helps maintain consistency between pyproject.toml and requirements.txt
to prevent deployment issues due to missing or mismatched dependencies.
"""

import re
import sys
from pathlib import Path

def parse_pyproject_toml(file_path):
    """Parse dependencies from pyproject.toml"""
    dependencies = {}
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the dependencies section
    deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if not deps_match:
        return dependencies
    
    deps_content = deps_match.group(1)
    
    # Parse each dependency
    for line in deps_content.split('\n'):
        line = line.strip()
        if line.startswith('"') and line.endswith('",'):
            dep = line[1:-2]  # Remove quotes and comma
            # Parse package name and version
            if '(' in dep:
                name = dep.split('(')[0].strip()
                version = dep.split('(')[1].split(')')[0].strip()
                dependencies[name] = version
            else:
                dependencies[dep] = '*'
    
    return dependencies

def parse_requirements_txt(file_path):
    """Parse dependencies from requirements.txt"""
    dependencies = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Handle packages with extras like uvicorn[standard]
                if '[' in line:
                    name = line.split('[')[0]
                    version = line.split('[')[1].split(']')[1] if ']' in line else '*'
                else:
                    parts = line.split('==')
                    if len(parts) == 2:
                        name, version = parts
                    else:
                        parts = line.split('>=')
                        if len(parts) == 2:
                            name, version = parts[1].split(',')[0]
                        else:
                            name, version = line, '*'
                
                dependencies[name] = version
    
    return dependencies

def compare_dependencies(pyproject_deps, requirements_deps):
    """Compare dependencies between the two files"""
    issues = []
    
    # Check for missing dependencies in requirements.txt
    for pkg, version in pyproject_deps.items():
        if pkg not in requirements_deps:
            issues.append(f"Missing in requirements.txt: {pkg} ({version})")
    
    # Check for missing dependencies in pyproject.toml
    for pkg, version in requirements_deps.items():
        if pkg not in pyproject_deps:
            issues.append(f"Missing in pyproject.toml: {pkg} ({version})")
    
    # Check for version mismatches
    for pkg in set(pyproject_deps.keys()) & set(requirements_deps.keys()):
        pyproject_ver = pyproject_deps[pkg]
        requirements_ver = requirements_deps[pkg]
        if pyproject_ver != requirements_ver:
            issues.append(f"Version mismatch for {pkg}: pyproject.toml={pyproject_ver}, requirements.txt={requirements_ver}")
    
    return issues

def main():
    """Main function"""
    server_dir = Path(__file__).parent
    pyproject_path = server_dir / "pyproject.toml"
    requirements_path = server_dir / "requirements.txt"
    
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        sys.exit(1)
    
    if not requirements_path.exists():
        print("Error: requirements.txt not found")
        sys.exit(1)
    
    print("🔍 Checking dependency consistency...")
    
    pyproject_deps = parse_pyproject_toml(pyproject_path)
    requirements_deps = parse_requirements_txt(requirements_path)
    
    issues = compare_dependencies(pyproject_deps, requirements_deps)
    
    if issues:
        print("❌ Found dependency inconsistencies:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n💡 Run this script after updating dependencies to ensure consistency.")
        sys.exit(1)
    else:
        print("✅ All dependencies are consistent between pyproject.toml and requirements.txt")

if __name__ == "__main__":
    main() 