#!/usr/bin/env python3
"""
Simple parser for JCL test files - only handles instructions and questions
"""

import re
import json
from pathlib import Path

def handle_section_headers(text, mode='detect'):
    """
    Unified function to handle section headers - can detect or clean them
    
    Args:
        text: The text to process
        mode: 'detect' to return True/False if it's a header, 'clean' to remove headers from text
    
    Returns:
        For 'detect' mode: True if text is a section header, False otherwise
        For 'clean' mode: Cleaned text with headers removed
    """
    if not text:
        return False if mode == 'detect' else ""
    
    # All patterns that indicate section headers
    section_patterns = [
        # FJCL Forum patterns
        'Mythology:', 'Phrases:', 'Mottoes:', 'Abbreviations:', 'Quotations:', 
        'Derivatives:', 'History:', 'Vocabulary:', 'Classical Art:', 'Classical Geography:',
        'Empire:', 'Monarchy:', 'Republic:', 'Vocabulary I:', 'Vocabulary II:',
        'Derivatives I:', 'Derivatives II:', 'History of the Empire:', 
        'History of the Monarchy and Republic:', 'History of the Monarchy & Republic:', 'MYTHOLOGY:', 'MOTTOES:', 'PHRASES:',
        'QUOTATIONS:', 'ABBREVIATIONS:', 'Chlorus:', 'Derived:', 'English word(s):',
        'Equivalents:', 'Extra questions:', 'Geography:', 'Image:', 'Miscellaneous:',
        'Word:', 'Phrases, Mottoes, Abbreviations, and Quotations:',
        # Without colons
        'Mythology', 'Phrases', 'Mottoes', 'Abbreviations', 'Quotations',
        'Derivatives', 'History', 'Vocabulary', 'Classical Art', 'Classical Geography',
        'Empire', 'Monarchy', 'Republic', 'Vocabulary I', 'Vocabulary II',
        'Derivatives I', 'Derivatives II', 'History of the Empire',
        'History of the Monarchy and Republic', 'History of the Monarchy & Republic', 'MYTHOLOGY', 'MOTTOES', 'PHRASES',
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
    
    # Headers to remove as prefixes (for clean mode)
    prefix_headers = [
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
    
    if mode == 'detect':
        # Pattern: "STATE LATIN FORUM" or "FJCL State Forum" patterns
        if re.match(r'^(STATE\s+LATIN\s+FORUM|FJCL\s+State\s+(Latin\s+)?Forum)', text, re.IGNORECASE):
            return True
        
        # Pattern: "Subject - States YYYY -" patterns (like "Derivatives 2 - States 2018 -")
        if re.match(r'^[A-Za-z\s]+I{0,3}\s*-\s*States?\s+\d{4}\s*-?\s*$', text):
            return True
        
        # Pattern: "Subject YYYY -" patterns (like "Derivatives 2 - States 2018 -")
        if re.match(r'^[A-Za-z\s]+\d{4}\s*-?\s*$', text):
            return True
        
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
        
        # Pattern: "Part X. Y" or "Part X) Y" or "Part X : Y" - ALL of these are section headers to be ignored
        if re.match(r'^Part\s+[IVX\d]+[\.\)\s*:]\s*.*$', text):
            return True
        
        # Pattern: "I. Y" or "II. Y" patterns (Roman numerals) - BUT NOT if it's followed by instruction text
        # If it's more than 3 words, it's probably an instruction, not a section header
        if re.match(r'^[IVX]+\.\s*.*$', text):
            words = text.split()
            if len(words) > 3:
                return False  # It's an instruction, not a section header
            # Also check if it contains instruction keywords
            instruction_keywords = ['choose', 'identify', 'complete', 'select', 'match', 'find', 'determine', 'given']
            text_lower = text.lower()
            if any(keyword in text_lower for keyword in instruction_keywords):
                return False  # It's an instruction, not a section header
            return True  # It's a short section header
        
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
    
    elif mode == 'clean':
        # Remove useless headers as prefixes
        cleaned_text = text
        for header in prefix_headers:
            # Remove as prefix (case insensitive)
            if cleaned_text.lower().startswith(header.lower()):
                cleaned_text = cleaned_text[len(header):].strip()
                # Remove leading newlines
                while cleaned_text.startswith('\n'):
                    cleaned_text = cleaned_text[1:]
        
        return cleaned_text.strip()
    
    else:
        raise ValueError("Mode must be 'detect' or 'clean'")

def parse_test_file(test_file_path):
    """Parse a single test file and return questions as JSON"""
    
    # Read the file
    with open(test_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Determine if this is pre-2018 or post-2018 format
    year_match = re.search(r'state_(\d{4})', str(test_file_path))
    year = int(year_match.group(1)) if year_match else 2018
    is_pre_2018 = year <= 2017  # 2017 and earlier use pre-2018 format
    
    print(f"DEBUG: Processing {test_file_path}, year={year}, is_pre_2018={is_pre_2018}")
    
    questions = []
    i = 0
    
    # State machine states
    STATE_INSTRUCTION = 0
    STATE_QUESTION = 1
    STATE_OPTION_A = 2
    STATE_OPTION_B = 3
    STATE_OPTION_C = 4
    STATE_OPTION_D = 5
    
    state = STATE_INSTRUCTION
    current_instruction = ""
    current_question_num = None
    current_question_text = ""
    current_options = {}
    current_option_text = ""
    
    def is_number_period(pos):
        """Check if position starts with number + period"""
        if pos >= len(content):
            return False, None
        
        # Extract digits
        num_start = pos
        num_end = pos
        while num_end < len(content) and content[num_end].isdigit():
            num_end += 1
        
        # Must have at least one digit and be followed by period
        if num_end > num_start and num_end < len(content) and content[num_end] == '.':
            return True, int(content[num_start:num_end])
        return False, None
    
    def is_option_letter(pos, letter, is_pre):
        """Check if position has the option letter + period"""
        if pos >= len(content) - 1:
            return False
        
        if is_pre:
            return content[pos].lower() == letter.lower() and content[pos + 1] == '.'
        else:
            return content[pos].upper() == letter.upper() and content[pos + 1] == '.'
    
    while i < len(content):
        # Check for transitions
        is_num_period, question_num = is_number_period(i)
        
        if state == STATE_INSTRUCTION:
            # Transition: number + period -> STATE_QUESTION
            if is_num_period:
                # Save instruction if non-empty
                cleaned = handle_section_headers(current_instruction.strip(), mode='clean')
                if cleaned and not handle_section_headers(cleaned, mode='detect'):
                    current_instruction = cleaned
                else:
                    current_instruction = ""
                
                # Move to question state
                state = STATE_QUESTION
                current_question_num = question_num
                current_question_text = ""
                current_options = {}
                
                # Skip past "number."
                while i < len(content) and content[i].isdigit():
                    i += 1
                i += 1  # Skip period
                
                print(f"DEBUG Q{current_question_num}: Started question")
                continue
            else:
                # Accumulate instruction text
                current_instruction += content[i]
                i += 1
                
        elif state == STATE_QUESTION:
            # Transition: option letter 'a' or 'A' + period -> STATE_OPTION_A
            if is_option_letter(i, 'a', is_pre_2018):
                current_question_text = current_question_text.strip()
                state = STATE_OPTION_A
                current_option_text = ""
                i += 2  # Skip "a."
                print(f"DEBUG Q{current_question_num}: Question text = {repr(current_question_text[:50])}")
                continue
            else:
                # Accumulate question text
                current_question_text += content[i]
                i += 1
                
        elif state == STATE_OPTION_A:
            # Transition: option letter 'b' + period -> STATE_OPTION_B
            if is_option_letter(i, 'b', is_pre_2018):
                current_options['A'] = current_option_text.strip()
                state = STATE_OPTION_B
                current_option_text = ""
                i += 2  # Skip "b."
                print(f"DEBUG Q{current_question_num}: Option A = {repr(current_options['A'])}")
                continue
            else:
                # Accumulate option A text
                current_option_text += content[i]
                i += 1
                
        elif state == STATE_OPTION_B:
            # Transition: option letter 'c' + period -> STATE_OPTION_C
            if is_option_letter(i, 'c', is_pre_2018):
                current_options['B'] = current_option_text.strip()
                state = STATE_OPTION_C
                current_option_text = ""
                i += 2  # Skip "c."
                print(f"DEBUG Q{current_question_num}: Option B = {repr(current_options['B'])}")
                continue
            else:
                # Accumulate option B text
                current_option_text += content[i]
                i += 1
                
        elif state == STATE_OPTION_C:
            # Transition: option letter 'd' + period -> STATE_OPTION_D
            if is_option_letter(i, 'd', is_pre_2018):
                current_options['C'] = current_option_text.strip()
                state = STATE_OPTION_D
                current_option_text = ""
                i += 2  # Skip "d."
                print(f"DEBUG Q{current_question_num}: Option C = {repr(current_options['C'])}")
                continue
            else:
                # Accumulate option C text
                current_option_text += content[i]
                i += 1
                
        elif state == STATE_OPTION_D:
            # Transition: number + period OR end of file -> Save question, move to STATE_INSTRUCTION or STATE_QUESTION
            if is_num_period or i >= len(content) - 1:
                # Save option D
                if i >= len(content) - 1 and not is_num_period:
                    # At end of file, include remaining text
                    current_option_text += content[i]
                
                # Clean up option D - remove section headers
                option_d_text = current_option_text.strip()
                # Split by newlines and remove section headers
                lines = option_d_text.split('\n')
                cleaned_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not handle_section_headers(line, mode='detect'):
                        cleaned_lines.append(line)
                option_d_text = ' '.join(cleaned_lines)
                
                current_options['D'] = option_d_text
                print(f"DEBUG Q{current_question_num}: Option D = {repr(current_options['D'])}")
                
                # Save the complete question
                questions.append({
                    "question_number": current_question_num,
                    "question": current_question_text,
                    "options": current_options.copy(),
                    "type": "multiple_choice",
                    "instruction": current_instruction if current_instruction else None,
                    "correct_answer": None
                })
                
                print(f"DEBUG Q{current_question_num}: Completed question\n")
                
                # Reset for next question
                if is_num_period:
                    # Next question starts immediately
                    state = STATE_QUESTION
                    current_question_num = question_num
                    current_question_text = ""
                    current_options = {}
                    
                    # Skip past "number."
                    while i < len(content) and content[i].isdigit():
                        i += 1
                    i += 1  # Skip period
                    print(f"DEBUG Q{current_question_num}: Started question")
                else:
                    # End of file
                    state = STATE_INSTRUCTION
                    current_instruction = ""
                    i += 1
                
                continue
            else:
                # Accumulate option D text
                current_option_text += content[i]
                i += 1
    
    print(f"DEBUG: Total questions found: {len(questions)}")
    
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
