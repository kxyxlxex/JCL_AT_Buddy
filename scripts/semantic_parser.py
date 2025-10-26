#!/usr/bin/env python3
"""
Semantic parser for JCL test files
Uses natural language understanding to parse test content
"""

import re
import json
from pathlib import Path


def parse_answer_key(test_file_path):
    """Parse the answer key file and return a dictionary of question_number -> answer"""
    # Try different possible key file names
    possible_keys = [
        test_file_path.parent / f"{test_file_path.stem.replace('_test', '')}_key.txt",
        test_file_path.parent / f"{test_file_path.stem}_key.txt",
    ]
    
    for answer_key_path in possible_keys:
        if answer_key_path.exists():
            with open(answer_key_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            answers = {}
            pattern = r'(\d+)\.\s*([A-D])'
            matches = re.findall(pattern, content, re.IGNORECASE)
            
            for question_num, answer in matches:
                answers[int(question_num)] = answer.upper()
            
            return answers
    
    return {}


def semantic_parse_test(text_content, answer_key):
    """
    Parse test content using semantic understanding
    Identifies questions, options, and instructions by understanding structure
    """
    lines = text_content.strip().split('\n')
    questions = []
    current_instruction = "Answer the following question."
    
    # Auto-detect format based on option letters in content
    # Pre-2018: lowercase a. b. c. d. (often all on one line)
    # Post-2018: uppercase A. B. C. D. (one per line)
    is_pre_2018 = bool(re.search(r'\n[a-d]\.\s+\w+\s+[b-d]\.', text_content, re.IGNORECASE))
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and obvious headers
        if not line:
            i += 1
            continue
        
        # Check if this is a general instruction (not a question)
        # Instructions are usually longer sentences without question numbers
        if not re.match(r'^\d+\.', line):
            # Check if this looks like an instruction
            instruction_indicators = [
                'choose', 'identify', 'select', 'complete', 'find',
                'items', 'questions', 'for questions', 'match', 'derived',
                'answer', 'give', 'provide', 'determine'
            ]
            line_lower = line.lower()
            
            # More strict: instruction should start with verb or "Items"
            is_instruction = False
            for indicator in instruction_indicators:
                if line_lower.startswith(indicator) or line_lower.startswith('items'):
                    is_instruction = True
                    break
            
            if is_instruction:
                # This is likely an instruction
                instruction_parts = [line]
                j = i + 1
                # Continue reading until we hit a question number or empty line
                while j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line or re.match(r'^\d+\.', next_line):
                        break
                    if is_header_or_metadata(next_line):
                        j += 1
                        break
                    # If next line also looks like an instruction start, stop here
                    next_lower = next_line.lower()
                    if any(next_lower.startswith(ind) for ind in instruction_indicators):
                        break
                    instruction_parts.append(next_line)
                    j += 1
                
                if instruction_parts:
                    new_instruction = ' '.join(instruction_parts).strip()
                    # Update only if it's a substantial instruction
                    if len(new_instruction) > 10:
                        current_instruction = new_instruction
                i = j
                continue
        
        # Check if this is a question (starts with number.)
        question_match = re.match(r'^(\d+)\.\s*(.*)', line)  # Allow empty question text
        if question_match:
            question_num = int(question_match.group(1))
            question_text = question_match.group(2)
            
            # Read the full question (may span multiple lines)
            j = i + 1
            question_lines = [question_text]
            
            # Continue reading until we hit an option line (A./a., B./b., etc.)
            while j < len(lines):
                next_line = lines[j].strip()
                if not next_line:
                    j += 1
                    continue
                
                # Check if this is an option line (case-insensitive)
                if re.match(r'^[A-Da-d]\.', next_line):
                    break
                
                # Check if this is the next question
                if re.match(r'^\d+\.', next_line):
                    break
                
                # Skip headers
                if is_header_or_metadata(next_line):
                    j += 1
                    continue
                
                question_lines.append(next_line)
                j += 1
            
            question_body = ' '.join(question_lines).strip()
            
            # Now collect the options
            options = {}
            
            # Pre-2018 format: options may be on same line
            if is_pre_2018:
                # Try to collect all options (might be on one or more lines)
                option_lines = []
                while j < len(lines) and len(options) < 4:
                    next_line = lines[j].strip()
                    
                    if not next_line:
                        j += 1
                        continue
                    
                    # Stop if we hit next question
                    if re.match(r'^\d+\.', next_line):
                        break
                    
                    # Stop if we hit header/instruction
                    if is_header_or_metadata(next_line):
                        break
                    
                    # Check for instruction
                    instruction_indicators = [
                        'choose', 'identify', 'select', 'complete', 'find',
                        'items', 'questions', 'for questions', 'match', 'derived',
                        'answer', 'give', 'provide', 'determine'
                    ]
                    next_lower = next_line.lower()
                    if any(next_lower.startswith(ind) for ind in instruction_indicators):
                        break
                    
                    # If line has options, collect it
                    if re.match(r'^[a-d]\.', next_line, re.IGNORECASE):
                        option_lines.append(next_line)
                        j += 1
                    else:
                        break
                
                # Parse all options from collected lines
                combined_options = ' '.join(option_lines)
                option_pattern = r'([a-d])\.\s+(.+?)(?=\s+[a-d]\.\s+|$)'
                matches = re.findall(option_pattern, combined_options, re.IGNORECASE)
                
                for option_letter, option_text in matches:
                    options[option_letter.upper()] = option_text.strip()
            
            else:
                # Post-2018 format: one option per line
                while j < len(lines) and len(options) < 4:
                    next_line = lines[j].strip()
                    
                    if not next_line:
                        j += 1
                        continue
                    
                    # Check if this is an instruction line (might appear before next question)
                    instruction_indicators = [
                        'choose', 'identify', 'select', 'complete', 'find',
                        'items', 'questions', 'for questions', 'match', 'derived',
                        'answer', 'give', 'provide', 'determine'
                    ]
                    next_lower = next_line.lower()
                    is_new_instruction = any(next_lower.startswith(ind) for ind in instruction_indicators)
                    
                    if is_new_instruction and len(options) == 4:
                        # We've finished collecting options and hit a new instruction
                        # Update instruction for next questions
                        inst_lines = [next_line]
                        k = j + 1
                        while k < len(lines):
                            inst_next = lines[k].strip()
                            if not inst_next or re.match(r'^\d+\.', inst_next):
                                break
                            if is_header_or_metadata(inst_next):
                                k += 1
                                break
                            inst_lines.append(inst_next)
                            k += 1
                        new_instruction = ' '.join(inst_lines).strip()
                        if len(new_instruction) > 10:
                            current_instruction = new_instruction
                        j = k
                        break
                    
                    # Check for option line (A., B., C., D.)
                    option_match = re.match(r'^([A-D])\.\s+(.+)', next_line)
                    
                    if option_match:
                        option_letter = option_match.group(1)
                        option_text = option_match.group(2)
                        
                        # Read continuation lines for this option if any
                        k = j + 1
                        option_lines = [option_text]
                        while k < len(lines):
                            cont_line = lines[k].strip()
                            if not cont_line:
                                k += 1
                                continue
                            
                            # Check if next line is an instruction
                            cont_lower = cont_line.lower()
                            if any(cont_lower.startswith(ind) for ind in instruction_indicators):
                                # This is likely a new instruction, stop here
                                break
                            
                            # Stop if we hit another option or question
                            if re.match(r'^[A-D]\.', cont_line) or re.match(r'^\d+\.', cont_line):
                                break
                            
                            # Stop if we hit a header
                            if is_header_or_metadata(cont_line):
                                break
                            
                            option_lines.append(cont_line)
                            k += 1
                        
                        options[option_letter] = ' '.join(option_lines).strip()
                        j = k
                    else:
                        # Not an option line, might be end of options or an instruction
                        if is_new_instruction:
                            # Save this instruction for next questions
                            inst_lines = [next_line]
                            k = j + 1
                            while k < len(lines):
                                inst_next = lines[k].strip()
                                if not inst_next or re.match(r'^\d+\.', inst_next):
                                    break
                                if is_header_or_metadata(inst_next):
                                    k += 1
                                    break
                                inst_lines.append(inst_next)
                                k += 1
                            new_instruction = ' '.join(inst_lines).strip()
                            if len(new_instruction) > 10:
                                current_instruction = new_instruction
                            j = k
                        break
            
            # Validate and add question
            # Question body can be empty if the instruction explains what to do
            if len(options) == 4:
                # Check all options are non-empty
                if all(options.get(key, '').strip() for key in ['A', 'B', 'C', 'D']):
                    answer = answer_key.get(question_num, "UNKNOWN")
                    
                    # If question body is empty, use the instruction as context
                    final_question_body = question_body if question_body else f"Question {question_num}"
                    
                    questions.append({
                        "question_index": question_num,
                        "question_body": final_question_body,
                        "question_options": options,
                        "question_key": answer,
                        "question_instruction": current_instruction
                    })
            
            i = j
        else:
            i += 1
    
    return questions


def is_header_or_metadata(line):
    """Check if a line is a header or metadata that should be skipped"""
    line_lower = line.lower()
    
    # Known header patterns
    headers = [
        'fjcl state forum',
        'derivatives',
        'mythology',
        'vocabulary',
        'history',
        'classical art',
        'classical geography',
        'mottoes',
        'abbreviations',
        'quotations',
        '- states',
        'state latin forum'
    ]
    
    for header in headers:
        if header in line_lower:
            return True
    
    # Check for year patterns
    if re.match(r'^\d{4}\s+FJCL', line):
        return True
    
    # Check for section markers
    if re.match(r'^[IVX]+\.\s*$', line):
        return True
    
    return False


def process_test_file(test_file_path):
    """Process a single test file using semantic parsing"""
    print(f"\nProcessing: {test_file_path}")
    
    # Read the test file
    with open(test_file_path, 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    # Parse answer key
    answer_key = parse_answer_key(test_file_path)
    print(f"  Found {len(answer_key)} answers in key")
    
    # Use semantic parsing
    questions = semantic_parse_test(text_content, answer_key)
    
    print(f"  Parsed {len(questions)} questions")
    
    # Validate
    missing_keys = [q["question_index"] for q in questions if q["question_key"] == "UNKNOWN"]
    if missing_keys:
        print(f"  Warning: Questions without answer keys: {missing_keys}")
    
    return questions


def main():
    """Main function to process all test files (excluding Classical Art and Classical Geography)"""
    base_dir = Path("/Users/kylexu/JCL_AT_Buddy/data/raw-data")
    
    if not base_dir.exists():
        print(f"Error: Directory {base_dir} not found")
        return
    
    # Find all test files across all years
    all_test_files = list(base_dir.rglob("*_test.txt"))
    
    # Filter out Classical_Art and Classical_Geography
    excluded_subjects = ['Classical_Art', 'Classical_Geography']
    test_files = [
        f for f in all_test_files 
        if not any(excluded in str(f) for excluded in excluded_subjects)
    ]
    
    print(f"Found {len(test_files)} test files to process")
    print(f"(Excluded Classical_Art and Classical_Geography: {len(all_test_files) - len(test_files)} files)")
    print("\n" + "=" * 70)
    
    success_count = 0
    error_count = 0
    total_questions = 0
    
    # Group by year for better output
    by_year = {}
    for test_file in test_files:
        year_match = re.search(r'state_(\d{4})', str(test_file))
        if year_match:
            year = year_match.group(1)
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(test_file)
    
    for year in sorted(by_year.keys()):
        print(f"\n{'='*70}")
        print(f"YEAR {year} ({len(by_year[year])} files)")
        print('='*70)
        
        for test_file in sorted(by_year[year]):
            try:
                questions = process_test_file(test_file)
                
                if questions:
                    # Save as JSON
                    output_file = test_file.parent / "semantic_parsed.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(questions, f, indent=2, ensure_ascii=False)
                    
                    print(f"  → Saved to {output_file.name}")
                    success_count += 1
                    total_questions += len(questions)
                else:
                    print(f"  → No questions parsed")
                    error_count += 1
            
            except Exception as e:
                print(f"  → Error: {e}")
                error_count += 1
                import traceback
                traceback.print_exc()
    
    print("\n" + "=" * 70)
    print(f"PROCESSING COMPLETE!")
    print("=" * 70)
    print(f"  Success: {success_count}/{len(test_files)} files")
    print(f"  Errors: {error_count}")
    print(f"  Total questions: {total_questions}")
    print("=" * 70)


if __name__ == "__main__":
    main()

