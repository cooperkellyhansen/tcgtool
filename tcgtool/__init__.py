"""
Pokemon TCG Price Analysis Tool

A comprehensive tool for tracking and analyzing Pokemon Trading Card Game prices
with Power BI integration.
"""

__version__ = "1.0.0"
__author__ = "Pokemon TCG Price Tool"

from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directory
DATA_DIR = PROJECT_ROOT / "data"
EXPORTS_DIR = PROJECT_ROOT / "exports"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
