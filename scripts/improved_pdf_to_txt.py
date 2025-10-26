#!/usr/bin/env python3
"""
Improved PDF to Text Converter
Handles PDF-to-text conversion with advanced text cleaning for JCL test files.
Separated from crawler for better organization.
"""

import os
import re
import PyPDF2
import pdfplumber
from pathlib import Path

class ImprovedPDFToTextConverter:
    def __init__(self, data_dir="../data/raw-data"):
        self.data_dir = data_dir
        
    def pdf_to_text_improved(self, pdf_path, txt_path):
        """Improved PDF to text conversion using pdfplumber"""
        try:
            text_content = ""
            
            # Try pdfplumber first (better text extraction)
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
            except ImportError:
                print("pdfplumber not available, falling back to PyPDF2")
                # Fallback to PyPDF2
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
            
            # Clean up the text
            text_content = self.clean_text(text_content)
            
            # Write to file
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text_content)
            
            print(f"Converted to text: {txt_path} ({len(text_content)} characters)")
            return True
            
        except Exception as e:
            print(f"Error converting PDF {pdf_path}: {e}")
            return False
    
    def clean_text(self, text):
        """Clean and format extracted text with proper line breaks"""
        if not text:
            return ""
        
        # Fix common PDF extraction issues first
        text = text.replace('ﬁ', 'fi')
        text = text.replace('ﬂ', 'fl')
        text = text.replace('ﬀ', 'ff')
        
        # Remove page numbers and headers
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'\d+\s*$', '', text, flags=re.MULTILINE)
        
        # CRITICAL FIX: Handle multiple answer options on the same line
        # Split lines that contain multiple answer options (A., B., C., D.)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Check if line contains multiple answer options
            if re.search(r'[A-D]\.\s+.*[A-D]\.\s+', line):
                # Split by answer options, keeping the option letters
                parts = re.split(r'([A-D]\.\s+)', line)
                if len(parts) > 1:
                    # Reconstruct with proper line breaks
                    current_option = ""
                    for i, part in enumerate(parts):
                        if re.match(r'[A-D]\.\s+', part):
                            # Save previous option if exists
                            if current_option.strip():
                                cleaned_lines.append(current_option.strip())
                            current_option = part
                        else:
                            current_option += part
                    # Add the last option
                    if current_option.strip():
                        cleaned_lines.append(current_option.strip())
                else:
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        
        # CRITICAL FIX: Detect and fix answer options contaminated with next questions
        # Pattern: "D. 46. The dates..." -> "D. 46" + separate line for "46. The dates..."
        # This preserves the question while fixing the contaminated answer option
        def fix_contaminated_option(match):
            option_letter = match.group(1)
            question_num = match.group(2)
            question_text = match.group(3)
            return f"{option_letter}. {question_num}\n{question_num}. {question_text}"
        
        # Apply the fix with proper question preservation - ONLY for cases where we have a question number
        # Don't truncate regular D options that just happen to have numbers
        text = re.sub(r'([A-D])\.\s+(\d+)\.\s+([A-Z][^A-D]*?)(?=\n[A-D]\.|\n\d+\.|$)', 
                     fix_contaminated_option, text, flags=re.MULTILINE)
        
        # Add line breaks before question numbers (but be more careful)
        text = re.sub(r'(\n|^)(\d+)\.\s+([A-Z][^A-D]*)', r'\1\n\2. \3', text)
        
        # Add line breaks before answer options (A., B., C., D.)
        text = re.sub(r'(\n|^)([A-D])\.\s+', r'\1\n\2. ', text)
        
        # Clean up multiple consecutive newlines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove excessive whitespace but preserve line breaks
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
        text = re.sub(r' \n', '\n', text)   # Remove trailing spaces before newlines
        text = re.sub(r'\n ', '\n', text)   # Remove leading spaces after newlines
        
        return text.strip()
    
    def convert_single_pdf(self, pdf_path):
        """Convert a single PDF file to text"""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            print(f"PDF file not found: {pdf_path}")
            return False
        
        txt_path = pdf_path.with_suffix('.txt')
        return self.pdf_to_text_improved(str(pdf_path), str(txt_path))
    
    def convert_all_pdfs_in_directory(self, directory_path):
        """Convert all PDF files in a directory to text"""
        directory = Path(directory_path)
        if not directory.exists():
            print(f"Directory not found: {directory}")
            return
        
        pdf_files = list(directory.glob("**/*.pdf"))
        print(f"Found {len(pdf_files)} PDF files to convert")
        
        for pdf_file in pdf_files:
            print(f"Converting: {pdf_file}")
            self.convert_single_pdf(pdf_file)
    
    def convert_all_test_pdfs(self):
        """Convert all test PDF files in the data directory"""
        data_path = Path(self.data_dir)
        if not data_path.exists():
            print(f"Data directory not found: {data_path}")
            return
        
        # Find all test PDF files
        test_pdfs = list(data_path.glob("**/*_test.pdf"))
        print(f"Found {len(test_pdfs)} test PDF files to convert")
        
        for pdf_file in test_pdfs:
            print(f"Converting: {pdf_file}")
            self.convert_single_pdf(pdf_file)

def main():
    converter = ImprovedPDFToTextConverter()
    
    # Convert all test PDFs
    converter.convert_all_test_pdfs()

if __name__ == "__main__":
    main()
