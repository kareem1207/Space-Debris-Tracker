"""
Configuration file for pytest to help with module imports
"""
import sys
import os

# Add parent directory to system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Check for main.py instead of main2.py
if os.path.exists(os.path.join(parent_dir, "main.py")):
    print("Found main.py in parent directory")
else:
    print("Warning: main.py not found in parent directory")
    print("Files in parent directory:")
    for file in os.listdir(parent_dir):
        print(f"  {file}")
