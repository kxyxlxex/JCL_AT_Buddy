#!/usr/bin/env python3
"""
Improved FJCL Test Crawler
Fixes issues with PDF text extraction and link parsing.
Downloads test files only (answer keys handled by separate test_answer_keys crawler).
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin, urlparse
# PDF-to-text conversion moved to improved_pdf_to_txt.py

class ImprovedFJCLCrawler:
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
    
    def extract_test_links_improved(self, html_content, year):
        """Improved link extraction with better parsing"""
        soup = BeautifulSoup(html_content, 'html.parser')
        test_links = {}
        
        # Look for all links first
        all_links = soup.find_all('a', href=True)
        print(f"Found {len(all_links)} total links on {year} page")
        
        # Create a mapping of link text to URLs
        link_map = {}
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            if href and (href.endswith('.pdf') or 'pdf' in href.lower()):
                full_url = urljoin(self.base_url, href)
                link_map[text.lower()] = full_url
                print(f"  Found PDF: '{text}' -> {full_url}")
        
        # Now match subjects to their links
        for subject in self.target_subjects:
            subject_lower = subject.lower()
            test_links[subject] = {'test': None, 'key': None}
            
            # Look for test link
            for link_text, url in link_map.items():
                if subject_lower in link_text and 'key' not in link_text:
                    test_links[subject]['test'] = url
                    break
            
            # Look for key link
            for link_text, url in link_map.items():
                if subject_lower in link_text and ('key' in link_text or 'answer' in link_text):
                    test_links[subject]['key'] = url
                    break
        
        return test_links
    
    def download_pdf(self, url, filepath):
        """Download PDF file with better error handling"""
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
    
    def process_year(self, year):
        """Process all tests for a specific year with improved logic"""
        print(f"\n=== Processing {year} ===")
        
        # Get year page
        html_content = self.get_year_page(year)
        if not html_content:
            return
        
        # Extract test links with improved method
        test_links = self.extract_test_links_improved(html_content, year)
        print(f"Found {len(test_links)} subjects with links")
        
        year_dir = os.path.join(self.data_dir, f"state_{year}")
        
        for subject, links in test_links.items():
            print(f"\nProcessing {subject}...")
            print(f"  Test link: {links['test']}")
            print(f"  Key link: {links['key']}")
            
            # Create subject directory
            subject_dir = os.path.join(year_dir, subject.replace(' ', '_').replace('&', 'and'))
            os.makedirs(subject_dir, exist_ok=True)
            
            # Download test PDF only (answer keys handled by separate crawler)
            if links['test']:
                test_pdf = os.path.join(subject_dir, f"{subject.replace(' ', '_')}_test.pdf")
                self.download_pdf(links['test'], test_pdf)
            
            # Skip answer key download - handled by test_answer_keys crawler
            if links['key']:
                print(f"  Skipping answer key download (handled by test_answer_keys crawler)")
            
            # Be respectful to the server
            time.sleep(2)
    
    def crawl_all_years(self):
        """Crawl all target years with improved processing (test files only)"""
        print("Starting Improved FJCL State Test Crawler...")
        print("Note: Answer keys are handled by the separate test_answer_keys crawler")
        print(f"Target years: {self.target_years}")
        print(f"Target subjects: {self.target_subjects}")
        
        # Create year directories
        self.create_year_directories()
        
        # Process each year
        for year in self.target_years:
            self.process_year(year)
            time.sleep(3)  # Be respectful to the server
        
        print("\nImproved test crawling completed!")

def main():
    crawler = ImprovedFJCLCrawler()
    crawler.crawl_all_years()

if __name__ == "__main__":
    main()
