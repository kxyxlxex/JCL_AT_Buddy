#!/usr/bin/env python3
"""
Consolidation script that includes answer key parsing
"""

import json
import re
from pathlib import Path

def parse_answer_key(questions_file_path):
    """Parse the answer key file and return a dictionary of question_number -> answer"""
    # Look for any *_key.txt file in the same directory
    key_files = list(questions_file_path.parent.glob("*_key.txt"))
    
    if not key_files:
        return {}
    
    # Use the first key file found
    answer_key_path = key_files[0]
    
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

def consolidate_jcl_data():
    """Consolidate all JSON files by subject across all years."""
    
    # Source directory
    source_dir = Path("data/raw-data")
    
    # Target directory for consolidated data
    target_dir = Path("data")
    target_dir.mkdir(exist_ok=True)
    
    # List of subjects
    subjects = [
        'Derivatives_I', 'Derivatives_II',
        'History_of_the_Empire', 'History_of_the_Monarchy_and_Republic',
        'Mottoes,_Abbreviations,_and_Quotations', 'Mythology', 'Vocabulary_I', 'Vocabulary_II'
    ]
    
    # Years to process
    years = [f"state_{year}" for year in range(2009, 2020)]
    
    for subject in subjects:
        print(f"Processing {subject}...")
        
        all_questions = []
        subject_stats = {
            'total_questions': 0,
            'years_processed': 0,
            'files_processed': 0,
            'pre_2018_questions': 0,
            'post_2018_questions': 0,
            'questions_with_answers': 0
        }
        
        for year in years:
            year_dir = source_dir / year
            if not year_dir.exists():
                continue
                
            # Find the subject directory
            subject_dir = None
            if (year_dir / subject).exists():
                subject_dir = year_dir / subject
            else:
                # Try alternative naming
                alt_name = subject.replace('_', ' ')
                if (year_dir / alt_name).exists():
                    subject_dir = year_dir / alt_name
                else:
                    # Try with ampersand
                    alt_name2 = alt_name.replace(' and ', ' & ')
                    if (year_dir / alt_name2).exists():
                        subject_dir = year_dir / alt_name2
            
            if not subject_dir or not subject_dir.exists():
                continue
            
            # Look for questions.json file
            questions_file = subject_dir / "questions.json"
            if questions_file.exists():
                try:
                    with open(questions_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if 'questions' in data:
                        # Parse answer key
                        answer_key = parse_answer_key(questions_file)
                        print(f"  Found {len(answer_key)} answers in key for {year}")
                        
                        # Determine if this is pre-2018 or post-2018 format
                        year_num = int(year.split('_')[1])
                        is_pre_2018 = year_num < 2018
                        
                        # Add metadata to each question
                        for question in data['questions']:
                            question['source_year'] = year
                            question['source_subject'] = subject
                            question['format_era'] = 'pre_2018' if is_pre_2018 else 'post_2018'
                            
                            # Keep the original question_number for reference
                            if 'question_number' in question:
                                question['original_question_number'] = question['question_number']
                            
                            # Add correct answer if available
                            if question['question_number'] in answer_key:
                                question['correct_answer'] = answer_key[question['question_number']]
                                subject_stats['questions_with_answers'] += 1
                            else:
                                question['correct_answer'] = None
                            
                            # For pre-2018, add section information if available
                            if is_pre_2018 and 'section' in question and question['section']:
                                question['has_section'] = True
                            else:
                                question['has_section'] = False
                        
                        # Add ALL questions (no filtering)
                        all_questions.extend(data['questions'])
                        
                        # Update stats
                        question_count = len(data['questions'])
                        subject_stats['total_questions'] += question_count
                        subject_stats['files_processed'] += 1
                        subject_stats['years_processed'] += 1
                        
                        if is_pre_2018:
                            subject_stats['pre_2018_questions'] += question_count
                        else:
                            subject_stats['post_2018_questions'] += question_count
                        
                        print(f"  Added {question_count} questions from {year} ({'pre-2018' if is_pre_2018 else 'post-2018'} format)")
                
                except Exception as e:
                    print(f"  Error processing {year}: {e}")
                    continue
        
        # Save consolidated data
        if all_questions:
            # Create filename
            filename = subject.replace(' ', '_').replace(',', '').replace('&', 'and')
            if filename == 'Mottoes,_Abbreviations,_and_Quotations':
                filename = 'Mottoes_Abbreviations_and_Quotations'
            
            output_file = target_dir / f"{filename}.json"
            
            # Save with proper structure
            consolidated_data = {
                "subject": subject,
                "total_questions": len(all_questions),
                "questions": all_questions,
                "metadata": subject_stats
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
            
            print(f"  Saved {len(all_questions)} questions to {filename}.json")
            print(f"  Questions with answers: {subject_stats['questions_with_answers']}/{len(all_questions)}")
            print(f"  Stats: {subject_stats}")
        else:
            print(f"  No questions found for {subject}")
    
    print("\n" + "="*50)
    print("Data consolidation with answers complete!")

if __name__ == "__main__":
    consolidate_jcl_data()
