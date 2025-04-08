#!/usr/bin/env python3
"""
Pipeline Runner Script

This script installs required dependencies from requirements.txt and
executes a series of Python scripts in a specific order, creating a 
data processing pipeline. Each script is expected to complete
successfully before the next one starts.
"""

import os
import subprocess
import sys
import time
from datetime import datetime

# Install dependencies from requirements.txt
def install_requirements():
    print("\n" + "=" * 60)
    print("Installing dependencies from requirements.txt")
    print("=" * 60)
    
    req_file = "requirements.txt"
    if not os.path.exists(req_file):
        print(f"❌ Error: {req_file} not found.")
        return False
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], check=True)
        print("\n✅ Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error installing dependencies. Return code: {e.returncode}")
        return False

# List of scripts to run in order
scripts = [
    "stock_fetch.py",
    "macro_fetch.py",
    "wide_form.py",
    "cleaning.py",
    "feature_creation.py",  # Note: There appears to be a typo in your list (feautre vs feature)
    "clustering.py",
    "optimization.py"
]

def run_script(script_name):
    """Run a Python script and return True if successful, False otherwise."""
    print(f"\n{'=' * 60}")
    print(f"Running {script_name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}")
    
    try:
        # Run the script using the same Python interpreter that's running this script
        result = subprocess.run([sys.executable, script_name], check=True)
        print(f"\n✅ {script_name} completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running {script_name}. Return code: {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Error: {script_name} not found.")
        return False

def main():
    start_time = time.time()
    print("Starting pipeline setup and execution")
    
    # Install dependencies first
    if not install_requirements():
        print("\n❌ Pipeline stopped due to failure installing dependencies")
        return 1
    
    # Ensure all scripts exist before starting
    missing_scripts = [script for script in scripts if not os.path.exists(script)]
    if missing_scripts:
        print("Error: The following scripts were not found:")
        for script in missing_scripts:
            print(f"  - {script}")
        print("\nPlease ensure all script files are in the current directory.")
        return 1
    
    # Run each script in order
    for i, script in enumerate(scripts):
        print(f"\nStep {i+1}/{len(scripts)}: {script}")
        success = run_script(script)
        
        if not success:
            print(f"\n❌ Pipeline stopped due to failure in {script}")
            return 1
    
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"✅ Pipeline completed successfully in {elapsed_time:.2f} seconds")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())