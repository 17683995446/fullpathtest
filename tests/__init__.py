"""
FullPathTest Tests Package
"""

import sys
from pathlib import Path

# Ensure the parent directory is in the path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
