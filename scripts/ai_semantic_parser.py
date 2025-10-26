#!/usr/bin/env python3
"""
AI-powered semantic parser for JCL test files
Uses an LLM to understand and parse test content semantically
"""

import re
import json
import os
from pathlib import Path
from anthropic import Anthropic

# Initialize Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def parse_answer_key(test_file_path):
    """Parse the answer key file and return a dictionary of question_number -> answer"""
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


def ai_parse_test(test_content, answer_key):
    """
    Use Claude AI to parse test content semantically
    The AI will understand the structure and extract questions properly
    """
    
    prompt = f"""You are an expert at parsing educational test files. Please analyze this JCL (Junior Classical League) Latin test and extract all questions with their options.

For each question, identify:
1. question_index: The question number (integer)
2. question_body: The question text (if the question has no text body, use "Question N" where N is the number)
3. question_options: A dictionary with keys A, B, C, D containing the option text
4. question_key: The correct answer letter (will be provided separately)
5. question_instruction: The instruction that applies to this question (e.g., "Choose what best completes the sentence", "Identify the Latin word", etc.)

Important notes:
- Instructions usually appear before a group of questions and apply to all following questions until a new instruction appears
- Some tests have options formatted as "a. X b. Y c. Z d. W" on one line (pre-2018 format)
- Some tests have options formatted as "A. X\\nB. Y\\nC. Z\\nD. W" on separate lines (post-2018 format)
- Some questions may have no question text, just a number followed by options - in these cases the instruction explains what to do
- Section headers like "Derivatives I", "FJCL State Forum", "- States 2019 -" should be ignored

Please output ONLY valid JSON in this exact format:
[
  {{
    "question_index": 1,
    "question_body": "question text here",
    "question_options": {{
      "A": "option A text",
      "B": "option B text", 
      "C": "option C text",
      "D": "option D text"
    }},
    "question_instruction": "instruction text here"
  }},
  ...
]

Here is the test content:

{test_content}

Please parse this test and return ONLY the JSON array, no other text."""

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=16000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text.strip()
        
        # Extract JSON from response (sometimes AI adds markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        questions = json.loads(response_text)
        
        # Add answer keys
        for question in questions:
            q_num = question['question_index']
            if q_num in answer_key:
                question['question_key'] = answer_key[q_num]
            else:
                question['question_key'] = "UNKNOWN"
        
        return questions
        
    except Exception as e:
        print(f"    Error during AI parsing: {e}")
        return []


def process_test_file(test_file_path):
    """Process a single test file using AI-powered parsing"""
    print(f"\nProcessing: {test_file_path}")
    
    # Read the test file
    with open(test_file_path, 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    # Parse answer key
    answer_key = parse_answer_key(test_file_path)
    print(f"  Found {len(answer_key)} answers in key")
    
    # Use AI to parse
    print(f"  Sending to Claude AI for semantic parsing...")
    questions = ai_parse_test(text_content, answer_key)
    
    print(f"  ✓ Parsed {len(questions)} questions")
    
    # Validate
    missing_keys = [q["question_index"] for q in questions if q.get("question_key") == "UNKNOWN"]
    if missing_keys:
        print(f"  Warning: Questions without answer keys: {missing_keys}")
    
    return questions


def main():
    """Main function to process test files using AI"""
    base_dir = Path("/Users/kylexu/JCL_AT_Buddy/data/raw-data")
    
    if not base_dir.exists():
        print(f"Error: Directory {base_dir} not found")
        return
    
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return
    
    # Find all test files across all years
    all_test_files = list(base_dir.rglob("*_test.txt"))
    
    # Filter out Classical_Art and Classical_Geography
    excluded_subjects = ['Classical_Art', 'Classical_Geography']
    test_files = [
        f for f in all_test_files 
        if not any(excluded in str(f) for excluded in excluded_subjects)
    ]
    
    print(f"Found {len(test_files)} test files to process with AI")
    print(f"(Excluded Classical_Art and Classical_Geography: {len(all_test_files) - len(test_files)} files)")
    print("\n" + "=" * 70)
    
    # For demo, just process 2019 files
    test_files_2019 = [f for f in test_files if 'state_2019' in str(f)]
    print(f"\nProcessing 2019 files first ({len(test_files_2019)} files)...")
    print("=" * 70)
    
    success_count = 0
    error_count = 0
    total_questions = 0
    
    for test_file in sorted(test_files_2019):
        try:
            questions = process_test_file(test_file)
            
            if questions:
                # Save as JSON
                output_file = test_file.parent / "ai_parsed.json"
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
    print(f"AI PARSING COMPLETE!")
    print("=" * 70)
    print(f"  Success: {success_count}/{len(test_files_2019)} files")
    print(f"  Errors: {error_count}")
    print(f"  Total questions: {total_questions}")
    print("=" * 70)


if __name__ == "__main__":
    main()

