#!/usr/bin/env python3
"""
Script to fix parsing issues where multi-line questions were incorrectly split
"""

import json
import re
from pathlib import Path

def fix_parsing_issues():
    """Fix parsing issues in all raw data files"""
    raw_data_dir = Path('data/raw-data')
    json_files = list(raw_data_dir.rglob('questions.json'))
    
    print(f"Fixing parsing issues in {len(json_files)} files...")
    
    total_fixed = 0
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            file_fixed = 0
            
            if "questions" in data:
                # Look for questions that might be incomplete
                for i, question in enumerate(data["questions"]):
                    question_text = question.get("question", "")
                    instruction = question.get("instruction", "")
                    
                    # Check if this question looks incomplete and the next question's instruction looks like a continuation
                    if (question_text and 
                        any(question_text.strip().endswith(word) for word in ['at', 'in', 'on', 'to', 'of', 'for', 'with', 'by', 'the', 'a', 'an']) and
                        i + 1 < len(data["questions"])):
                        
                        next_question = data["questions"][i + 1]
                        next_instruction = next_question.get("instruction", "")
                        
                        # If the next question's instruction looks like a continuation of this question
                        if (next_instruction and 
                            not next_instruction.startswith(('Choose', 'Identify', 'Give', 'Match', 'Select', 'Answer')) and
                            len(next_instruction.split()) > 3):  # More than just a short instruction
                            
                            # Merge the instruction into the question
                            original_question = question_text
                            question["question"] = question_text + " " + next_instruction
                            question["instruction"] = None  # Clear the instruction since it's now part of the question
                            
                            # Clear the next question's instruction since we moved it
                            next_question["instruction"] = None
                            
                            file_fixed += 1
                            
                            print(f"  Fixed Q{question.get('question_number', i+1)}: '{original_question}' + '{next_instruction}'")
            
            if file_fixed > 0:
                # Save the fixed file
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"  ✓ {json_file.parent.name}: fixed {file_fixed} issues")
                total_fixed += file_fixed
            else:
                print(f"  - {json_file.parent.name}: no issues found")
        
        except Exception as e:
            print(f"  ✗ Error processing {json_file.parent.name}: {e}")
    
    print(f"\nTotal issues fixed: {total_fixed}")

if __name__ == "__main__":
    fix_parsing_issues()
