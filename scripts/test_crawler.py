#!/usr/bin/env python3
"""
Test script to verify FJCL crawler on a single year
"""

from fjcl_crawler import FJCLCrawler

def test_single_year():
    """Test crawler on a single year (2019)"""
    crawler = FJCLCrawler()
    
    # Test on 2019 first
    print("Testing crawler on 2019...")
    crawler.process_year(2019)

if __name__ == "__main__":
    test_single_year()
