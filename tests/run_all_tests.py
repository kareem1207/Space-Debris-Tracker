import unittest
import os
import sys

def run_all_tests():
    """Run all test cases and print results"""
    # Ensure parent directory is in path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Also add the test directory itself
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)
    
    # Print current path for debugging
    print("Python search path:")
    for path in sys.path:
        print(f"  {path}")
    
    # Check if main.py exists in the expected location
    main_path = os.path.join(parent_dir, "main.py")
    if os.path.exists(main_path):
        print(f"Found main.py at: {main_path}")
    else:
        print(f"main.py not found at expected location: {main_path}")
        # List files in parent directory to help debugging
        print("Files in parent directory:")
        for file in os.listdir(parent_dir):
            print(f"  {file}")
    
    print("\nRunning ISS Tracker Tests...")
    print("=" * 50)
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    tests = loader.discover(os.path.dirname(os.path.abspath(__file__)))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(tests)
    
    print("\nTest Summary:")
    print(f"Ran {result.testsRun} tests")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
