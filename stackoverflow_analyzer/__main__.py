"""
Main entry point for running the Stack Overflow Analyzer as a module.

This allows the library to be run directly with:
python -m stackoverflow_analyzer schema.csv raw_data.csv
"""

from .cli import main

if __name__ == "__main__":
    main()