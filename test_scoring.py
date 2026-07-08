#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the new scoring algorithm functions
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta

def test_new_functions():
    """Test the new scoring functions"""
    print("Testing new scoring functions...")

    # Add code directory to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code'))

    try:
        # Import the functions we want to test
        from food_recommender import get_recent_cuisine_penalty, get_seasonal_boost, compute_score

        # Create test dishes
        test_dishes = [
            {
                "name": "Test Dish 1",
                "meal": "Lunch",
                "your_rating": 4,
                "wife_rating": 3,
                "effort": 2,
                "tags": ["Light"],
                "last_eaten": (datetime.now() - timedelta(days=1)).isoformat(),
                "cuisine": "Indian"
            },
            {
                "name": "Test Dish 2",
                "meal": "Dinner",
                "your_rating": 5,
                "wife_rating": 4,
                "effort": 3,
                "tags": ["Comfort"],
                "last_eaten": (datetime.now() - timedelta(days=5)).isoformat(),
                "cuisine": "Italian"
            },
            {
                "name": "Test Dish 3",
                "meal": "Breakfast",
                "your_rating": 3,
                "wife_rating": 3,
                "effort": 1,
                "tags": ["Quick", "Light"],
                "last_eaten": None,  # Never eaten
                "cuisine": "Mexican"
            }
        ]

        # Test get_recent_cuisine_penalty
        penalty, cuisine_counts = get_recent_cuisine_penalty(test_dishes, lookback_days=3)
        print("Variety penalty: {0}".format(penalty))
        print("Cuisine counts: {0}".format(cuisine_counts))

        # Test get_seasonal_boost (will depend on current month)
        for dish in test_dishes:
            boost = get_seasonal_boost(dish)
            print("Seasonal boost for {0}: {1}".format(dish["name"], boost))

        # Test compute_score (base function)
        for dish in test_dishes:
            base_score = compute_score(dish)
            print("Base score for {0}: {1:.1f}".format(dish["name"], base_score))

        print("SUCCESS: All new functions executed without errors")
        return True

    except Exception as e:
        print("FAILED: Error testing new functions: {0}".format(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing scoring algorithm enhancements...\n")

    if test_new_functions():
        print("\nAll tests passed! The scoring enhancements are ready.")
        sys.exit(0)
    else:
        print("\nSome tests failed.")
        sys.exit(1)
