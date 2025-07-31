import os
import shutil
import yaml
from datetime import datetime
from github import Github
from git import Repo

# -------------------- CONFIG --------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
REPO_NAME = "your-org/your-repo"  # e.g., "octocat/Hello-World"
MANIFEST_FILENAME = "manifest.yaml"
BRANCH_NAME = "auto-update-" + datetime.now().strftime("%Y%m%d%H%M%S")
COMMIT_MESSAGE = "Update manifest.yaml automatically"
PR_TITLE = "Automated update to manifest.yaml"
PR_BODY = "This pull request was created automatically using PyGithub."
# ------------------------------------------------

if not GITHUB_TOKEN:
    raise Exception("❌ GITHUB_TOKEN is not set")

# --- Authenticate with PyGithub ---
g = Github(
    base_url="https://api.github.com",
    login_or_token=GITHUB_TOKEN
)

user = g.get_user()
print(f"✅ Authenticated as: {user.login}")

# --- Get the repository object ---
repo = g.get_repo(REPO_NAME)
default_branch = repo.default_branch
print(f"🌿 Default branch: {default_branch}")

# --- Prepare clone ---
clone_url = f"https://{GITHUB_TOKEN}@github.com/{REPO_NAME}.git"
local_dir = REPO_NAME.replace("/", "_")
shutil.rmtree(local_dir, ignore_errors=True)

# --- Clone repo and create branch ---
print("📥 Cloning repository...")
repo_local = Repo.clone_from(clone_url, local_dir)
git = repo_local.git
git.checkout(default_branch)
git.checkout('-b', BRANCH_NAME)

# --- Locate and modify manifest.yaml ---
manifest_path = None
for root, dirs, files in os.walk(local_dir):
    for file in files:
        if file.lower() == MANIFEST_FILENAME:
            manifest_path = os.path.join(root, file)
            break
    if manifest_path:
        break

if not manifest_path:
    raise Exception("❌ manifest.yaml not found in repo")

print(f"✏️ Editing: {manifest_path}")
with open(manifest_path, 'r') as f:
    data = yaml.safe_load(f) or {}

data['version'] = "v1.0.1"  # Add version if not present

with open(manifest_path, 'w') as f:
    yaml.dump(data, f, sort_keys=False)

# --- Commit and push changes ---
repo_local.git.add(A=True)
repo_local.git.config('--global', 'user.name', 'Automation Bot')
repo_local.git.config('--global', 'user.email', 'bot@example.com')
repo_local.index.commit(COMMIT_MESSAGE)
repo_local.git.push('--set-upstream', 'origin', BRANCH_NAME)

print(f"🚀 Pushed branch: {BRANCH_NAME}")

# --- Create Pull Request using PyGithub ---
pr = repo.create_pull(
    title=PR_TITLE,
    body=PR_BODY,
    head=BRANCH_NAME,
    base=default_branch
)

print(f"✅ Pull request created: {pr.html_url}")
