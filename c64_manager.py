#!/usr/bin/env python
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from c64collector.cli import main

if __name__ == '__main__':
    main()
