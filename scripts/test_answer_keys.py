#!/usr/bin/env python3
"""
Test script for answer key downloader
Tests on a single year to verify order-based mapping
"""

from download_answer_keys import AnswerKeyDownloader

def test_single_year():
    """Test answer key downloader on a single year (2019)"""
    downloader = AnswerKeyDownloader()
    
    # Test on 2019 first
    print("Testing answer key downloader on 2019...")
    downloader.process_year(2019)

if __name__ == "__main__":
    test_single_year()
