#!/usr/bin/env python3
"""
Script to clean instruction headers from all JSON files:
- Remove Part x), For X-Y, I., II., etc. headers
- Capitalize first word after For X-Y removal
- Handle multiple headers in single instruction
- Replace ending punctuation with colon
"""

import json
import re
from pathlib import Path

def clean_instruction(instruction):
    """Clean instruction text by removing headers and formatting"""
    if not instruction:
        return instruction
    
    # List of useless headers to remove as prefixes (case insensitive)
    useless_headers = [
        # FJCL Forum patterns
        "FJCL State Latin Forum – Derivatives 1 -",
        "FJCL State Latin Forum – Derivatives I -", 
        "FJCL State Latin Forum – Derivatives II -",
        "FJCL State Latin Forum – Derivatives -",
        "FJCL State Latin Forum – Mythology -",
        "FJCL State Latin Forum – Vocabulary 1 -",
        "FJCL State Latin Forum – Vocabulary I -",
        "FJCL State Latin Forum – Vocabulary II -",
        "FJCL State Latin Forum – Vocabulary -",
        "FJCL State Latin Forum – History -",
        "FJCL State Latin Forum – Mottoes -",
        "FJCL State Latin Forum – Phrases -",
        "FJCL State Latin Forum – Abbreviations -",
        "FJCL State Latin Forum – Quotations -",
        "FJCL State Latin Forum – Classical Art -",
        "FJCL State Latin Forum – Classical Geography -",
        "FJCL State Latin Forum – History of the Empire -",
        "FJCL State Latin Forum – History of the Monarchy and Republic -",
        "FJCL State Latin Forum – History of the Monarchy & Republic -",
        "FJCL State Latin Forum – Mottoes, Abbreviations, and Quotations -",
        "FJCL State Latin Forum – Mottoes, Abbreviations, & Quotations -",
        
        # Year + FJCL patterns
        "2015 FJCL State Latin Forum",
        "2014 FJCL State Latin Forum", 
        "2013 FJCL State Latin Forum",
        "2012 FJCL State Latin Forum",
        "2011 FJCL State Latin Forum",
        "2010 FJCL State Latin Forum",
        "2009 FJCL State Latin Forum",
        "2019 FJCL State Forum",
        "2018 FJCL State Forum",
        "2017 FJCL State Forum",
        "2016 FJCL State Forum",
        "2015 FJCL State Forum",
        "2014 FJCL State Forum",
        "2013 FJCL State Forum",
        "2012 FJCL State Forum",
        "2011 FJCL State Forum",
        "2010 FJCL State Forum",
        "2009 FJCL State Forum",
        
        # Generic FJCL patterns
        "FJCL State Latin Forum",
        "FJCL State Forum",
        
        # Subject names
        "Derivatives",
        "Mythology", 
        "Vocabulary",
        "History",
        "Classical Art",
        "Classical Geography",
        "Mottoes",
        "Abbreviations",
        "Quotations",
        "Phrases",
        
        # Subject with numbers/descriptions
        "Derivatives I",
        "Derivatives II", 
        "Vocabulary I",
        "Vocabulary II",
        "History of the Empire",
        "History of the Monarchy and Republic",
        "History of the Monarchy & Republic",
        "Mottoes, Abbreviations, and Quotations",
        "Mottoes, Abbreviations, & Quotations",
        "Phrases, Mottoes, Abbreviations, and Quotations",
        
        # Roman numeral section headers
        "I. Mottoes",
        "II. Phrases", 
        "III. Abbreviations",
        "IV. Quotations",
        "Part I: Phrases",
        "Part II: Mottoes",
        "Part III: Abbreviations", 
        "Part IV: Quotations",
        
        # Other patterns
        "N.B. There are no macra on this test.",
    ]
    
    # Remove useless headers as prefixes
    for header in useless_headers:
        if instruction.lower().startswith(header.lower()):
            instruction = instruction[len(header):].strip()
            # Remove leading newlines
            while instruction.startswith('\n'):
                instruction = instruction[1:]
    
    # Remove For X-Y headings (various formats)
    instruction = re.sub(r'^For\s+\d+-\d+\s+', '', instruction, flags=re.IGNORECASE).strip()
    instruction = re.sub(r'^For\s+questions\s+\d+-\d+\s+', '', instruction, flags=re.IGNORECASE).strip()
    instruction = re.sub(r'^For\s+questions\s+\d+-\d+\s+please\s+', '', instruction, flags=re.IGNORECASE).strip()
    
    # Remove Roman numerals (I., II., III., IV., V., etc.)
    instruction = re.sub(r'^[IVX]+[\.:]\s*', '', instruction, flags=re.IGNORECASE).strip()
    
    # Remove Part headers (all formats)
    instruction = re.sub(r'^Part\s+[IVX]+[\.:]\s*', '', instruction, flags=re.IGNORECASE).strip()
    instruction = re.sub(r'^Part\s+\d+[\.:]\s*', '', instruction, flags=re.IGNORECASE).strip()
    instruction = re.sub(r'^Part\s+\d+\)\s*', '', instruction, flags=re.IGNORECASE).strip()
    
    # Handle multiple headers in sequence (e.g., "Part 1) For 46-50 given...")
    # Keep removing until no more headers are found
    max_iterations = 5  # Prevent infinite loops
    for _ in range(max_iterations):
        original = instruction
        # Remove For X-Y patterns
        instruction = re.sub(r'^For\s+\d+-\d+\s+', '', instruction, flags=re.IGNORECASE).strip()
        instruction = re.sub(r'^For\s+questions\s+\d+-\d+\s+', '', instruction, flags=re.IGNORECASE).strip()
        instruction = re.sub(r'^For\s+questions\s+\d+-\d+\s+please\s+', '', instruction, flags=re.IGNORECASE).strip()
        # Remove Roman numerals
        instruction = re.sub(r'^[IVX]+[\.:]\s*', '', instruction, flags=re.IGNORECASE).strip()
        # Remove Part headers
        instruction = re.sub(r'^Part\s+[IVX]+[\.:]\s*', '', instruction, flags=re.IGNORECASE).strip()
        instruction = re.sub(r'^Part\s+\d+[\.:]\s*', '', instruction, flags=re.IGNORECASE).strip()
        instruction = re.sub(r'^Part\s+\d+\)\s*', '', instruction, flags=re.IGNORECASE).strip()
        
        # If no change occurred, we're done
        if instruction == original:
            break
    
    # Capitalize first word (especially after For X-Y removal)
    if instruction:
        instruction = instruction[0].upper() + instruction[1:]
    
    # Replace ending punctuation with colon
    instruction = re.sub(r'[\.:!?]+\s*$', '', instruction).strip()
    if instruction:
        instruction = instruction + ':'
    
    # Replace all newlines with spaces for single-line display
    instruction = instruction.replace('\n', ' ')
    
    # Clean up multiple spaces
    instruction = re.sub(r'\s+', ' ', instruction).strip()
    
    return instruction

def process_json_file(file_path):
    """Process a single JSON file to clean instruction headers"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cleaned_count = 0
        
        # Process each question
        if 'questions' in data:
            for question in data['questions']:
                if 'instruction' in question and question['instruction']:
                    original = question['instruction']
                    cleaned = clean_instruction(original)
                    if cleaned != original:
                        question['instruction'] = cleaned
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
            print(f"  ✓ Cleaned {cleaned_count} instructions")
            total_cleaned += cleaned_count
        else:
            print(f"  - No changes needed")
        
        processed_count += 1
    
    print(f"\nProcessing complete:")
    print(f"  ✓ Files processed: {processed_count}")
    print(f"  ✓ Instructions cleaned: {total_cleaned}")

if __name__ == "__main__":
    main()
