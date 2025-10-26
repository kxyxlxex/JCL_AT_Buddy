#!/usr/bin/env python3
"""
Script to fix remaining parsing issues where questions are still incomplete
"""

import json
import re
from pathlib import Path

def fix_remaining_parsing():
    """Fix remaining parsing issues"""
    raw_data_dir = Path('data/raw-data')
    json_files = list(raw_data_dir.rglob('questions.json'))
    
    print(f"Fixing remaining parsing issues in {len(json_files)} files...")
    
    total_fixed = 0
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            file_fixed = 0
            
            if "questions" in data:
                # Look for questions that are still incomplete
                for i, question in enumerate(data["questions"]):
                    question_text = question.get("question", "")
                    
                    # Check if this question looks incomplete (ends with common incomplete words)
                    incomplete_endings = ['sowing', 'at', 'in', 'on', 'to', 'of', 'for', 'with', 'by', 'the', 'a', 'an']
                    if (question_text and 
                        any(question_text.strip().endswith(word) for word in incomplete_endings) and
                        i + 1 < len(data["questions"])):
                        
                        next_question = data["questions"][i + 1]
                        next_question_text = next_question.get("question", "")
                        
                        # If the next question starts with a word that could be a continuation
                        if (next_question_text and 
                            not next_question_text[0].isupper() and  # Doesn't start with capital (likely continuation)
                            len(next_question_text.split()) <= 10):  # Not too long (likely continuation)
                            
                            # Merge the next question text into this question
                            original_question = question_text
                            question["question"] = question_text + " " + next_question_text
                            
                            # Remove the next question since we merged it
                            data["questions"].pop(i + 1)
                            
                            file_fixed += 1
                            
                            print(f"  Fixed Q{question.get('question_number', i+1)}: '{original_question}' + '{next_question_text}'")
            
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
    fix_remaining_parsing()
