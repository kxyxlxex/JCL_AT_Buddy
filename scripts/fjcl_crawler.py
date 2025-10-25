open #!/usr/bin/env python3
"""
FJCL Test Crawler
Extracts State tests from FJCL website (2009-2019) and organizes them by year and subject.
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin, urlparse
import PyPDF2
import io

class FJCLCrawler:
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
        
    def create_year_directories(self):
        """Create directories for each year"""
        for year in self.target_years:
            year_dir = os.path.join(self.data_dir, f"state_{year}")
            os.makedirs(year_dir, exist_ok=True)
            print(f"Created directory: {year_dir}")
    
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
    
    def extract_test_links(self, html_content, year):
        """Extract test and answer key links from year page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        test_links = {}
        
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
                            if subject not in test_links:
                                test_links[subject] = {'test': None, 'key': None}
                            
                            # Look for test link in subject cell
                            test_link = subject_cell.find('a', href=True)
                            if test_link and test_link.get('href'):
                                href = test_link.get('href')
                                if href.endswith('.pdf') or 'pdf' in href.lower():
                                    test_links[subject]['test'] = urljoin(self.base_url, href)
                            
                            # Look for key link in the next cell
                            if key_cell:
                                key_link = key_cell.find('a', href=True)
                                if key_link and key_link.get('href'):
                                    href = key_link.get('href')
                                    if href.endswith('.pdf') or 'pdf' in href.lower():
                                        test_links[subject]['key'] = urljoin(self.base_url, href)
        
        # Fallback: if no structured content found, try the old method
        if not test_links:
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href')
                text = link.get_text().strip()
                
                # Look for our target subjects
                for subject in self.target_subjects:
                    if subject.lower() in text.lower():
                        # Check if it's a PDF link
                        if href and (href.endswith('.pdf') or 'pdf' in href.lower()):
                            # Determine if it's a test or answer key
                            is_answer_key = ('key' in text.lower() or 'answer' in text.lower() or 
                                          'answer key' in text.lower() or 'key' in href.lower())
                            
                            if subject not in test_links:
                                test_links[subject] = {'test': None, 'key': None}
                            
                            if is_answer_key:
                                test_links[subject]['key'] = urljoin(self.base_url, href)
                            else:
                                test_links[subject]['test'] = urljoin(self.base_url, href)
        
        return test_links
    
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
        """Process all tests for a specific year"""
        print(f"\n=== Processing {year} ===")
        
        # Get year page
        html_content = self.get_year_page(year)
        if not html_content:
            return
        
        # Extract test links
        test_links = self.extract_test_links(html_content, year)
        print(f"Found {len(test_links)} subjects with links")
        
        year_dir = os.path.join(self.data_dir, f"state_{year}")
        
        for subject, links in test_links.items():
            print(f"\nProcessing {subject}...")
            print(f"  Test link: {links['test']}")
            print(f"  Key link: {links['key']}")
            
            # Create subject directory
            subject_dir = os.path.join(year_dir, subject.replace(' ', '_').replace('&', 'and'))
            os.makedirs(subject_dir, exist_ok=True)
            
            # Download test PDF
            if links['test']:
                test_pdf = os.path.join(subject_dir, f"{subject.replace(' ', '_')}_test.pdf")
                if self.download_pdf(links['test'], test_pdf):
                    # Convert to text
                    test_txt = test_pdf.replace('.pdf', '.txt')
                    self.pdf_to_text(test_pdf, test_txt)
            
            # Download answer key PDF
            if links['key']:
                key_pdf = os.path.join(subject_dir, f"{subject.replace(' ', '_')}_key.pdf")
                if self.download_pdf(links['key'], key_pdf):
                    # Convert to text
                    key_txt = key_pdf.replace('.pdf', '.txt')
                    self.pdf_to_text(key_pdf, key_txt)
            
            # Be respectful to the server
            time.sleep(1)
    
    def crawl_all_years(self):
        """Crawl all target years"""
        print("Starting FJCL State Test Crawler...")
        print(f"Target years: {self.target_years}")
        print(f"Target subjects: {self.target_subjects}")
        
        # Create year directories
        self.create_year_directories()
        
        # Process each year
        for year in self.target_years:
            self.process_year(year)
            time.sleep(2)  # Be respectful to the server
        
        print("\nCrawling completed!")

def main():
    crawler = FJCLCrawler()
    crawler.crawl_all_years()

if __name__ == "__main__":
    main()
