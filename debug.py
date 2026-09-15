import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# 1. Set your WordPress details from environment
url = f"{os.getenv('WP_SITE_URL', 'https://mycarautogroup.com').rstrip('/')}/wp-json/wp/v2/posts/7291"
username = os.getenv("WP_USERNAME")
app_password = os.getenv("WP_APP_PASSWORD")

# 2. Add headers to disguise our script as a normal web browser to bypass Cloudflare
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

# 3. Make the GET request to fetch Post 7291
print(f"Fetching data for Post 7291...")
response = requests.get(url, headers=headers, auth=(username, app_password))

# 4. Print the results to find the secret keys
if response.status_code == 200:
    data = response.json()
    print("\n--- SUCCESS! HERE ARE THE KEYS ---")
    
    if 'meta' in data:
        print(json.dumps(data['meta'], indent=4))
    else:
        print("No 'meta' object found. Printing everything:")
        print(json.dumps(data, indent=4))
        
else:
    print(f"Failed! Status Code: {response.status_code}")
    print(response.text)