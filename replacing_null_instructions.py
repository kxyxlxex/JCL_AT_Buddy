#!/usr/bin/env python3
"""
Script to replace null instructions with generic professional instruction:
"Choose the response that best answers the question:"
"""

import json
from pathlib import Path

def replace_null_instructions(file_path):
    """Replace null instructions with generic instruction in a single JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        replaced_count = 0
        
        # Process each question
        if 'questions' in data:
            for question in data['questions']:
                if 'instruction' in question and question['instruction'] is None:
                    question['instruction'] = "Choose the response that best answers the question:"
                    replaced_count += 1
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return replaced_count
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def main():
    """Main function to process all JSON files"""
    base_dir = Path("data/raw-data")
    
    # Find all questions.json files
    json_files = list(base_dir.rglob("questions.json"))
    
    print(f"Found {len(json_files)} JSON files to process...")
    
    total_replaced = 0
    processed_count = 0
    
    for json_file in json_files:
        print(f"Processing {json_file.parent.name}...")
        
        replaced_count = replace_null_instructions(json_file)
        if replaced_count > 0:
            print(f"  ✓ Replaced {replaced_count} null instructions")
            total_replaced += replaced_count
        else:
            print(f"  - No null instructions found")
        
        processed_count += 1
    
    print(f"\nProcessing complete:")
    print(f"  ✓ Files processed: {processed_count}")
    print(f"  ✓ Null instructions replaced: {total_replaced}")

if __name__ == "__main__":
    main()
