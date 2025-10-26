#!/usr/bin/env python3
"""
Simple parser for JCL test files - only handles instructions and questions
"""

import re
import json
from pathlib import Path

def is_section_header(text):
    """Check if text is a section header that should be ignored"""
    if not text:
        return False
    
    # Common section header patterns
    section_patterns = [
        'Mythology:', 'Phrases:', 'Mottoes:', 'Abbreviations:', 'Quotations:', 
        'Derivatives:', 'History:', 'Vocabulary:', 'Classical Art:', 'Classical Geography:',
        'Empire:', 'Monarchy:', 'Republic:', 'Vocabulary I:', 'Vocabulary II:',
        'Derivatives I:', 'Derivatives II:', 'History of the Empire:', 
        'History of the Monarchy and Republic:', 'MYTHOLOGY:', 'MOTTOES:', 'PHRASES:',
        'QUOTATIONS:', 'ABBREVIATIONS:', 'Chlorus:', 'Derived:', 'English word(s):',
        'Equivalents:', 'Extra questions:', 'Geography:', 'Image:', 'Miscellaneous:',
        'Word:', 'Phrases, Mottoes, Abbreviations, and Quotations:',
        # Without colons
        'Mythology', 'Phrases', 'Mottoes', 'Abbreviations', 'Quotations',
        'Derivatives', 'History', 'Vocabulary', 'Classical Art', 'Classical Geography',
        'Empire', 'Monarchy', 'Republic', 'Vocabulary I', 'Vocabulary II',
        'Derivatives I', 'Derivatives II', 'History of the Empire',
        'History of the Monarchy and Republic', 'MYTHOLOGY', 'MOTTOES', 'PHRASES',
        'QUOTATIONS', 'ABBREVIATIONS', 'Chlorus', 'Derived', 'English word(s)',
        'Equivalents', 'Extra questions', 'Geography', 'Image', 'Miscellaneous',
        'Word', 'Phrases, Mottoes, Abbreviations, and Quotations',
        # Roman numeral patterns
        'I.', 'II.', 'III.', 'IV.', 'V.', 'VI.', 'VII.', 'VIII.', 'IX.', 'X.',
        'I)', 'II)', 'III)', 'IV)', 'V)', 'VI)', 'VII)', 'VIII)', 'IX)', 'X)',
        # Part patterns
        'Part I)', 'Part II)', 'Part III)', 'Part IV)', 'Part V)',
        'Part 1)', 'Part 2)', 'Part 3)', 'Part 4)', 'Part 5)',
        'Part I.', 'Part II.', 'Part III.', 'Part IV.', 'Part V.',
        'Part 1.', 'Part 2.', 'Part 3.', 'Part 4.', 'Part 5.'
    ]
    
    # Direct match with known patterns
    if text in section_patterns:
        return True
    
    # Pattern: single word + colon (likely section)
    if len(text.split()) == 1 and text.endswith(':'):
        return True
    
    # Pattern: very short phrases (1-2 words) + colon
    if len(text.split()) <= 2 and text.endswith(':'):
        return True
    
    # Pattern: single word without colon (likely section)
    if len(text.split()) == 1:
        return True
    
    # Pattern: "Part X. Y" or "Part X) Y" - ALL of these are section headers to be ignored
    if re.match(r'^Part\s+[IVX\d]+[\.\)]\s*.*$', text):
        return True
    
    # Pattern: "I. Y" or "II. Y" patterns (Roman numerals)
    if re.match(r'^[IVX]+\.\s*.*$', text):
        return True
    
    # Pattern: "Items X-Y:" (section header to skip)
    if re.match(r'^Items\s+\d+[–-]\d+:', text):
        return True
    
    # Pattern: "N.B." patterns (skip these)
    if re.match(r'^N\.B\.', text):
        return True
    
    # Pattern: "Subject Test" (like "Mythology Test")
    if re.match(r'^[A-Za-z\s]+Test$', text):
        return True
    
    return False

def parse_test_file(test_file_path):
    """Parse a single test file and return questions as JSON"""
    
    # Read the file
    with open(test_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines for processing
    lines = content.split('\n')
    
    questions = []
    current_question = None
    current_instruction = None
    between_questions = True  # Track if we're between questions (after option D)
    
    # Determine if this is pre-2018 or post-2018 format
    year_match = re.search(r'state_(\d{4})', str(test_file_path))
    year = int(year_match.group(1)) if year_match else 2018
    is_pre_2018 = year <= 2017  # 2017 and earlier use pre-2018 format
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Skip header lines
        if re.match(r'^\d{4}\s+FJCL\s+State\s+(Latin\s+)?Forum', line):
            continue
        if re.match(r'^\d{4}\s+FJCL\s+State\s+Forum.*-$', line):
            continue
        if re.match(r'^\d{4}\s+FJCL\s+State\s+Forum.*\s+-\s*$', line):
            continue
        if re.match(r'^FJCL\s+State\s+Forum$', line):  # Skip standalone "FJCL State Forum"
            continue
        
        # Skip subject headers like "Derivatives I - States 2019 -"
        if re.match(r'^[A-Za-z\s]+I{0,3}\s*-\s*States?\s+\d{4}\s*-?\s*$', line):
            continue
        
        # Skip section dividers
        if re.match(r'^Part\s+(\d+)\s*[-–]\s*(.+)$', line):  # "Part 2 – Mottoes"
            continue
        if re.match(r'^Part\s+(\d+)-\s*(.+)$', line):  # "Part 1- Phrases"
            continue
        if re.match(r'^Part\s+([IVX]+):\s*(.+)$', line):  # "Part II: Mottoes"
            continue
        
        # Handle "Items X-Y: instruction" pattern BEFORE section header check
        if (between_questions and  # Only when between questions
            not re.match(r'^\d+\.', line)):  # Not a question number
            
            items_match = re.match(r'^Items\s+\d+[–-]\d+:\s*(.+)$', line)
            if items_match:
                instruction_text = items_match.group(1).strip()
                if current_instruction:
                    current_instruction += " " + instruction_text
                else:
                    current_instruction = instruction_text
                continue
        
        # SIMPLIFIED INSTRUCTION DETECTION (ONLY when between questions)
        # Instructions continue until a question number + period is seen
        if (between_questions and  # Only when between questions
            not re.match(r'^\d+\.', line) and  # Not a question number
            not is_section_header(line) and  # Not a section header
            line.strip()):  # Not empty
            
            # Concatenate instruction lines
            if current_instruction:
                current_instruction += " " + line.strip()
            else:
                current_instruction = line.strip()
            continue
        
        
        # Check for question numbers (with or without question text)
        question_match = re.match(r'^(\d+)\.\s*(.*)$', line)
        if question_match:
            # Save previous question if exists
            if current_question and len(current_question["options"]) > 0:
                questions.append(current_question)
            
            # Start new question with accumulated instruction
            question_num = int(question_match.group(1))
            question_text = question_match.group(2).strip()
            
            # Handle questions with no text (just number and options)
            if not question_text:
                question_text = ""
            
            # Determine instruction to use (inherit from previous if current is None)
            instruction_to_use = current_instruction
            if instruction_to_use is None and questions:
                # Inherit instruction from previous question
                instruction_to_use = questions[-1]["instruction"]
            
            current_question = {
                "question_number": question_num,
                "question": question_text,
                "options": {},
                "type": "multiple_choice",
                "instruction": instruction_to_use,
                "correct_answer": None
            }
            
            # Clear instruction for next question
            current_instruction = None
            between_questions = False  # We're now building a question
            continue
        
        # Check for answer options
        if current_question:
            # Handle pre-2018 format (lowercase options)
            if is_pre_2018:
                option_match = re.match(r'^([a-d])\.\s*(.+)$', line)
                if option_match:
                    option_letter = option_match.group(1).upper()
                    remaining_text = option_match.group(2).strip()
                    
                    # Check if there are multiple options on this line by looking for "b.", "c.", "d."
                    if re.search(r'\s+[b-d]\.\s+', remaining_text):
                        # Multiple options on one line - split them
                        parts = re.split(r'\s+([b-d])\.\s+', remaining_text)
                        if len(parts) > 1:
                            # First option (use the actual letter from the match)
                            first_option = parts[0].strip()
                            current_question["options"][option_letter] = first_option
                            
                            # Process remaining options
                            for i in range(1, len(parts), 2):
                                if i + 1 < len(parts):
                                    letter = parts[i].upper()
                                    text = parts[i + 1].strip()
                                    current_question["options"][letter] = text
                                    # If this was option D, we're now between questions
                                    if letter == 'D':
                                        between_questions = True
                    else:
                        # Single option on the line
                        current_question["options"][option_letter] = remaining_text
                        # If this was option D, we're now between questions
                        if option_letter == 'D':
                            between_questions = True
                    continue
            
            # Handle post-2018 format (uppercase options)
            else:
                option_match = re.match(r'^([A-D])\.\s*(.+)$', line)
                if option_match:
                    option_letter = option_match.group(1)
                    remaining_text = option_match.group(2).strip()
                    
                    # Check if there are multiple options on this line
                    if re.search(r'\s+[B-D]\.\s+', remaining_text):
                        # Multiple options on one line - split them
                        parts = re.split(r'\s+([B-D])\.\s+', remaining_text)
                        if len(parts) > 1:
                            # First option (use the actual letter from the match)
                            first_option = parts[0].strip()
                            current_question["options"][option_letter] = first_option
                            
                            # Process remaining options
                            for i in range(1, len(parts), 2):
                                if i + 1 < len(parts):
                                    letter = parts[i]
                                    text = parts[i + 1].strip()
                                    current_question["options"][letter] = text
                                    # If this was option D, we're now between questions
                                    if letter == 'D':
                                        between_questions = True
                    else:
                        # Single option on the line
                        current_question["options"][option_letter] = remaining_text
                        # If this was option D, we're now between questions
                        if option_letter == 'D':
                            between_questions = True
                    continue
            
            # If we have a current question and this line doesn't start with an option, 
            # it might be a continuation of the question statement
            if (not re.match(r'^([a-dA-D])\.\s*(.+)$', line) and  # Not an option
                not re.match(r'^\d+\.', line) and  # Not a new question number
                not re.match(r'^\d{4}\s+FJCL\s+State\s+(Latin\s+)?Forum', line) and  # Not a header
                not re.match(r'^\d{4}\s+FJCL\s+State\s+Forum.*-$', line) and  # Not headers ending with dash
                not re.match(r'^\d{4}\s+FJCL\s+State\s+Forum.*\s+-\s*$', line) and  # Not headers ending with space-dash-space
                not re.match(r'^Part\s+(\d+)\s*[-–]\s*(.+)$', line) and  # Not a section divider
                not re.match(r'^Part\s+(\d+)-\s*(.+)$', line) and  # Not a section divider (hyphen)
                not re.match(r'^Part\s+([IVX]+):\s*(.+)$', line) and  # Not a Part II: Mottoes divider
                not re.match(r'^[A-Za-z\s]+I{0,3}\s*-\s*States?\s+\d{4}\s*-?\s*$', line) and  # Not subject headers
                line.strip()):  # Not empty
                # This is a continuation of the question statement
                current_question["question"] += " " + line.strip()
                continue
        
    
    # Save the last question if it exists
    if current_question and len(current_question["options"]) > 0:
        questions.append(current_question)
    
    # Parse answer key
    answer_key = parse_answer_key(test_file_path)
    
    # Add correct answers to questions
    for question in questions:
        question_num = question["question_number"]
        if question_num in answer_key:
            question["correct_answer"] = answer_key[question_num]
    
    return {
        "questions": questions,
        "metadata": {
            "year": year,
            "format": "pre_2018" if is_pre_2018 else "post_2018",
            "total_questions": len(questions)
        }
    }

def parse_answer_key(test_file_path):
    """Parse the answer key file and return a dictionary of question_number -> answer"""
    answer_key_path = test_file_path.parent / f"{test_file_path.stem}_key.txt"
    
    if not answer_key_path.exists():
        return {}
    
    with open(answer_key_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for answer patterns like "1. A 2. B 3. C" or "1. A\n2. B\n3. C"
    answers = {}
    
    # Try to find answers in the format "number. letter"
    pattern = r'(\d+)\.\s*([A-D])'
    matches = re.findall(pattern, content)
    
    for question_num, answer in matches:
        answers[int(question_num)] = answer
    
    return answers

def main():
    """Main function to process all test files"""
    base_dir = Path("data/raw-data")
    
    # Process all test files
    for test_file in base_dir.rglob("*_test.txt"):
        print(f"Processing {test_file}")
        
        try:
            result = parse_test_file(test_file)
            
            # Save as JSON
            output_file = test_file.parent / "questions.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"  -> Saved {len(result['questions'])} questions to {output_file}")
            
        except Exception as e:
            print(f"  -> Error processing {test_file}: {e}")

if __name__ == "__main__":
    main()
