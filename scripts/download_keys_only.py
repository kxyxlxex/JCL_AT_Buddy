#!/usr/bin/env python3
"""
FJCL Answer Key Downloader
Downloads only answer keys for existing test directories (2009-2019)
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin, urlparse
import PyPDF2
import io

class FJCLKeyDownloader:
    def __init__(self, base_url="https://www.fjcl.org", data_dir="../data/raw-data"):
        self.base_url = base_url
        self.data_dir = data_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Target years for State tests
        self.target_years = list(range(2009, 2020))  # 2009-2019
        
        # Subject categories to extract
        self.target_subjects = [
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
    
    def extract_key_links(self, html_content, year):
        """Extract only answer key links from year page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        key_links = {}
        
        # Look for tables or structured content with two columns
        tables = soup.find_all('table')
        if not tables:
            # If no tables, look for divs or other structured content
            tables = soup.find_all(['div', 'section'])
        
        for table in tables:
            rows = table.find_all('tr') if table.name == 'table' else table.find_all(['div', 'p'])
            
            for row in rows:
                cells = row.find_all(['td', 'th', 'div', 'p'])
                if len(cells) >= 2:
                    # First cell should contain subject name
                    subject_cell = cells[0]
                    key_cell = cells[1] if len(cells) > 1 else None
                    
                    subject_text = subject_cell.get_text().strip()
                    
                    # Check if this matches our target subjects
                    for subject in self.target_subjects:
                        if subject.lower() in subject_text.lower():
                            # Look for key link in the next cell
                            if key_cell:
                                key_link = key_cell.find('a', href=True)
                                if key_link and key_link.get('href'):
                                    href = key_link.get('href')
                                    if href.endswith('.pdf') or 'pdf' in href.lower():
                                        key_links[subject] = urljoin(self.base_url, href)
                                        break
        
        return key_links
    
    def download_pdf(self, url, filepath):
        """Download PDF file"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filepath}")
            return True
        except requests.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return False
    
    def pdf_to_text(self, pdf_path, txt_path):
        """Convert PDF to text"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                with open(txt_path, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(text)
                
                print(f"Converted to text: {txt_path}")
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
        
        # Extract key links
        key_links = self.extract_key_links(html_content, year)
        print(f"Found {len(key_links)} answer key links")
        
        year_dir = os.path.join(self.data_dir, f"state_{year}")
        
        for subject, key_url in key_links.items():
            print(f"\nProcessing {subject} answer key...")
            print(f"  Key URL: {key_url}")
            
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
            
            # Be respectful to the server
            time.sleep(1)
    
    def download_all_keys(self):
        """Download answer keys for all target years"""
        print("Starting FJCL Answer Key Downloader...")
        print(f"Target years: {self.target_years}")
        print(f"Target subjects: {self.target_subjects}")
        
        # Process each year
        for year in self.target_years:
            self.process_year(year)
            time.sleep(2)  # Be respectful to the server
        
        print("\nAnswer key downloading completed!")

def main():
    downloader = FJCLKeyDownloader()
    downloader.download_all_keys()

if __name__ == "__main__":
    main()
