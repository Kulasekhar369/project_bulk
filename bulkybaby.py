import os
import shutil
import yaml
import pandas as pd
from datetime import datetime
from github import Github
from git import Repo

# -------------------- CONFIG --------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
CSV_FILE = "repos.csv"
MANIFEST_FILENAME = "manifest.yaml"
STACK_VALUE = "python"
# ------------------------------------------------

if not GITHUB_TOKEN:
    raise Exception("GITHUB_TOKEN is not set")

g = Github(base_url="https://api.github.com", login_or_token=GITHUB_TOKEN)
user = g.get_user()
print(f"Authenticated as: {user.login}")

df = pd.read_csv(CSV_FILE)

for index, row in df.iterrows():
    repo_url = row['repo_url'].strip()
    base_branch = row['branch'].strip()

    # Parse repo full name from URL
    if not repo_url.startswith("https://github.com/") or not repo_url.endswith(".git"):
        print(f"Skipping invalid repo URL: {repo_url}")
        continue

    repo_full_name = repo_url.replace("https://github.com/", "").replace(".git", "")
    branch_suffix = datetime.now().strftime("%Y%m%d%H%M%S")
    new_branch = f"update-stack-{branch_suffix}"
    local_dir = repo_full_name.replace("/", "_")
    clone_url_with_token = f"https://{GITHUB_TOKEN}@github.com/{repo_full_name}.git"

    try:
        shutil.rmtree(local_dir, ignore_errors=True)
        print(f"\nProcessing repo: {repo_full_name}")
        print("Cloning...")
        repo_local = Repo.clone_from(clone_url_with_token, local_dir)
        git = repo_local.git
        git.checkout(base_branch)
        git.checkout('-b', new_branch)

        # Locate manifest.yaml
        manifest_path = None
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                if file.lower() == MANIFEST_FILENAME:
                    manifest_path = os.path.join(root, file)
                    break
            if manifest_path:
                break

        if not manifest_path:
            print("manifest.yaml not found. Skipping.")
            continue

        # Modify or add stack field
        with open(manifest_path, 'r') as f:
            data = yaml.safe_load(f) or {}

        if 'stack' in data:
            print(f"Updating existing 'stack': {data['stack']} → {STACK_VALUE}")
        else:
            print("Adding new 'stack' key")

        data['stack'] = STACK_VALUE

        with open(manifest_path, 'w') as f:
            yaml.dump(data, f, sort_keys=False)

        # Commit and push
        git.add(A=True)
        git.config('--global', 'user.name', 'Automation Bot')
        git.config('--global', 'user.email', 'bot@example.com')
        repo_local.index.commit(f"Set 'stack' to '{STACK_VALUE}' in manifest.yaml")
        git.push('--set-upstream', 'origin', new_branch)
        print(f"Pushed branch: {new_branch}")

        # Create PR
        repo_obj = g.get_repo(repo_full_name)
        pr = repo_obj.create_pull(
            title=f"Update stack to {STACK_VALUE}",
            body=f"Setting stack to `{STACK_VALUE}` via automation",
            head=new_branch,
            base=base_branch
        )
        print(f"Pull request created: {pr.html_url}")

    except Exception as e:
        print(f"Error processing {repo_full_name}: {e}")
