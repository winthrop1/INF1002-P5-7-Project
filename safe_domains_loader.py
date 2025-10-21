"""
Fast loader for safe domains using pre-computed cache.
This avoids loading 2800+ email files on every app startup.

Falls back to datas.py if cache file doesn't exist (for local development).
"""

import os
import json

# Path to cached safe domains file
CACHE_FILE = 'safe_domains_cache.json'

def load_safe_domains_from_cache():
    """
    Load safe domains from cache file (FAST - 0.01s vs 10+ seconds).

    Returns:
        set: Set of safe email domains with @ prefix (e.g., '@gmail.com')
    """
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                domains_list = json.load(f)
            print(f"✅ Loaded {len(domains_list)} safe domains from cache (fast startup)")
            return set(domains_list)
        except Exception as e:
            print(f"⚠️ Error loading cache: {e}, falling back to dataset extraction...")

    # Fallback: Use original datas.py (slow but works)
    print("⚠️ Cache file not found, loading from dataset (this may take 10-30 seconds)...")
    try:
        from datas import unique_from_emails
        print(f"✅ Loaded {len(unique_from_emails)} safe domains from dataset")
        return unique_from_emails
    except Exception as e:
        print(f"❌ Error loading from dataset: {e}")
        # Return empty set as last resort
        return set()

# Export unique_from_emails for compatibility with existing code
unique_from_emails = load_safe_domains_from_cache()
