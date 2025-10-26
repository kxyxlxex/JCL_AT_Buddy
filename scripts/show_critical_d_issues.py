#!/usr/bin/env python3
"""
Show Critical D Option Issues
Shows exactly where the 3 types of critical D option issues are located.
"""

import os
import re
import glob
from pathlib import Path

def find_critical_d_issues():
    """Find the 3 critical types of D option issues"""
    
    # Find all test txt files
    pattern = 'data/raw-data/state_*/**/*_test.txt'
    test_files = glob.glob(pattern)
    
    print("🔍 CRITICAL D OPTION ISSUES LOCATION GUIDE")
    print("=" * 80)
    
    # Type 1: D options contaminated with question text
    print("\n1️⃣ D OPTIONS CONTAMINATED WITH QUESTION TEXT")
    print("=" * 60)
    print("Pattern: D. [number]. [Question text]")
    print("These need to be split into: D. [number] + [number]. [Question text]")
    print("-" * 60)
    
    type1_count = 0
    for file_path in sorted(test_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            found_in_file = False
            
            for i, line in enumerate(lines):
                if re.search(r'D\.\s+\d+\.\s+[A-Z]', line):
                    if not found_in_file:
                        print(f"\n📁 {file_path}")
                        found_in_file = True
                    print(f"  Line {i+1}: {line.strip()}")
                    type1_count += 1
                    
        except Exception as e:
            continue
    
    print(f"\n📊 Total Type 1 issues: {type1_count}")
    
    # Type 2: D options with incomplete date ranges
    print("\n\n2️⃣ D OPTIONS WITH INCOMPLETE DATE RANGES")
    print("=" * 60)
    print("Pattern: D. [number]–")
    print("These need the end date added (e.g., D. 149–146)")
    print("-" * 60)
    
    type2_count = 0
    for file_path in sorted(test_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            found_in_file = False
            
            for i, line in enumerate(lines):
                if re.search(r'D\.\s+\d+[–-]\s*$', line):
                    if not found_in_file:
                        print(f"\n📁 {file_path}")
                        found_in_file = True
                    print(f"  Line {i+1}: {line.strip()}")
                    type2_count += 1
                    
        except Exception as e:
            continue
    
    print(f"\n📊 Total Type 2 issues: {type2_count}")
    
    # Type 3: D options that are just numbers
    print("\n\n3️⃣ D OPTIONS THAT ARE JUST NUMBERS")
    print("=" * 60)
    print("Pattern: D. [number]")
    print("These need context added (e.g., D. 15 BC)")
    print("-" * 60)
    
    type3_count = 0
    for file_path in sorted(test_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            found_in_file = False
            
            for i, line in enumerate(lines):
                if re.match(r'D\.\s+\d+\s*$', line.strip()):
                    if not found_in_file:
                        print(f"\n📁 {file_path}")
                        found_in_file = True
                    print(f"  Line {i+1}: {line.strip()}")
                    type3_count += 1
                    
        except Exception as e:
            continue
    
    print(f"\n📊 Total Type 3 issues: {type3_count}")
    
    print("\n" + "=" * 80)
    print(f"🎯 SUMMARY:")
    print(f"   Type 1 (Contaminated): {type1_count} issues")
    print(f"   Type 2 (Incomplete dates): {type2_count} issues") 
    print(f"   Type 3 (Just numbers): {type3_count} issues")
    print(f"   TOTAL CRITICAL ISSUES: {type1_count + type2_count + type3_count}")
    print("=" * 80)

if __name__ == "__main__":
    find_critical_d_issues()
