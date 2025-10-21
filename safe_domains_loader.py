"""
Safe Domains Loader - Fast startup module for production deployment

This module provides a fast-loading alternative to datas.py for production environments.
Instead of loading 2,801 email files (10-30 seconds), it loads a pre-computed cache file
containing 581 unique safe domains (<0.01 seconds).

For local development, it falls back to datas.py if the cache file is missing.
"""

import os
import json

# Path to the pre-computed safe domains cache
CACHE_FILE = 'safe_domains_cache.json'

def load_safe_domains_from_cache():
    """
    Load safe email domains from cache file or fall back to datas.py

    Returns:
        set: A set of unique safe email domains (e.g., {'@gmail.com', '@yahoo.com', ...})
    """
    # Try to load from cache first (production/Railway deployment)
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                domains_list = json.load(f)
            domains_set = set(domains_list)
            print(f"✅ Loaded {len(domains_set)} safe domains from cache (fast startup)")
            return domains_set
        except Exception as e:
            print(f"⚠️ Failed to load cache file: {e}")
            print("⚠️ Falling back to datas.py (slower startup)")

    # Fallback to datas.py for local development
    try:
        from datas import unique_from_emails
        print(f"✅ Loaded {len(unique_from_emails)} safe domains from datas.py (local development)")
        return unique_from_emails
    except Exception as e:
        print(f"❌ Failed to load safe domains: {e}")
        # Return empty set as last resort to prevent crash
        return set()

# Export the safe domains set with the same variable name as datas.py
# This allows drop-in replacement: `from safe_domains_loader import unique_from_emails`
unique_from_emails = load_safe_domains_from_cache()