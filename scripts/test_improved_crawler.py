#!/usr/bin/env python3
"""
Test script for the improved FJCL crawler
Tests on a single year to verify PDF to text conversion with improved formatting
"""

from improved_fjcl_crawler import ImprovedFJCLCrawler

def test_single_year():
    """Test improved crawler on a single year (2019) with formatting fixes"""
    crawler = ImprovedFJCLCrawler()
    
    # Test on 2019 first to verify the formatting improvements
    print("Testing improved crawler on 2019...")
    print("This will test the new text formatting with proper line breaks")
    print("Answer keys will be skipped (handled by separate crawler)")
    print("-" * 50)
    
    crawler.process_year(2019)
    
    print("-" * 50)
    print("Test completed! Check the generated text files for proper formatting.")

if __name__ == "__main__":
    test_single_year()
