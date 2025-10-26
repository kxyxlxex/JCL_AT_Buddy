#!/usr/bin/env python3
"""
Simple parser V2 for JCL test files
Creates JSON files with fields: question_index, question_body, question_options, question_key, question_instruction
Ensures all fields are not empty
"""

import re
import json
from pathlib import Path


def parse_answer_key(test_file_path):
    """Parse the answer key file and return a dictionary of question_number -> answer"""
    answer_key_path = test_file_path.parent / f"{test_file_path.stem.replace('_test', '')}_key.txt"
    
    if not answer_key_path.exists():
        print(f"  Warning: No answer key found at {answer_key_path}")
        return {}
    
    with open(answer_key_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for answer patterns like "1. A 2. B 3. C" or "1. A\n2. B\n3. C"
    answers = {}
    
    # Try to find answers in the format "number. letter"
    pattern = r'(\d+)\.\s*([A-D])'
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    for question_num, answer in matches:
        answers[int(question_num)] = answer.upper()
    
    return answers


def is_section_header(line):
    """Check if a line is a section header that should be ignored"""
    if not line or not line.strip():
        return True
    
    line = line.strip()
    
    # Patterns that indicate section headers to skip
    skip_patterns = [
        r'^FJCL\s+State\s+(Latin\s+)?Forum',
        r'^STATE\s+LATIN\s+FORUM',
        r'^\d{4}\s+FJCL',
        r'^Mythology\s*$',
        r'^Derivatives\s*(I|II)?\s*$',
        r'^Vocabulary\s*(I|II)?\s*$',
        r'^History\s+of\s+the\s+(Empire|Monarchy)',
        r'^Classical\s+(Art|Geography)\s*$',
        r'^Mottoes,?\s+Abbreviations',
        r'^Phrases',
        r'^Quotations',
        r'- States \d{4} -',
    ]
    
    for pattern in skip_patterns:
        if re.match(pattern, line, re.IGNORECASE):
            return True
    
    return False


def is_instruction_line(line):
    """Check if a line is an instruction (e.g., 'Items 41–45: Identify the mother...')"""
    if not line or not line.strip():
        return False
    
    line = line.strip()
    
    # Patterns that indicate instructions
    instruction_patterns = [
        r'^Items?\s+\d+[–-]\d+:',
        r'^Questions?\s+\d+[–-]\d+:',
        r'^For\s+questions?\s+\d+[–-]\d+',
        r'^Part\s+[IVX]+[:\.\)]',
    ]
    
    for pattern in instruction_patterns:
        if re.match(pattern, line, re.IGNORECASE):
            return True
    
    return False


def parse_test_file(test_file_path):
    """
    Parse a single test file and return questions with specified fields:
    - question_index: the question number
    - question_body: the question text
    - question_options: dictionary with keys A, B, C, D
    - question_key: the correct answer (A, B, C, or D)
    - question_instruction: the instruction for the question section
    """
    
    # Read the file
    with open(test_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Determine if this is pre-2018 or post-2018 format
    year_match = re.search(r'state_(\d{4})', str(test_file_path))
    year = int(year_match.group(1)) if year_match else 2018
    is_pre_2018 = year <= 2017
    
    print(f"\nProcessing {test_file_path}")
    print(f"  Year: {year}, Format: {'pre-2018' if is_pre_2018 else 'post-2018'}")
    
    # Parse answer key
    answer_key = parse_answer_key(test_file_path)
    print(f"  Found {len(answer_key)} answers in key")
    
    questions = []
    current_instruction = "Answer the following question."  # Default instruction
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and section headers
        if not line or is_section_header(line):
            i += 1
            continue
        
        # Check if this is an instruction line
        if is_instruction_line(line):
            # Capture the entire instruction (may span multiple lines)
            instruction_lines = [line]
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                # Stop if we hit a question number or empty line
                if re.match(r'^\d+\.', next_line) or not next_line:
                    break
                instruction_lines.append(next_line)
                j += 1
            current_instruction = ' '.join(instruction_lines)
            i = j
            continue
        
        # Check if this is a question (starts with number.)
        question_match = re.match(r'^(\d+)\.\s+(.+)', line)
        if question_match:
            question_num = int(question_match.group(1))
            question_text_parts = [question_match.group(2)]
            
            # Read subsequent lines until we hit an option line
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if not next_line:
                    j += 1
                    continue
                
                # Check if this is an option line (for either format)
                # Pre-2018: all options on one line like "a. X b. Y c. Z d. W"
                # Post-2018: one option per line like "A. X"
                if re.match(r'^[a-dA-D]\.', next_line):
                    break
                
                # Check if this is the next question
                if re.match(r'^\d+\.', next_line):
                    break
                
                question_text_parts.append(next_line)
                j += 1
            
            question_body = ' '.join(question_text_parts).strip()
            
            # Now parse the options
            options = {}
            
            if is_pre_2018:
                # Pre-2018 format: options may be on one line or split across multiple lines
                # Pattern: a. option_text b. option_text c. option_text d. option_text
                # Collect all option lines until we have all 4 options or hit a new question
                options_lines = []
                while j < len(lines) and len(options) < 4:
                    next_line = lines[j].strip()
                    
                    # Skip empty lines
                    if not next_line:
                        j += 1
                        continue
                    
                    # Stop if we hit a new question number
                    if re.match(r'^\d+\.', next_line):
                        break
                    
                    # Stop if we hit a section header or instruction
                    if is_section_header(next_line) or is_instruction_line(next_line):
                        break
                    
                    # Check if this line has options (starts with a letter followed by period)
                    if re.match(r'^[a-d]\.', next_line, re.IGNORECASE):
                        options_lines.append(next_line)
                        j += 1
                    else:
                        break
                
                # Combine all options lines and parse them
                combined_options = ' '.join(options_lines)
                option_pattern = r'([a-d])\.\s+(.+?)(?=\s+[a-d]\.\s+|$)'
                matches = re.findall(option_pattern, combined_options, re.IGNORECASE)
                
                for option_letter, option_text in matches:
                    options[option_letter.upper()] = option_text.strip()
            else:
                # Post-2018 format: one option per line
                option_keys = ['A', 'B', 'C', 'D']
                option_idx = 0
                
                while j < len(lines) and option_idx < 4:
                    next_line = lines[j].strip()
                    
                    if not next_line:
                        j += 1
                        continue
                    
                    # Check for option line
                    option_match = re.match(r'^([A-D])\.\s+(.+)', next_line)
                    
                    if option_match:
                        option_letter = option_match.group(1).upper()
                        option_text_parts = [option_match.group(2)]
                        
                        # Read subsequent lines for this option
                        k = j + 1
                        while k < len(lines):
                            opt_next_line = lines[k].strip()
                            if not opt_next_line:
                                k += 1
                                continue
                            
                            # Stop if we hit the next option, next question, or instruction
                            if re.match(r'^[A-D]\.', opt_next_line):
                                break
                            
                            if re.match(r'^\d+\.', opt_next_line):
                                break
                            
                            if is_instruction_line(opt_next_line) or is_section_header(opt_next_line):
                                break
                            
                            option_text_parts.append(opt_next_line)
                            k += 1
                        
                        options[option_letter] = ' '.join(option_text_parts).strip()
                        option_idx += 1
                        j = k
                    else:
                        j += 1
            
            # Only add question if all required fields are present and non-empty
            if question_body and len(options) == 4:
                # Check if all options are non-empty
                option_keys = ['A', 'B', 'C', 'D']
                all_options_valid = all(options.get(key, '').strip() for key in option_keys)
                
                # Get the answer key (may be None if not in answer key)
                answer = answer_key.get(question_num)
                
                if all_options_valid:
                    question_data = {
                        "question_index": question_num,
                        "question_body": question_body,
                        "question_options": options,
                        "question_key": answer if answer else "UNKNOWN",
                        "question_instruction": current_instruction
                    }
                    questions.append(question_data)
                    print(f"  ✓ Question {question_num} parsed successfully")
                else:
                    print(f"  ✗ Question {question_num} skipped: Empty option(s)")
            else:
                print(f"  ✗ Question {question_num} skipped: Incomplete data (body={bool(question_body)}, options={len(options)})")
            
            i = j
        else:
            i += 1
    
    print(f"  Total questions parsed: {len(questions)}")
    
    # Check for any questions without answer keys
    missing_keys = [q["question_index"] for q in questions if q["question_key"] == "UNKNOWN"]
    if missing_keys:
        print(f"  Warning: Questions without answer keys: {missing_keys}")
    
    return questions


def main():
    """Main function to process all test files"""
    base_dir = Path("/Users/kylexu/JCL_AT_Buddy/data/raw-data")
    
    if not base_dir.exists():
        print(f"Error: Directory {base_dir} not found")
        return
    
    # Find all test files
    test_files = list(base_dir.rglob("*_test.txt"))
    print(f"Found {len(test_files)} test files to process\n")
    
    success_count = 0
    error_count = 0
    
    # Process all test files
    for test_file in sorted(test_files):
        try:
            questions = parse_test_file(test_file)
            
            if questions:
                # Save as JSON in the same directory as the test file
                output_file = test_file.parent / "parsed_questions.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(questions, f, indent=2, ensure_ascii=False)
                
                print(f"  → Saved to {output_file}")
                success_count += 1
            else:
                print(f"  → No questions parsed")
                error_count += 1
            
        except Exception as e:
            print(f"  → Error: {e}")
            import traceback
            traceback.print_exc()
            error_count += 1
    
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

