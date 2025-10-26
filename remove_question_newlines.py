#!/usr/bin/env python3
"""
Script to remove newlines from question text in all JSON files:
- Replace all \n newlines with spaces in question text
- Clean up multiple spaces to single spaces
- Keep questions on single lines for display
"""

import json
import re
from pathlib import Path

def clean_question_text(question_text):
    """Clean question text by removing newlines and extra spaces"""
    if not question_text:
        return question_text
    
    # Replace all newlines with spaces
    cleaned_text = question_text.replace('\n', ' ')
    
    # Clean up multiple spaces to single spaces
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    return cleaned_text

def process_json_file(file_path):
    """Process a single JSON file to clean question text"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cleaned_count = 0
        
        # Process each question
        if 'questions' in data:
            for question in data['questions']:
                if 'question' in question and question['question']:
                    original = question['question']
                    cleaned = clean_question_text(original)
                    if cleaned != original:
                        question['question'] = cleaned
                        cleaned_count += 1
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return cleaned_count
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def main():
    """Main function to process all JSON files"""
    base_dir = Path("data/raw-data")
    
    # Find all questions.json files
    json_files = list(base_dir.rglob("questions.json"))
    
    print(f"Found {len(json_files)} JSON files to process...")
    
    total_cleaned = 0
    processed_count = 0
    
    for json_file in json_files:
        print(f"Processing {json_file.parent.name}...")
        
        cleaned_count = process_json_file(json_file)
        if cleaned_count > 0:
            print(f"  ✓ Cleaned {cleaned_count} questions")
            total_cleaned += cleaned_count
        else:
            print(f"  - No changes needed")
        
        processed_count += 1
    
    print(f"\nProcessing complete:")
    print(f"  ✓ Files processed: {processed_count}")
    print(f"  ✓ Questions cleaned: {total_cleaned}")

if __name__ == "__main__":
    main()
