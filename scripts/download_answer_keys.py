#!/usr/bin/env python3
"""
Answer Key Downloader for FJCL Tests
Downloads answer keys for existing test directories
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin, urlparse
import PyPDF2
import pdfplumber

class AnswerKeyDownloader:
    def __init__(self, base_url="https://www.fjcl.org", data_dir="../data/raw-data"):
        self.base_url = base_url
        self.data_dir = data_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Target years for State tests
        self.target_years = list(range(2009, 2020))  # 2009-2019
        
        # Subject categories in the order they appear on the page
        self.target_subjects = [
            "Classical Art",
            "Classical Geography",
            "Customs",
            "Decathlon", 
            "Derivatives I",
            "Derivatives II",
            "Derivatives, Advanced",
            "Grammar I",
            "Grammar II",
            "Grammar, Advanced",
            "Greek Derivatives",
            "Greek Language",
            "Greek Literature",
            "Hellenic History",
            "Heptathlon",
            "History of the Empire",
            "History of the Monarchy & Republic",
            "Latin Literature",
            "Mottoes, Abbreviations, & Quotations",
            "Mythology",
            "Pentathlon",
            "Reading Comprehension, Poetry",
            "Reading Comprehension, Prose",
            "Vocabulary I",
            "Vocabulary II",
            "Vocabulary, Advanced"
        ]
        
        # Only extract the subjects we want (the original 10)
        self.extract_subjects = [
            "History of the Empire",
            "History of the Monarchy & Republic", 
            "Vocabulary I",
            "Vocabulary II",
            "Mottoes, Abbreviations, & Quotations",
            "Mythology",
            "Derivatives I",
            "Derivatives II",
            "Classical Art",
            "Classical Geography"
        ]
        
    def get_year_page(self, year):
        """Get the main page for a specific year"""
        year_url = f"{self.base_url}/{year}.html"
        try:
            response = self.session.get(year_url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {year_url}: {e}")
            return None
    
    def extract_answer_keys(self, html_content, year):
        """Extract answer key links using order-based mapping"""
        soup = BeautifulSoup(html_content, 'html.parser')
        key_links = {}
        
        # Find all "key" links in order
        all_links = soup.find_all('a', href=True)
        key_urls = []
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text().strip().lower()
            
            if href and (href.endswith('.pdf') or 'pdf' in href.lower()):
                if 'key' in text:
                    full_url = urljoin(self.base_url, href)
                    key_urls.append(full_url)
                    print(f"  Found key #{len(key_urls)}: {full_url}")
        
        # Map keys to subjects in order
        for i, subject in enumerate(self.target_subjects):
            if i < len(key_urls):
                key_links[subject] = key_urls[i]
                print(f"  Mapped {subject} -> Key #{i+1}")
            else:
                key_links[subject] = None
                print(f"  No key found for {subject}")
        
        return key_links
    
    def matches_subject(self, subject_lower, link_text, url):
        """Check if a key link matches a subject"""
        # Create subject mapping for better matching
        subject_mappings = {
            "history of the empire": ["empire", "imperial"],
            "history of the monarchy & republic": ["republic", "monarchy"],
            "vocabulary i": ["vocabulary_1", "vocab_1"],
            "vocabulary ii": ["vocabulary_2", "vocab_2"],
            "mottoes, abbreviations, & quotations": ["mottoes", "quotations"],
            "mythology": ["mythology"],
            "derivatives i": ["derivatives_1", "deriv_1"],
            "derivatives ii": ["derivatives_2", "deriv_2"],
            "classical art": ["classical_art", "art"],
            "classical geography": ["geography", "geo"]
        }
        
        # Get keywords for this subject
        keywords = subject_mappings.get(subject_lower, [subject_lower.split()[0]])
        
        # Check if any keyword appears in the URL or link text
        for keyword in keywords:
            if keyword in url.lower() or keyword in link_text.lower():
                return True
        
        return False
    
    def download_pdf(self, url, filepath):
        """Download PDF file"""
        try:
            print(f"Downloading: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filepath}")
            return True
        except requests.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return False
    
    def pdf_to_text(self, pdf_path, txt_path):
        """Convert PDF to text using pdfplumber"""
        try:
            text_content = ""
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            
            # Clean up the text
            text_content = re.sub(r'\s+', ' ', text_content)
            text_content = text_content.strip()
            
            # Write to file
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text_content)
            
            print(f"Converted to text: {txt_path} ({len(text_content)} characters)")
            return True
            
        except Exception as e:
            print(f"Error converting PDF {pdf_path}: {e}")
            return False
    
    def process_year(self, year):
        """Process answer keys for a specific year"""
        print(f"\n=== Processing Answer Keys for {year} ===")
        
        # Get year page
        html_content = self.get_year_page(year)
        if not html_content:
            return
        
        # Extract answer key links
        key_links = self.extract_answer_keys(html_content, year)
        print(f"Found {len([k for k in key_links.values() if k])} answer key links")
        
        year_dir = os.path.join(self.data_dir, f"state_{year}")
        
        # Only process the subjects we want to extract
        for subject in self.extract_subjects:
            key_url = key_links.get(subject)
            if key_url:
                print(f"\nProcessing {subject} answer key...")
                
                # Find existing subject directory
                subject_dir = os.path.join(year_dir, subject.replace(' ', '_').replace('&', 'and'))
                
                if os.path.exists(subject_dir):
                    # Download answer key PDF
                    key_pdf = os.path.join(subject_dir, f"{subject.replace(' ', '_')}_key.pdf")
                    if self.download_pdf(key_url, key_pdf):
                        # Convert to text
                        key_txt = key_pdf.replace('.pdf', '.txt')
                        self.pdf_to_text(key_pdf, key_txt)
                else:
                    print(f"  Subject directory not found: {subject_dir}")
            else:
                print(f"No answer key found for {subject}")
            
            # Be respectful to the server
            time.sleep(1)
    
    def download_all_keys(self):
        """Download answer keys for all target years"""
        print("Starting Answer Key Downloader...")
        print(f"Target years: {self.target_years}")
        print(f"Target subjects: {self.target_subjects}")
        
        # Process each year
        for year in self.target_years:
            self.process_year(year)
            time.sleep(2)  # Be respectful to the server
        
        print("\nAnswer key downloading completed!")

def main():
    downloader = AnswerKeyDownloader()
    downloader.download_all_keys()

if __name__ == "__main__":
    main()
