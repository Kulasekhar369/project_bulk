import os
import requests

# Step 1: Get GitHub token from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()

if not GITHUB_TOKEN:
    raise Exception("❌ Environment variable GITHUB_TOKEN is not set")

# Step 2: Set headers for the API request
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Step 3: Make a request to the authenticated user endpoint
response = requests.get("https://api.github.com/user", headers=headers)

# Step 4: Process the response
if response.status_code == 200:
    user = response.json()
    print("✅ GitHub API Authentication Successful!")
    print(f"👤 Username: {user['login']}")
    print(f"📧 Email: {user.get('email', 'Not public')}")
    print(f"🆔 User ID: {user['id']}")
else:
    print("❌ Authentication failed.")
    print(f"Status Code: {response.status_code}")
    print("Response:", response.json())
