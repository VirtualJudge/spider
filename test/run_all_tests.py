import unittest
import os

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(unittest.defaultTestLoader.discover(start_dir=os.path.dirname(os.path.abspath(__file__)),
                                                   pattern="test_*.py"))
