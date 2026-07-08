#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify the meal planner works in cron-like environment
This simulates what happens when run from cron (no user interaction, etc.)
"""

import os
import sys
import tempfile
import shutil
from mock import patch

def test_environment_setup():
    """Test that the script can run with environment variables"""
    print "Testing environment variable handling..."
    
    # Set test environment variables
    test_env = {
        'NOTION_API_KEY': 'test_notion_key',
        'DATABASE_ID': 'test_database_id', 
        'EMAIL_PASSWORD': 'test_email_pass',
        'SENDER_EMAIL': 'test@example.com',
        'WIFE_EMAIL': 'wife@example.com'
    }
    
    with patch.dict(os.environ, test_env, clear=False):
        # Import after setting environment
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code'))
        try:
            from food_recommender import NOTION_API_KEY, EMAIL_PASSWORD
            if NOTION_API_KEY == 'test_notion_key' and EMAIL_PASSWORD == 'test_email_pass':
                print "Environment variables loaded correctly"
            else:
                print "Environment variables not loaded correctly"
                return False
        except Exception as e:
            print "Environment test failed: %s" % e
            return False
    
    return True

def test_should_send_today_logic():
    """Test the daily execution logic"""
    print "Testing daily execution logic..."
    
    # Create temporary directory for test
    tmpdir = tempfile.mkdtemp()
    old_dir = os.getcwd()
    os.chdir(tmpdir)
    
    try:
        # Import the function
        sys.path.insert(0, os.path.join(old_dir, 'code'))
        from food_recommender import should_send_today
        
        # First run should return True (no last_sent.txt)
        result = should_send_today()
        if result != True:
            print "First run should return True, got %s" % result
            return False
        print "First run correctly returns True"
        
        # Second run should return False (same day)
        result = should_send_today()
        if result != False:
            print "Second run should return False, got %s" % result
            return False
        print "Second run correctly returns False"
        
    finally:
        os.chdir(old_dir)
        shutil.rmtree(tmpdir)
        
    return True

def test_logging_function():
    """Test that logging works"""
    print "Testing logging function..."
    
    tmpdir = tempfile.mkdtemp()
    old_dir = os.getcwd()
    os.chdir(tmpdir)
    
    try:
        sys.path.insert(0, os.path.join(old_dir, 'code'))
        from food_recommender import log, LOG_FILE
        
        # Test logging
        test_msg = "Test log message"
        log(test_msg)
        
        # Check if log file was created and contains message
        if not os.path.exists(LOG_FILE):
            print "Log file should be created"
            return False
        with open(LOG_FILE, 'r') as f:
            content = f.read()
            if test_msg not in content:
                print "Log message should be in file"
                return False
        
        print "Logging function works correctly"
    finally:
        os.chdir(old_dir)
        shutil.rmtree(tmpdir)
        
    return True

if __name__ == "__main__":
    print "Running cron environment tests...\n"
    
    tests = [
        test_environment_setup,
        test_should_send_today_logic,
        test_logging_function
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print ""  # Blank line between tests
        except Exception as e:
            print "Test %s failed with exception: %s\n" % (test.__name__, e)
    
    print "Results: %d/%d tests passed" % (passed, total)
    
    if passed == total:
        print "All tests passed! Ready for cron deployment."
        sys.exit(0)
    else:
        print "Some tests failed. Please fix issues before deploying."
        sys.exit(1)