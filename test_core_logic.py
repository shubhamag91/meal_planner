#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test core logic without external dependencies (Google API, etc.)
"""

import os
import sys
import tempfile
import shutil

def test_basic_structure():
    """Test that our modified files have the correct structure"""
    print "Testing basic file structure..."
    
    # Check that key files exist
    required_files = [
        'code/food_db.py',
        'code/food_recommender.py',
        'setup_cron.sh',
        '.env.example'
    ]
    
    all_exist = True
    for f in required_files:
        if not os.path.exists(f):
            print "MISSING: %s" % f
            all_exist = False
        else:
            print "FOUND: %s" % f
    
    return all_exist

def test_environment_variable_usage():
    """Test that we're using environment variables instead of hardcoded values"""
    print "Testing environment variable usage..."
    
    # Check food_db.py
    with open('code/food_db.py', 'r') as f:
        content = f.read()
        if 'os.environ.get' in content and 'ntn_' not in content:
            print "SUCCESS: food_db.py uses environment variables"
            db_ok = True
        else:
            print "FAILED: food_db.py still has hardcoded values or missing os.environ.get"
            db_ok = False
    
    # Check food_recommender.py
    with open('code/food_recommender.py', 'r') as f:
        content = f.read()
        # Check for our environment variable pattern
        if ('os.environ.get' in content and 
            'NOTION_API_KEY = os.environ.get' in content and
            'ntn_' not in content and
            '***REMOVED_EMAIL_PASSWORD***' not in content):
            print "SUCCESS: food_recommender.py uses environment variables"
            rec_ok = True
        else:
            print "FAILED: food_recommender.py still has hardcoded values"
            rec_ok = False
    
    return db_ok and rec_ok

def test_cron_script_content():
    """Test that cron setup script has expected content"""
    print "Testing cron setup script content..."
    
    with open('setup_cron.sh', 'r') as f:
        content = f.read()
        
    checks = [
        ('PROJECT_DIR', 'Sets project directory'),
        ('LOG_DIR', 'Sets log directory'),
        ('CRON_TIME', 'Defines cron schedule'),
        ('crontab', 'Installs cron job'),
        ('.env', 'References environment file')
    ]
    
    all_good = True
    for check, desc in checks:
        if check in content:
            print "SUCCESS: {0}".format(desc)
        else:
            print "FAILED: Missing {0}".format(desc)
            all_good = False
    
    return all_good

def test_readme_updated():
    """Test that README mentions environment variables"""
    print "Testing README updates..."
    
    with open('README.md', 'r') as f:
        content = f.read()
        
    if 'export NOTION_API_KEY' in content and 'export EMAIL_PASSWORD' in content:
        print "SUCCESS: README mentions environment variables"
        return True
    else:
        print "FAILED: README doesn't properly document environment variables"
        return False

if __name__ == "__main__":
    print "Running core logic verification tests...\n"
    
    tests = [
        test_basic_structure,
        test_environment_variable_usage,
        test_cron_script_content,
        test_readme_updated
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
        print "All core tests passed! The security improvements are in place."
        print "Note: Full functionality testing requires installing Python dependencies."
        sys.exit(0)
    else:
        print "Some tests failed. Please review the issues above."
        sys.exit(1)