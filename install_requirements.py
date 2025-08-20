#!/usr/bin/env python3
"""
Step-by-step installation script for dependencies
"""

import subprocess
import sys

def install_package(package):
    """Install a single package"""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}: {e}")
        return False

def main():
    """Install packages step by step"""
    print("Installing dependencies step by step...")
    
    # Essential build tools first
    build_tools = [
        "pip>=23.0",
        "setuptools>=65.0.0",
        "wheel>=0.37.0"
    ]
    
    # Core dependencies
    core_packages = [
        "numpy>=1.21.0",
        "torch>=1.9.0",
        "websockets>=11.0.0"
    ]
    
    # ML packages
    ml_packages = [
        "transformers>=4.20.0",
        "sentence-transformers>=2.0.0",
        "scikit-learn>=1.0.0"
    ]
    
    # Other packages
    other_packages = [
        "faiss-cpu>=1.7.0",
        "google-genai>=0.3.0",
        "PyMuPDF>=1.20.0",
        "pytest>=7.0.0"
    ]
    
    all_packages = [
        ("Build Tools", build_tools),
        ("Core Packages", core_packages),
        ("ML Packages", ml_packages),
        ("Other Packages", other_packages)
    ]
    
    failed_packages = []
    
    for category, packages in all_packages:
        print(f"\n=== Installing {category} ===")
        for package in packages:
            if not install_package(package):
                failed_packages.append(package)
    
    print("\n" + "="*50)
    if failed_packages:
        print(f"Failed to install: {failed_packages}")
        print("Try installing these manually:")
        for package in failed_packages:
            print(f"  pip install {package}")
    else:
        print("All packages installed successfully!")
    
    print("\nTo test the installation, run:")
    print("  python unit_test.py")

if __name__ == "__main__":
    main()