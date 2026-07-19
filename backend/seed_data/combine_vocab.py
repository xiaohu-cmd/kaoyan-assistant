#!/usr/bin/env python3
"""Combine all vocabulary parts into vocab_5500.json."""
import json
import os
import sys

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# Import data from parts
sys.path.insert(0, DATA_DIR)

# Load each part
from part_a_high import HIGH_WORDS
from part_b_high import HIGH_WORDS_B
from part_c_high import HIGH_WORDS_C
from part_d_mid import MID_WORDS_A
from part_e_mid import MID_WORDS_B
from part_f_low import LOW_WORDS_A
from part_g_high import HIGH_WORDS_G

# Combine all words
all_data = []
seen_words = set()

def add_words(words, freq_level):
    """Add words with deduplication."""
    for w in words:
        word_key = w[0].lower()
        if word_key not in seen_words:
            seen_words.add(word_key)
            entry = {
                "word": w[0],
                "phonetic": w[1],
                "part_of_speech": w[2],
                "meaning": w[3],
                "example_sentence": w[4],
                "example_translation": w[5],
                "frequency_level": freq_level
            }
            all_data.append(entry)

add_words(HIGH_WORDS, "high")
add_words(HIGH_WORDS_B, "high")
add_words(HIGH_WORDS_C, "high")
add_words(HIGH_WORDS_G, "high")
add_words(MID_WORDS_A, "mid")
add_words(MID_WORDS_B, "mid")
add_words(LOW_WORDS_A, "low")

# Write output
OUT = os.path.join(DATA_DIR, "vocab_5500.json")
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"Generated {OUT}")
print(f"Total words: {len(all_data)}")
print(f"  High: {sum(1 for w in all_data if w['frequency_level'] == 'high')}")
print(f"  Mid:  {sum(1 for w in all_data if w['frequency_level'] == 'mid')}")
print(f"  Low:  {sum(1 for w in all_data if w['frequency_level'] == 'low')}")
