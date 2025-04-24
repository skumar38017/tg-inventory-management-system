#  frontend/app/common_imports.py

# Standard library imports
import os
import sys
import platform
import logging
import json
import uuid
import re
import random
import string
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta, date, timezone
from itertools import cycle
import time
import queue
import threading
import io
import base64
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Third-party imports
import requests
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, font
from tkcalendar import Calendar, DateEntry
from PIL import Image, ImageTk

# Local imports
from config import *
from utils.field_validators import StatusEnum
from utils.window_utils import maximize_window, setup_clock_update, setup_window_closing
from widgets.generate_id import generate_inventory_id, generate_product_id

# Configure logging
logger = logging.getLogger(__name__)