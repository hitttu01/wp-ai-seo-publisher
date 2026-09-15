#!/usr/bin/env python3
"""
WordPress REST API Diagnostic & Reverse-Engineering Tool
Inspects Post ID 7291 (or any target post) to discover custom meta keys,
ACF structures, and media bindings.
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_SITE_URL", "https://mycarautogroup.com").rstrip('/')
USERNAME = os.getenv("WP_USERNAME")
PASSWORD = os.getenv("WP_APP_PASSWORD")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def diagnose_post(post_id: int = 7291, search_query: str = None):
    endpoint = f"{WP_URL}/wp-json/wp/v2/posts/{post_id}?context=edit"
    print(f"================================================================")
    print(f"🔎 Querying WordPress REST API: GET {endpoint}")
    print(f"👤 Authenticated as: {USERNAME}")
    print(f"================================================================")

    try:
        response = requests.get(
            endpoint,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers=HEADERS,
            timeout=25
        )

        print(f"HTTP Status Code: {response.status_code}\n")

        if response.status_code != 200:
            print(f"❌ Error: Received {response.status_code} - {response.text}")
            return None

        post_data = response.json()

        # 1. Root Level Keys
        print("📁 1. ROOT LEVEL JSON KEYS:")
        print(list(post_data.keys()))
        print("-" * 64)

        # 2. Featured Media Binding
        print("🖼️ 2. FEATURED MEDIA ATTRIBUTE:")
        featured_media_id = post_data.get("featured_media")
        print(f"  featured_media ID: {featured_media_id}")
        if "_links" in post_data and "wp:featuredmedia" in post_data["_links"]:
            print(f"  _links -> wp:featuredmedia: {json.dumps(post_data['_links']['wp:featuredmedia'], indent=2)}")
        print("-" * 64)

        # 3. Post Meta Dictionary
        print("🏷️ 3. POST META DICTIONARY (`meta`):")
        meta_dict = post_data.get("meta", {})
        print(json.dumps(meta_dict, indent=2))
        print("-" * 64)

        # 4. ACF Dictionary (if present)
        print("⚡ 4. ADVANCED CUSTOM FIELDS (`acf`):")
        acf_dict = post_data.get("acf", {})
        if acf_dict:
            print(json.dumps(acf_dict, indent=2))
        else:
            print("  [acf] is empty or not registered for this post type.")
        print("-" * 64)

        # 5. Search Tree for Seeded Test String
        print("🔍 5. SEARCH TREE FOR SEEDED DATA:")
        search_terms = [search_query.lower()] if search_query else ["test", "schema", "script", "gallery", "image", "bold"]

        matches_found = []

        def search_json_tree(obj, current_path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_path = f"{current_path}.{k}" if current_path else k
                    if any(term in k.lower() for term in search_terms):
                        matches_found.append((new_path, str(v)[:250]))
                    search_json_tree(v, new_path)
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    new_path = f"{current_path}[{idx}]"
                    search_json_tree(item, new_path)
            elif isinstance(obj, str):
                if any(term in obj.lower() for term in search_terms):
                    matches_found.append((current_path, obj[:250]))

        search_json_tree(post_data)

        if matches_found:
            print(f"Found {len(matches_found)} match(es) in response:")
            for path, snippet in matches_found:
                print(f"  📍 [{path}]: {snippet}")
        else:
            print("  No seeded test string matches found in the REST response.")

        print("================================================================")
        return post_data

    except Exception as e:
        print(f"❌ Exception occurred during diagnostic: {e}")
        return None


if __name__ == "__main__":
    diagnose_post(post_id=7291)
