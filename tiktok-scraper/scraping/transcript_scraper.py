import asyncio, re, json, random
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FOLDER = BASE_DIR / "data"
IN_FILE = DATA_FOLDER / "ids.json"
OUT_FILE = DATA_FOLDER / "raw_data.csv"