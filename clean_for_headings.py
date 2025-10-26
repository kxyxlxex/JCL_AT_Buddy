#!/usr/bin/env python3
"""
Script to remove "For X-Y" headings from instructions and capitalize "given"
"""

import json
import re
from pathlib import Path

def clean_for_headings(text):
    """Remove For X-Y headings and capitalize 'given'"""
    if not text:
        return text
    
    # Remove "For 46-50", "For 1-10", "For questions 1-10", etc.
    text = re.sub(r'^For\s+\d+-\d+\s+', '', text, flags=re.IGNORECASE).strip()
    text = re.sub(r'^For\s+questions\s+\d+-\d+\s+', '', text, flags=re.IGNORECASE).strip()
    text = re.sub(r'^For\s+questions\s+\d+-\d+\s+please\s+', '', text, flags=re.IGNORECASE).strip()
    
    # Capitalize "given" at the beginning of the instruction
    text = re.sub(r'^given\s+', 'Given ', text, flags=re.IGNORECASE)
    
    return text

def process_json_files():
    """Process all JSON files to clean For headings"""
    data_dir = Path("data")
    json_files = list(data_dir.glob("*.json"))
    
    if not json_files:
        print("No JSON files found in data directory")
        return
    
    print(f"Processing {len(json_files)} JSON files...")
    
    total_cleaned = 0
    
    for json_file in json_files:
        if json_file.name == "data_index.json":
            continue
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            file_cleaned = 0
            
            if "questions" in data:
                for question in data["questions"]:
                    # Clean instruction
                    if "instruction" in question and question["instruction"]:
                        original = question["instruction"]
                        cleaned = clean_for_headings(question["instruction"])
                        if cleaned != original:
                            question["instruction"] = cleaned
                            file_cleaned += 1
                    
                    # Clean question text
                    if "question" in question and question["question"]:
                        original = question["question"]
                        cleaned = clean_for_headings(question["question"])
                        if cleaned != original:
                            question["question"] = cleaned
                            file_cleaned += 1
            
            if file_cleaned > 0:
                # Save the cleaned file
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"  ✓ {json_file.name}: cleaned {file_cleaned} instances")
                total_cleaned += file_cleaned
            else:
                print(f"  - {json_file.name}: no For headings found")
        
        except Exception as e:
            print(f"  ✗ Error processing {json_file.name}: {e}")
    
    print(f"\nTotal instances cleaned: {total_cleaned}")

if __name__ == "__main__":
    process_json_files()
