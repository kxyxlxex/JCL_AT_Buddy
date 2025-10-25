#!/usr/bin/env python3
"""
Script to consolidate all JCL test data into individual subject files
for the web application.
"""

import json
import os
import shutil
from pathlib import Path

def consolidate_jcl_data():
    """Consolidate all JSON files by subject across all years."""
    
    # Source directory (your JCL_AT_Buddy data)
    source_dir = Path("/Users/kylexu/JCL_AT_Buddy/data/raw-data")
    
    # Target directory for consolidated data
    target_dir = Path("/Users/kylexu/JCL_AT_Buddy/website/data")
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
            'post_2018_questions': 0
        }
        
        for year in years:
            year_dir = source_dir / year
            if not year_dir.exists():
                continue
                
            # Find the subject directory (handle different naming)
            subject_dir = None
            for potential_name in [subject, subject.replace('_', ' ')]:
                potential_path = year_dir / potential_name
                if potential_path.exists():
                    subject_dir = potential_path
                    break
            
            if not subject_dir:
                print(f"  No data found for {subject} in {year}")
                continue
            
            # Look for questions.json file
            questions_file = subject_dir / "questions.json"
            if questions_file.exists():
                try:
                    with open(questions_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if 'questions' in data:
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
                            
                            # For pre-2018, add section information if available
                            if is_pre_2018 and 'section' in question and question['section']:
                                question['has_section'] = True
                            else:
                                question['has_section'] = False
                        
                        all_questions.extend(data['questions'])
                        subject_stats['years_processed'] += 1
                        subject_stats['files_processed'] += 1
                        
                        if is_pre_2018:
                            subject_stats['pre_2018_questions'] += len(data['questions'])
                        else:
                            subject_stats['post_2018_questions'] += len(data['questions'])
                        
                        print(f"  Added {len(data['questions'])} questions from {year} ({'pre-2018' if is_pre_2018 else 'post-2018'} format)")
                    
                except Exception as e:
                    print(f"  Error processing {year}/{subject}: {e}")
        
        subject_stats['total_questions'] = len(all_questions)
        
        # Create consolidated file for this subject
        consolidated_data = {
            'subject_info': {
                'name': subject,
                'total_questions': len(all_questions),
                'years_covered': subject_stats['years_processed'],
                'pre_2018_questions': subject_stats['pre_2018_questions'],
                'post_2018_questions': subject_stats['post_2018_questions'],
                'description': get_subject_description(subject)
            },
            'questions': all_questions
        }
        
        # Save consolidated file
        output_file = target_dir / f"{subject.replace(',', '').replace(' ', '_')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
        
        print(f"  Saved {len(all_questions)} questions to {output_file.name}")
        print(f"  Stats: {subject_stats}")
        print()

def get_subject_description(subject):
    """Get a description for each subject."""
    descriptions = {
        'Derivatives_I': 'Basic Latin derivative questions and word formation',
        'Derivatives_II': 'Advanced Latin derivative questions and etymology',
        'History_of_the_Empire': 'Questions about Roman Empire history and events',
        'History_of_the_Monarchy_and_Republic': 'Questions about early Roman history',
        'Mottoes,_Abbreviations,_and_Quotations': 'Latin sayings, abbreviations, and famous quotations',
        'Mythology': 'Greek and Roman mythology, gods, heroes, and stories',
        'Vocabulary_I': 'Basic Latin vocabulary and word meanings',
        'Vocabulary_II': 'Advanced Latin vocabulary and specialized terms'
    }
    return descriptions.get(subject, f'Questions about {subject}')

def create_data_index():
    """Create an index file listing all available subjects."""
    target_dir = Path("/Users/kylexu/JCL_AT_Buddy/website/data")
    
    subjects = [
        'Derivatives_I', 'Derivatives_II',
        'History_of_the_Empire', 'History_of_the_Monarchy_and_Republic',
        'Mottoes_Abbreviations_and_Quotations', 'Mythology', 'Vocabulary_I', 'Vocabulary_II'
    ]
    
    index_data = {
        'subjects': [],
        'total_subjects': len(subjects),
        'last_updated': str(Path().cwd())
    }
    
    for subject in subjects:
        subject_file = target_dir / f"{subject.replace(',', '').replace(' ', '_')}.json"
        if subject_file.exists():
            try:
                with open(subject_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                index_data['subjects'].append({
                    'name': subject,
                    'file': subject_file.name,
                    'total_questions': data['subject_info']['total_questions'],
                    'description': data['subject_info']['description']
                })
            except Exception as e:
                print(f"Error reading {subject_file}: {e}")
    
    # Save index file
    with open(target_dir / 'index.json', 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print(f"Created data index with {len(index_data['subjects'])} subjects")

if __name__ == "__main__":
    print("Consolidating JCL test data...")
    print("=" * 50)
    
    consolidate_jcl_data()
    create_data_index()
    
    print("=" * 50)
    print("Data consolidation complete!")
    print("You can now use the website with consolidated data.")
