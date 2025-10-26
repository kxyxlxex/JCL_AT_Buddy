#!/usr/bin/env python3
"""
Fixed parser that properly handles pre-2018 vs post-2018 format differences.
"""

import os
import json
import re
from pathlib import Path

def parse_test_file_fixed(test_file_path):
    """Parse a test file with proper handling of pre-2018 vs post-2018 formats."""
    with open(test_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines for processing
    lines = content.split('\n')
    
    questions = []
    current_question = None
    current_section = None
    section_context = None
    current_instruction = None
    question_buffer = []
    
    # Determine if this is pre-2018 or post-2018 format
    year_match = re.search(r'state_(\d{4})', str(test_file_path))
    year = int(year_match.group(1)) if year_match else 2018
    is_pre_2018 = year <= 2017  # 2017 and earlier use pre-2018 format with sections
    
    print(f"  Parsing {test_file_path.name} ({'pre-2018' if is_pre_2018 else 'post-2018'} format)")
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Skip header lines like "2010 FJCL State Latin Forum – Derivatives I –"
        if re.match(r'^\d{4}\s+FJCL\s+State\s+Latin\s+Forum', line):
            continue
        
        # Handle pre-2018 format with sections
        if is_pre_2018:
            # Check for section headers (I:, II:, III:, etc.)
            section_match = re.match(r'^([IVX]+):\s*(.+)$', line)
            if section_match:
                current_section = line
                section_context = line
                continue
            
            # Check for "I. Identify the ..." format (Roman numeral followed by period)
            roman_period_match = re.match(r'^([IVX]+)\.\s*(.+)$', line)
            if roman_period_match:
                # Strip the "I." prefix and keep only the instruction
                instruction_text = roman_period_match.group(2).strip()
                current_section = instruction_text
                section_context = instruction_text
                continue
            
            # Check for "Part x)" format (useful section headers with instructions)
            part_match = re.match(r'^Part\s+(\d+)\)\s*(.+)$', line)
            if part_match:
                # Only treat as section if it contains instruction keywords
                if any(word in line.lower() for word in ['choose', 'match', 'identify', 'give', 'complete', 'select', 'answer', 'refer', 'use', 'items', 'for questions']):
                    # Strip the "Part x)" prefix and keep only the instruction
                    instruction_text = part_match.group(2).strip()
                    current_section = instruction_text
                    section_context = instruction_text
                continue
            
            # Skip "Part x – Description" format (2017 style) - these are just dividers, not real sections
            part_dash_match = re.match(r'^Part\s+(\d+)\s*–\s*(.+)$', line)
            if part_dash_match:
                # Don't treat these as sections, just skip them entirely
                continue
            
            # Skip "Part x- Description" format (hyphen style) - these are also just dividers
            part_hyphen_match = re.match(r'^Part\s+(\d+)-\s*(.+)$', line)
            if part_hyphen_match:
                # Don't treat these as sections, just skip them entirely
                continue
            
            # Skip "Part II: Mottoes" format (Roman numeral with colon) - these are just dividers
            part_roman_colon_match = re.match(r'^Part\s+([IVX]+):\s*(.+)$', line)
            if part_roman_colon_match:
                # Don't treat these as sections, just skip them entirely
                continue
            
            # Check for instruction patterns (excluding N.B. instructions and section dividers)
            # Instructions are lines that tell students how to solve the next few problems
            if (not re.match(r'^N\.B\.', line) and  # Not N.B. instructions
                not re.match(r'^\d+\.', line) and  # Not question numbers
                not re.match(r'^([a-d])\.\s*(.+)$', line) and  # Not answer options
                not re.match(r'^\d{4}\s+FJCL\s+State\s+(Latin\s+)?Forum', line) and  # Not headers
                not re.match(r'^\d{4}\s+FJCL\s+State\s+Forum.*-$', line) and  # Not headers ending with dash
                not re.match(r'^\d{4}\s+FJCL\s+State\s+Forum.*\s+-\s*$', line) and  # Not headers ending with space-dash-space
                not re.match(r'^Part\s+\d+\s*[-–]\s*(.+)$', line) and  # Not "Part x - Description" dividers
                not re.match(r'^Part\s+(\d+)\)\s*(.+)$', line) and  # Not Part x) lines (handled separately)
                line.endswith(('.', ':')) and  # Ends with period or colon
                len(line.split()) > 2 and  # Has multiple words
                any(word in line.lower() for word in ['choose', 'match', 'identify', 'give', 'complete', 'select', 'answer', 'refer', 'use', 'items', 'for questions'])):  # Contains instruction keywords
                
                # This is an instruction line
                current_instruction = line
                continue
            
            # Check for question numbers
            question_match = re.match(r'^(\d+)\.\s*(.+)$', line)
            if question_match:
                # Save previous question if exists
                if current_question and len(current_question["options"]) >= 4:
                    questions.append(current_question)
                
                # Start new question
                question_num = int(question_match.group(1))
                question_text = question_match.group(2).strip()
                
                # Build complete question text with section context
                full_question = question_text
                if section_context:
                    full_question = f"{section_context} {question_text}".strip()
                
                current_question = {
                    "question_number": question_num,
                    "question": full_question,
                    "options": {},
                    "type": "multiple_choice",
                    "section": current_section,
                    "section_context": section_context,
                    "instruction": current_instruction
                }
                continue
            
            # Extract instruction from Part x) lines and strip extraneous prefixes
            part_match = re.match(r'^Part\s+(\d+)\)\s*(.+)$', line)
            if part_match:
                instruction_text = part_match.group(2).strip()
                
                # Remove question range patterns like "For 46-50" or "For questions 1-10"
                instruction_text = re.sub(r'^For\s+\d+-\d+\s+', '', instruction_text)
                instruction_text = re.sub(r'^For\s+questions\s+\d+-\d+\s+', '', instruction_text)
                instruction_text = re.sub(r'^For\s+questions\s+\d+-\d+\s+please\s+', '', instruction_text)
                
                # Clean up any remaining artifacts
                instruction_text = instruction_text.strip()
                
                current_instruction = instruction_text
                continue
            
            # If we have a current question and this line doesn't start with an option, 
            # it might be a continuation of the question statement
            if (current_question and 
                not re.match(r'^([a-d])\.\s*(.+)$', line) and  # Not an option
                not re.match(r'^\d+\.', line) and  # Not a new question number
                not re.match(r'^\d{4}\s+FJCL\s+State\s+Latin\s+Forum', line) and  # Not a header
                not re.match(r'^Part\s+(\d+)\s*[-–]\s*(.+)$', line) and  # Not a section divider
                not re.match(r'^Part\s+(\d+)-\s*(.+)$', line) and  # Not a section divider (hyphen)
                not re.match(r'^Part\s+([IVX]+):\s*(.+)$', line) and  # Not a Part II: Mottoes divider
                not re.match(r'^([IVX]+)\.\s*(.+)$', line) and  # Not a Roman numeral section
                not re.match(r'^Part\s+(\d+)\)\s*(.+)$', line) and  # Not a Part x) section
                not re.match(r'^N\.B\.', line) and  # Not an N.B. instruction
                line.strip() and  # Not empty
                not any(word in line.lower() for word in ['choose', 'match', 'identify', 'give', 'complete', 'select', 'answer', 'refer', 'use', 'items', 'for questions'])):  # Not an instruction
                # This is a continuation of the question statement
                current_question["question"] += " " + line.strip()
                continue
            
            # Check for options (a., b., c., d.) - pre-2018 uses lowercase
            # Look for pattern: lowercase letter followed by period with spaces on both sides
            option_match = re.match(r'^([a-d])\.\s*(.+)$', line)
            if option_match and current_question:
                option_letter = option_match.group(1).upper()
                option_text = option_match.group(2).strip()
                
                # Check if this line contains multiple options (like "his severe punishment b. his ability c. his affair d. his musical")
                if re.search(r'\s+[b-d]\.\s+', option_text):
                    # Split the line into individual options using the pattern: space + lowercase letter + period + space
                    parts = re.split(r'\s+([b-d])\.\s+', option_text)
                    if len(parts) >= 3:
                        # First option (use the actual letter from the match)
                        first_option = parts[0].strip()
                        current_question["options"][option_letter] = first_option
                        
                        # Process remaining options
                        for i in range(1, len(parts), 2):
                            if i + 1 < len(parts):
                                letter = parts[i].upper()
                                text = parts[i + 1].strip()
                                current_question["options"][letter] = text
                else:
                    # Single option on the line
                    current_question["options"][option_letter] = option_text
                continue
            
        
        # Handle post-2018 format (no sections)
        else:
            # Check for instruction patterns (excluding N.B. instructions and section dividers)
            # Instructions are lines that tell students how to solve the next few problems
            if (not re.match(r'^N\.B\.', line) and  # Not N.B. instructions
                not re.match(r'^\d+\.', line) and  # Not question numbers
                not re.match(r'^([A-D])\.\s*(.+)$', line) and  # Not answer options
                not re.match(r'^\d{4}\s+FJCL\s+State\s+(Latin\s+)?Forum', line) and  # Not headers
                not re.match(r'^\d{4}\s+FJCL\s+State\s+Forum.*-$', line) and  # Not headers ending with dash
                not re.match(r'^\d{4}\s+FJCL\s+State\s+Forum.*\s+-\s*$', line) and  # Not headers ending with space-dash-space
                not re.match(r'^Part\s+\d+\s*[-–]\s*(.+)$', line) and  # Not "Part x - Description" dividers
                line.endswith(('.', ':')) and  # Ends with period or colon
                len(line.split()) > 2 and  # Has multiple words
                any(word in line.lower() for word in ['choose', 'match', 'identify', 'give', 'complete', 'select', 'answer', 'refer', 'use', 'items', 'for questions'])):  # Contains instruction keywords
                
                # This is an instruction line
                current_instruction = line
                continue
            
            # Check for question numbers
            question_match = re.match(r'^(\d+)\.\s*(.+)$', line)
            if question_match:
                # Save previous question if exists
                if current_question and len(current_question["options"]) > 0:
                    questions.append(current_question)
                
                # Start new question
                question_num = int(question_match.group(1))
                question_text = question_match.group(2).strip()
                
                current_question = {
                    "question_number": question_num,
                    "question": question_text,
                    "options": {},
                    "type": "multiple_choice",
                    "section": None,
                    "section_context": None,
                    "instruction": current_instruction
                }
                continue
            
            # Extract instruction from Part x) lines and strip extraneous prefixes
            part_match = re.match(r'^Part\s+(\d+)\)\s*(.+)$', line)
            if part_match:
                instruction_text = part_match.group(2).strip()
                
                # Remove question range patterns like "For 46-50" or "For questions 1-10"
                instruction_text = re.sub(r'^For\s+\d+-\d+\s+', '', instruction_text)
                instruction_text = re.sub(r'^For\s+questions\s+\d+-\d+\s+', '', instruction_text)
                instruction_text = re.sub(r'^For\s+questions\s+\d+-\d+\s+please\s+', '', instruction_text)
                
                # Clean up any remaining artifacts
                instruction_text = instruction_text.strip()
                
                current_instruction = instruction_text
                continue
            
            # If we have a current question and this line doesn't start with an option, 
            # it might be a continuation of the question statement
            if (current_question and 
                not re.match(r'^([A-D])\.\s*(.+)$', line) and  # Not an option
                not re.match(r'^\d+\.', line) and  # Not a new question number
                not re.match(r'^\d{4}\s+FJCL\s+State\s+Latin\s+Forum', line) and  # Not a header
                not re.match(r'^Part\s+(\d+)\s*[-–]\s*(.+)$', line) and  # Not a section divider
                not re.match(r'^Part\s+(\d+)-\s*(.+)$', line) and  # Not a section divider (hyphen)
                not re.match(r'^Part\s+([IVX]+):\s*(.+)$', line) and  # Not a Part II: Mottoes divider
                not re.match(r'^([IVX]+)\.\s*(.+)$', line) and  # Not a Roman numeral section
                not re.match(r'^Part\s+(\d+)\)\s*(.+)$', line) and  # Not a Part x) section
                not re.match(r'^N\.B\.', line) and  # Not an N.B. instruction
                line.strip() and  # Not empty
                not any(word in line.lower() for word in ['choose', 'match', 'identify', 'give', 'complete', 'select', 'answer', 'refer', 'use', 'items', 'for questions'])):  # Not an instruction
                # This is a continuation of the question statement
                current_question["question"] += " " + line.strip()
                continue
            
            # Check for options (A., B., C., D.) - post-2018 uses uppercase
            option_match = re.match(r'^([A-D])\.\s*(.+)$', line)
            if option_match and current_question:
                option_letter = option_match.group(1)
                option_text = option_match.group(2).strip()
                
                # Check if this line contains multiple options (like "Helle B. Danae C. Io D. Daphne")
                if re.search(r'\s+[B-D]\.\s+', option_text):
                    # Split the line into individual options
                    parts = re.split(r'\s+([B-D])\.\s+', option_text)
                    if len(parts) >= 3:
                        # First option (A.)
                        first_option = parts[0].strip()
                        current_question["options"]["A"] = first_option
                        
                        # Process remaining options
                        for i in range(1, len(parts), 2):
                            if i + 1 < len(parts):
                                letter = parts[i]
                                text = parts[i + 1].strip()
                                current_question["options"][letter] = text
                else:
                    # Single option on the line
                    current_question["options"][option_letter] = option_text
                continue
    
    # Don't forget the last question
    if current_question and len(current_question["options"]) > 0:
        questions.append(current_question)
    
    return questions

def parse_answer_key(key_file_path):
    """Parse the answer key file."""
    with open(key_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract answers from the key
    # Pattern: number. answer (handles both single line and multi-line formats)
    answer_pattern = r'(\d+)\.\s+([A-D])'
    matches = re.findall(answer_pattern, content)
    
    answers = {}
    for match in matches:
        question_num = int(match[0])
        answer = match[1]
        answers[question_num] = answer
    
    return answers

def convert_test_to_json_fixed(test_dir):
    """Convert a test directory to JSON with fixed parsing."""
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
    questions = parse_test_file_fixed(test_file)
    
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

def process_all_tests_fixed():
    """Process all test directories with fixed parsing."""
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
            result = convert_test_to_json_fixed(subject_dir)
            
            if result:
                # Save JSON file
                json_file = subject_dir / "questions.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"    Saved {len(result['questions'])} questions to {json_file.name}")
                if result['test_info']['sections']:
                    print(f"    Sections found: {result['test_info']['sections']}")

if __name__ == "__main__":
    print("Running fixed parser on all test files...")
    process_all_tests_fixed()
    print("Done!")
