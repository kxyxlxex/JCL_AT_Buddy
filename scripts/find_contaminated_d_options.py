#!/usr/bin/env python3
"""
Find Contaminated D Options
Scans all test files to find cases where option D has been contaminated or overlaid.
"""

import os
import re
import glob
from pathlib import Path

def find_contaminated_d_options():
    """Find all cases where option D is contaminated or incomplete"""
    
    # Find all test txt files
    pattern = 'data/raw-data/state_*/**/*_test.txt'
    test_files = glob.glob(pattern)
    
    print(f"Scanning {len(test_files)} test files for contaminated D options...")
    print("=" * 80)
    
    total_issues = 0
    
    for file_path in sorted(test_files):
        print(f"\n📁 {file_path}")
        print("-" * 60)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            issues_found = 0
            
            for i, line in enumerate(lines):
                # Look for D options that might be contaminated
                if re.match(r'^D\.\s+', line.strip()):
                    # Check if it looks incomplete or contaminated
                    d_content = line.strip()
                    
                    # Pattern 1: D option followed by a question number (e.g., "D. 46. The dates...")
                    if re.search(r'D\.\s+\d+\.\s+[A-Z]', d_content):
                        print(f"  ❌ Line {i+1}: {d_content}")
                        print(f"     → Contaminated with question text")
                        issues_found += 1
                    
                    # Pattern 2: D option that ends abruptly (e.g., "D. 149–" or "D. 264–")
                    elif re.search(r'D\.\s+\d+[–-]\s*$', d_content):
                        print(f"  ❌ Line {i+1}: {d_content}")
                        print(f"     → Incomplete date range")
                        issues_found += 1
                    
                    # Pattern 3: D option that's just a number (e.g., "D. 46")
                    elif re.match(r'D\.\s+\d+\s*$', d_content):
                        print(f"  ❌ Line {i+1}: {d_content}")
                        print(f"     → Just a number (likely contaminated)")
                        issues_found += 1
                    
                    # Pattern 4: D option that seems too short compared to others
                    elif len(d_content) < 10:  # Very short D options
                        # Check context to see if it's suspicious
                        context_lines = []
                        for j in range(max(0, i-3), min(len(lines), i+4)):
                            if j != i:
                                context_lines.append(f"    {j+1}: {lines[j].strip()}")
                        
                        # If A, B, C are much longer, this D might be incomplete
                        prev_lines = lines[max(0, i-3):i]
                        if any(re.match(r'^[A-C]\.\s+', prev_line.strip()) for prev_line in prev_lines):
                            print(f"  ⚠️  Line {i+1}: {d_content}")
                            print(f"     → Suspiciously short compared to other options")
                            for ctx in context_lines:
                                print(ctx)
                            issues_found += 1
            
            if issues_found == 0:
                print("  ✅ No contaminated D options found")
            else:
                total_issues += issues_found
                print(f"  📊 Found {issues_found} issues in this file")
                
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
    
    print("\n" + "=" * 80)
    print(f"🎯 SUMMARY: Found {total_issues} total contaminated D options across all files")
    print("=" * 80)

def find_specific_patterns():
    """Find specific contamination patterns"""
    
    print("\n🔍 Looking for specific contamination patterns...")
    print("=" * 60)
    
    patterns = [
        (r'D\.\s+\d+\.\s+[A-Z]', "D option contaminated with question text"),
        (r'D\.\s+\d+[–-]\s*$', "D option with incomplete date range"),
        (r'D\.\s+\d+\s*$', "D option that's just a number"),
    ]
    
    pattern = 'data/raw-data/state_*/**/*_test.txt'
    test_files = glob.glob(pattern)
    
    for pattern_regex, description in patterns:
        print(f"\n📋 Pattern: {description}")
        print(f"   Regex: {pattern_regex}")
        print("-" * 40)
        
        found_any = False
        for file_path in sorted(test_files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if re.search(pattern_regex, line):
                        if not found_any:
                            found_any = True
                        print(f"  📄 {file_path}:{i+1} - {line.strip()}")
                        
            except Exception as e:
                continue
        
        if not found_any:
            print("  ✅ No matches found for this pattern")

if __name__ == "__main__":
    find_contaminated_d_options()
    find_specific_patterns()
