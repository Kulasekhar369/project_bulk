from github import Github
import os

# --- STEP 1: Read GitHub Token from environment ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise Exception("❌ Environment variable GITHUB_TOKEN not set!")

# --- STEP 2: Initialize PyGithub ---
try:
    g = Github(GITHUB_TOKEN)
    user = g.get_user()
    print(f"✅ Authenticated as: {user.login}")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
    exit(1)

# --- STEP 3: Try accessing a specific repository ---
REPO_NAME = "your-org/your-repo"  # Replace with your repo, e.g., "octocat/Hello-World"

try:
    repo = g.get_repo(REPO_NAME)
    print(f"✅ Repository accessed: {repo.full_name}")
    print(f"📦 Default Branch: {repo.default_branch}")
    print(f"⭐ Stars: {repo.stargazers_count}")
    print(f"🔧 Permissions: {repo.permissions}")
except Exception as e:
    print(f"❌ Failed to access repository '{REPO_NAME}': {e}")
