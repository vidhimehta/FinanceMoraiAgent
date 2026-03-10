#!/usr/bin/env python3
"""
Runner script for FinanceMoraiAgent.
This ensures proper import paths.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now run main
if __name__ == "__main__":
    import src.main
    src.main.main()
