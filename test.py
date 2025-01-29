import json
import pandas as pd

valid_lines = []

with open("2025/2025/01/cerberus-node-lt1_2025-01-23.txt", 'r') as file:
    for i, line in enumerate(file):
        try:
            valid_lines.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"Error on line {i+1}: {e}")