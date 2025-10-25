#!/usr/bin/env python3
"""
Improved parser that handles sections, multi-line questions, and context instructions.
"""

import os
import json
import re
from pathlib import Path

def parse_test_file_improved(test_file_path):
    """Parse a test file with improved handling of sections and multi-line questions."""
    with open(test_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines for processing
    lines = content.split('\n')
    
    questions = []
    current_question = None
    current_section = None
    section_context = None
    question_buffer = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Check for section headers (PHRASES, MOTTOES, ABBREVIATIONS, etc.)
        # Only consider lines that are clearly section headers
        if (line.isupper() and len(line) > 3 and 
            not line.startswith('FJCL') and 
            not line.startswith('State') and
            not line.startswith('Choose') and
            not line.startswith('Identify') and
            not line.startswith('Complete') and
            not re.match(r'^\d+\.', line) and
            not re.match(r'^[A-D]\.', line) and
            line in ['PHRASES', 'MOTTOES', 'ABBREVIATIONS', 'QUOTATIONS', 'DERIVATIVES', 'VOCABULARY', 'HISTORY', 'MYTHOLOGY', 'CLASSICAL ART', 'CLASSICAL GEOGRAPHY']):
            current_section = line
            section_context = None
            continue
        
        # Check for context instructions that apply to sections
        if (line.startswith("Choose the") or 
            line.startswith("Identify the") or 
            line.startswith("Complete the") or
            line.startswith("For questions") or
            line.startswith("N.b.") or
            (line.startswith("Items") and ":" in line)):
            section_context = line
            continue
        
        # Check for question numbers
        question_match = re.match(r'^(\d+)\.\s*(.*)$', line)
        if question_match:
            # Save previous question if exists
            if current_question and len(current_question["options"]) > 0:
                questions.append(current_question)
            
            # Start new question
            question_num = int(question_match.group(1))
            question_text = question_match.group(2).strip()
            
            # Build complete question text
            full_question = question_text
            if section_context:
                full_question = f"{section_context} {question_text}".strip()
            
            current_question = {
                "question_number": question_num,
                "question": full_question,
                "options": {},
                "type": "multiple_choice",
                "section": current_section,
                "section_context": section_context
            }
            
            question_buffer = [question_text] if question_text else []
            continue
        
        # Handle continuation of question text (if current line doesn't start with A-D)
        if (current_question and 
            not re.match(r'^[A-D]\.\s+', line) and 
            not re.match(r'^\d+\.', line) and
            line and
            not line.isupper()):
            # This might be a continuation of the question
            if not current_question["options"]:  # No options yet, so this is question text
                current_question["question"] += " " + line
                question_buffer.append(line)
            continue
        
        # Check for options (A., B., C., D.)
        option_match = re.match(r'^([A-D])\.\s+(.+)$', line)
        if option_match and current_question:
            option_letter = option_match.group(1)
            option_text = option_match.group(2).strip()
            current_question["options"][option_letter] = option_text
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
    
    # Don't forget the last question
    if current_question and len(current_question["options"]) > 0:
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

def convert_test_to_json_improved(test_dir):
    """Convert a test directory to JSON with improved parsing."""
    test_dir = Path(test_dir)
    
    # Find test and key files
    test_files = list(test_dir.glob("*_test.txt"))
    key_files = list(test_dir.glob("*_key.txt"))
    
    if not test_files:
        print(f"No test files found in {test_dir}")
        return None
    
    test_file = test_files[0]
    key_file = key_files[0] if key_files else None
    
    print(f"Processing {test_file}")
    
    # Parse test file
    questions = parse_test_file_improved(test_file)
    
    # Parse answer key if available
    answers = {}
    if key_file:
        answers = parse_answer_key(key_file)
        print(f"Found {len(answers)} answers in key file")
    
    # Add correct answers to questions
    for question in questions:
        question_num = question["question_number"]
        if question_num in answers:
            question["correct_answer"] = answers[question_num]
        else:
            question["correct_answer"] = "?"
            print(f"Warning: No answer found for question {question_num}")
    
    # Create test info
    test_info = {
        "name": test_dir.name,
        "year": test_dir.parent.name,
        "subject": test_dir.name,
        "total_questions": len(questions),
        "sections": list(set(q.get("section") for q in questions if q.get("section")))
    }
    
    # Create final JSON structure
    result = {
        "test_info": test_info,
        "questions": questions
    }
    
    return result

def process_all_tests_improved():
    """Process all test directories with improved parsing."""
    base_dir = Path("/Users/kylexu/JCL_AT_Buddy/data/raw-data")
    
    for year_dir in base_dir.iterdir():
        if not year_dir.is_dir():
            continue
        
        print(f"\nProcessing year: {year_dir.name}")
        
        for subject_dir in year_dir.iterdir():
            if not subject_dir.is_dir():
                continue
            
            print(f"  Processing subject: {subject_dir.name}")
            
            # Convert to JSON
            result = convert_test_to_json_improved(subject_dir)
            
            if result:
                # Save JSON file
                json_file = subject_dir / "questions.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"    Saved {len(result['questions'])} questions to {json_file.name}")
                if result['test_info']['sections']:
                    print(f"    Sections found: {result['test_info']['sections']}")

if __name__ == "__main__":
    print("Running improved parser on all test files...")
    process_all_tests_improved()
    print("Done!")
