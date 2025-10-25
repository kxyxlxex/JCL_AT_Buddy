#!/usr/bin/env python3
"""
Script to run the improved parser on all formatted test files.
"""

import os
import json
import re
from pathlib import Path

def parse_test_file(test_file_path):
    """Parse a formatted test file and extract questions with options."""
    with open(test_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    questions = []
    current_question = None
    last_instruction = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for any instruction lines (not just specific ones)
        if (line.startswith("Choose the") or 
            line.startswith("Identify the") or 
            line.startswith("Complete the") or
            line.startswith("Items") and ":" in line):
            last_instruction = line
            continue
        
        # Check for question numbers
        question_match = re.match(r'^(\d+)\.\s*(.+)$', line)
        if question_match:
            # Save previous question if exists and has at least 1 option
            if current_question and len(current_question["options"]) > 0:
                questions.append(current_question)
            
            # Start new question
            question_num = int(question_match.group(1))
            question_text = question_match.group(2).strip()
            
            # Clean up question text
            question_text = re.sub(r'Derivatives I - States \d+ - \d+', '', question_text).strip()
            
            current_question = {
                "question_number": question_num,
                "question": question_text,
                "options": {},
                "type": "multiple_choice"
            }
            
            # Apply last instruction if question has no text or is empty
            if not question_text and last_instruction:
                current_question["question"] = last_instruction
            elif question_text and last_instruction:
                current_question["question"] = f"{last_instruction} {question_text}"
            
            continue
        
        # Check for question numbers without text (like "41.")
        question_num_match = re.match(r'^(\d+)\.\s*$', line)
        if question_num_match:
            # Save previous question if exists and has at least 1 option
            if current_question and len(current_question["options"]) > 0:
                questions.append(current_question)
            
            # Start new question
            question_num = int(question_num_match.group(1))
            
            current_question = {
                "question_number": question_num,
                "question": "",
                "options": {},
                "type": "multiple_choice"
            }
            
            # Apply last instruction if question has no text
            if last_instruction:
                current_question["question"] = last_instruction
            
            continue
        
        # Check for lines that start with multiple options (like "a. Echo b. Lara c. Thetis d. Averna")
        if current_question and re.match(r'^[a-d]\.\s+', line):
            # This line contains multiple options
            if re.search(r'\s+[b-d]\.\s+', line):
                # Split the line into individual options
                parts = re.split(r'\s+([b-d])\.\s+', line)
                if len(parts) >= 3:
                    # First option (a.)
                    first_option = parts[0].strip()
                    if first_option.startswith('a. '):
                        first_option = first_option[3:].strip()
                    current_question["options"]["A"] = first_option
                    
                    # Process remaining options
                    for i in range(1, len(parts), 2):
                        if i + 1 < len(parts):
                            letter = parts[i].upper()
                            text = parts[i + 1].strip()
                            current_question["options"][letter] = text
            else:
                # Single option on the line
                option_match = re.match(r'^([a-d])\.\s+(.+)$', line)
                if option_match:
                    letter = option_match.group(1).upper()
                    text = option_match.group(2).strip()
                    current_question["options"][letter] = text
            continue
        
        # Check for options (A., B., C., D.)
        option_match = re.match(r'^([A-D])\.\s+(.+)$', line)
        if option_match and current_question:
            option_letter = option_match.group(1)
            option_text = option_match.group(2).strip()
            
            # Clean up option text - remove any instruction text that got mixed in
            option_text = re.sub(r'Choose the.*$', '', option_text).strip()
            
            current_question["options"][option_letter] = option_text
            continue
    
    # Don't forget the last question
    if current_question:
        questions.append(current_question)
    
    return questions

def parse_answer_key(key_file_path):
    """Parse the answer key file."""
    with open(key_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract answers from the key
    # Pattern: number. answer
    answer_pattern = r'(\d+)\.\s+([A-D])'
    matches = re.findall(answer_pattern, content)
    
    answers = {}
    for match in matches:
        question_num = int(match[0])
        answer = match[1]
        answers[question_num] = answer
    
    return answers

def convert_test_to_json(test_dir):
    """Convert a test directory to JSON format."""
    test_dir = Path(test_dir)
    
    # Find the test and key files
    test_files = list(test_dir.glob("*_test.txt"))
    key_files = list(test_dir.glob("*_key.txt"))
    
    if not test_files:
        print(f"No test file found in {test_dir}")
        return None
    
    if not key_files:
        print(f"No answer key found in {test_dir}")
        return None
    
    test_file = test_files[0]
    key_file = key_files[0]
    
    print(f"Processing {test_file.name} and {key_file.name}")
    
    # Parse questions and answers
    questions = parse_test_file(test_file)
    answers = parse_answer_key(key_file)
    
    if not questions:
        print(f"No questions found in {test_file}")
        return None
    
    print(f"Found {len(questions)} questions")
    
    # Match questions with answers
    for question in questions:
        question_num = question["question_number"]
        if question_num in answers:
            question["correct_answer"] = answers[question_num]
        else:
            print(f"Warning: No answer found for question {question_num}")
            question["correct_answer"] = ""
    
    # Create the JSON structure
    json_data = {
        "test_info": {
            "name": test_dir.name,
            "year": test_dir.parent.name if "state_" in test_dir.parent.name else "unknown",
            "subject": test_dir.name,
            "total_questions": len(questions)
        },
        "questions": questions
    }
    
    return json_data

def main():
    """Main function to process all test directories."""
    base_dir = Path("/Users/kylexu/JCL_AT_Buddy/data/raw-data")
    
    if not base_dir.exists():
        print(f"Base directory {base_dir} not found.")
        return
    
    successful = 0
    failed = 0
    
    # Process all year directories
    for year_dir in sorted(base_dir.iterdir()):
        if not year_dir.is_dir() or not year_dir.name.startswith("state_"):
            continue
            
        print(f"\n=== Processing {year_dir.name} ===")
        
        # Process all subject directories in this year
        for subject_dir in sorted(year_dir.iterdir()):
            if not subject_dir.is_dir():
                continue
                
            print(f"\nConverting {subject_dir.name}...")
            json_data = convert_test_to_json(subject_dir)
            
            if json_data:
                # Save JSON file
                json_file = subject_dir / "questions.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                print(f"✓ Created {json_file} with {json_data['test_info']['total_questions']} questions")
                successful += 1
            else:
                print(f"✗ Failed to convert {subject_dir}")
                failed += 1
    
    print(f"\n=== Conversion Summary ===")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {successful + failed}")

if __name__ == "__main__":
    main()
