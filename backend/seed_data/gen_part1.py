#!/usr/bin/env python3
"""Generate vocab_5500.json — comprehensive CET-6 / Postgraduate vocabulary."""
import json, os, sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocab_5500.json")

# Each entry: (word, phonetic, pos, meaning, example, translation, freq_level)
RAW = []
