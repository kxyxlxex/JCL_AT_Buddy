#!/usr/bin/env python3
"""
Consolidation script that uses ai_model_parsed.json files
"""

import json
from pathlib import Path

def consolidate_jcl_data():
    """Consolidate all ai_model_parsed.json files by subject across all years."""
    
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
            
            # Look for ai_model_parsed.json file
            ai_parsed_file = subject_dir / "ai_model_parsed.json"
            if ai_parsed_file.exists():
                try:
                    with open(ai_parsed_file, 'r', encoding='utf-8') as f:
                        questions = json.load(f)
                    
                    # ai_model_parsed.json is a list of questions
                    if isinstance(questions, list):
                        print(f"  Found {len(questions)} questions in {year}")
                        
                        # Add metadata to each question
                        for question in questions:
                            # Add source metadata
                            question['source_year'] = year
                            question['source_subject'] = subject
                            
                            # Count questions with answers
                            if question.get('question_key'):
                                subject_stats['questions_with_answers'] += 1
                        
                        # Add ALL questions
                        all_questions.extend(questions)
                        
                        # Update stats
                        question_count = len(questions)
                        subject_stats['total_questions'] += question_count
                        subject_stats['files_processed'] += 1
                        subject_stats['years_processed'] += 1
                        
                        print(f"  Added {question_count} questions from {year}")
                
                except Exception as e:
                    print(f"  Error processing {year}: {e}")
                    import traceback
                    traceback.print_exc()
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
