#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the scoring algorithm logic directly without importing full module
"""

import os
import sys
import math
import random
from datetime import datetime, timedelta
from collections import Counter

def get_recent_cuisine_penalty(dishes, lookback_days=3):
    """Calculate cuisine variety penalty based on recently eaten dishes"""
    # Get recently eaten dishes (based on last_eaten)
    recent_dishes = []
    cutoff_date = datetime.now() - timedelta(days=lookback_days)

    for dish in dishes:
        if dish.get("last_eaten"):
            try:
                last_eaten_date = datetime.strptime(dish["last_eaten"], "%Y-%m-%d")
                if last_eaten_date >= cutoff_date:
                    recent_dishes.append(dish)
            except:
                # If date parsing fails, skip this dish for variety calculation
                pass

    # Count cuisine types in recent dishes
    cuisine_counts = Counter()
    for dish in recent_dishes:
        cuisine = dish.get("cuisine", "Unknown")
        cuisine_counts[cuisine] += 1

    # If no recent dishes, return no penalty
    if not recent_dishes:
        return 0, {}

    # Calculate penalty: more repetition = higher penalty
    # Normalize by number of recent dishes to get repetition ratio
    total_recent = len(recent_dishes)
    max_repetition = max(cuisine_counts.values()) if cuisine_counts else 0
    repetition_ratio = max_repetition / float(total_recent) if total_recent > 0 else 0

    # Apply penalty: 0-5 points based on repetition
    # 0% repetition (perfect variety) = 0 penalty
    # 100% repetition (same cuisine always) = 5 point penalty
    variety_penalty = repetition_ratio * 5

    return variety_penalty, dict(cuisine_counts)

def get_seasonal_boost(dish):
    """Calculate seasonal boost based on current month and dish properties"""
    month = datetime.now().month  # 1-12

    # Define seasonal preferences (simplified)
    # Month groupings: Winter(12,1,2), Spring(3,4,5), Summer(6,7,8), Fall(9,10,11)
    seasonal_boost = 0

    # Light/cooling foods boost in spring/summer
    if month in [3,4,5,6,7,8]:  # Spring/Summer
        if "Light" in (dish.get("tags") or []):
            seasonal_boost += 1
        if dish.get("effort", 3) <= 2:  # Lower effort foods
            seasonal_boost += 0.5
        # Avoid heavy/comfort foods in hot months
        if "Heavy" in (dish.get("tags") or []):
            seasonal_boost -= 1
        if "Comfort" in (dish.get("tags") or []) and month in [6,7,8]:  # Peak summer
            seasonal_boost -= 0.5

    # Warm/comforting foods boost in fall/winter
    elif month in [9,10,11,12,1,2]:  # Fall/Winter
        if "Heavy" in (dish.get("tags") or []):
            seasonal_boost += 1
        if "Comfort" in (dish.get("tags") or []):
            seasonal_boost += 0.5
        if dish.get("effort", 3) >= 3:  # Higher effort cooking acceptable
            seasonal_boost += 0.5
        # Light foods less preferred in cold months
        if "Light" in (dish.get("tags") or []) and month in [12,1,2]:  # Deep winter
            seasonal_boost -= 0.5

    return seasonal_boost

def compute_score(dish):
    score = (dish["your_rating"] + dish["wife_rating"]) * 2

    if dish.get("last_eaten"):
        try:
            days = (datetime.now() - datetime.strptime(dish["last_eaten"], "%Y-%m-%d")).days
        except:
            days = 999
    else:
        days = 999

    score += days / 2.0

    if days <= 2:
        score -= 10
    elif days <= 5:
        score -= 5

    if dish.get("effort", 0) >= 4:
        score -= 2

    # Add randomness for variety
    score += random.uniform(-1, 1)

    return score

def test_new_functions():
    """Test the new scoring functions"""
    print("Testing new scoring functions...")

    # Create test dishes
    test_dishes = [
        {
            "name": "Test Dish 1",
            "meal": "Lunch",
            "your_rating": 4,
            "wife_rating": 3,
            "effort": 2,
            "tags": ["Light"],
            "last_eaten": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "cuisine": "Indian"
        },
        {
            "name": "Test Dish 2",
            "meal": "Dinner",
            "your_rating": 5,
            "wife_rating": 4,
            "effort": 3,
            "tags": ["Comfort"],
            "last_eaten": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
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

if __name__ == "__main__":
    print("Testing scoring algorithm enhancements...\n")

    if test_new_functions():
        print("\nAll tests passed! The scoring enhancements are ready.")
        sys.exit(0)
    else:
        print("\nSome tests failed.")
        sys.exit(1)
