#!/usr/bin/env python3
"""
Script to remove annoying headers from instructions in all JSON files:
- Remove "Part 1)", "Part 2)", etc.
- Remove "I.", "II.", "III.", etc. (Roman numerals)
- Remove "A.", "B.", etc. (single letters)
- Clean up any remaining artifacts
"""

import json
import re
from pathlib import Path

def clean_instruction_header(instruction):
    """Remove headers from a single instruction string"""
    if not instruction:
        return instruction
    
    # Remove leading Roman numerals with period (I., II., III., etc.)
    instruction = re.sub(r'^[IVX]+\.\s*', '', instruction)
    
    # Remove leading "Part x)" patterns
    instruction = re.sub(r'^Part\s+\d+\)\s*', '', instruction)
    
    # Remove single letter with period (A., B., etc.)
    instruction = re.sub(r'^[A-Z]\.\s*', '', instruction)
    
    # Remove any other common prefixes
    instruction = re.sub(r'^[a-z]\.\s*', '', instruction)  # lowercase letters
    
    # Clean up whitespace
    instruction = instruction.strip()
    
    return instruction

def process_json_file(file_path):
    """Process a single JSON file to remove headers from instructions"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Process each question
        if 'questions' in data:
            for question in data['questions']:
                if 'instruction' in question and question['instruction']:
                    question['instruction'] = clean_instruction_header(question['instruction'])
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all JSON files"""
    base_dir = Path("data/raw-data")
    
    processed_count = 0
    error_count = 0
    
    # Find all questions.json files
    json_files = list(base_dir.rglob("questions.json"))
    
    print(f"Found {len(json_files)} JSON files to process...")
    
    for json_file in json_files:
        print(f"Processing {json_file}")
        
        if process_json_file(json_file):
            processed_count += 1
            print(f"  ✓ Successfully processed")
        else:
            error_count += 1
            print(f"  ✗ Error processing")
    
    print(f"\nProcessing complete:")
    print(f"  ✓ Successfully processed: {processed_count}")
    print(f"  ✗ Errors: {error_count}")

if __name__ == "__main__":
    main()
