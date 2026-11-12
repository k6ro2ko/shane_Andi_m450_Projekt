import os
import sys

ordner = os.path.join(os.path.dirname(__file__), "..", "parking")
sys.path.insert(0, os.path.join(ordner, "common"))
sys.path.insert(0, os.path.join(ordner, "pico1_kasse"))
sys.path.insert(0, os.path.join(ordner, "pico2_schranke"))
