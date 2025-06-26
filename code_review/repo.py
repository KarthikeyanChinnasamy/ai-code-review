import os
from typing import Iterable

import streamlit as st
from git import Repo
# from tempfile import mkdtemp
import shutil
from datetime import datetime


def list_code_files_in_repository(repo_url: str, extensions: list[str], password: str = None, branch: str = None) -> Iterable[str]:
    """Clone the GitHub repository and return a list of code files with the specified extensions."""
    # if password:
    #     # Modify the URL to include the password for authentication
    #     repo_url = repo_url.replace("https://", f"https://:@{password}")
     # Remove the directory if it already exists
    # if os.path.exists(local_path):
    #     print(f"Removing existing directory: {local_path}")
    #     shutil.rmtree(local_path)
    # print("local_path = repo_url.split")
    # print("\n")
    # local_path = repo_url.split("/")[-1]#.replace(".git", "")  # Derive the local path from the repo URL
    # print("remove the local_path if exists")
    # ensure_clean_directory(local_path)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    if password and branch:
        # print("repo_url, password, branch:")
        # print("\n")
        local_path = clone_github_repository(repo_url, timestamp, password, branch)
        # print("local_path_11:", [local_path]) 
        # print("value of repo_url, password, branch:")
        # print("\n")
    elif branch:
        # print("repo_url, password, branch:")
        # print("\n")
        local_path = clone_github_repository(repo_url, timestamp, branch)
        # print("local_path_12:", [local_path]) 
        # print("value of repo_url, password, branch:")
        # print("\n")
    elif password:
        # print("repo_url, password, branch:")
        # print("\n")
        local_path = clone_github_repository(repo_url, timestamp, password)
        # print("local_path_13:", [local_path]) 
        # print("value of repo_url, password, branch:")
        # print("\n")
    else:
        # print("repo_url, password:")
        # print("\n")
        local_path = clone_github_repository(repo_url, password)
        # print("local_path_14:", [local_path]) 
        # print("value of repo_url, password, branch:")
        # print("\n")

    # print("local_path_3: ")
    # print(local_path)
    # print("\n")
    # print("repo_url: ")
    # print(repo_url)
    # print("\n")
    return get_all_files_in_directory(local_path, extensions)



@st.cache_data(show_spinner=False)
def clone_github_repository(repo_url: str, timestamp, password: str = None, branch: str = None) -> str:
    """
    Clone a GitHub repository into a temporary local directory, switch to the specified branch,
    and pull the latest changes to ensure the branch's data is accurate.
    """
    # print("local_path = repo_url.split('/'')[-1].replace('.git', ''):")
    # print("\n")
    # base_local_path = repo_url.split("/")[-1].replace(".git", "")
    # # timestamp = int(datetime.utcnow().timestamp())
    # timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    # print("timestamp: ")
    # print(timestamp)
    # print("\n")
    # local_path = base_local_path if not branch else os.path.join(branch, timestamp, base_local_path)
    # print(f"Local path derived: {local_path}")

    if timestamp:
        # print("local_path = repo_url.split('/'')[-1].replace('.git', ''):")
        # print("\n")
        base_local_path = repo_url.split("/")[-1]#.replace(".git", "")
        # timestamp = int(datetime.utcnow().timestamp())
        # timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        # print("timestamp: ")
        # print(timestamp)
        # print("\n")
        branch_name = f"{branch}-{timestamp}"
        local_path = base_local_path if not branch else os.path.join(branch_name, base_local_path)
        # print(f"Local path derived: {local_path}")
    else:
        # print("valied 'local_path = repo_url.split'")
        # print("\n")
        local_path = repo_url.split("/")[-1]#.replace(".git", "")
        # print(f"Local path derived: {local_path}")

    # Ensure a clean directory before cloning
    if os.path.exists(local_path):
        print(f"Directory '{local_path}' already exists. Cleaning up...")
        shutil.rmtree(local_path)

    # Handle authentication
    if password:
        protocol, host_path = repo_url.split("://", 1)
        username, rest = host_path.split("@", 1)
        repo_url = f"{protocol}://{username}:{password}@{rest}"
        # print(f"Authenticated repo URL: {repo_url}")

    try:
        # Clone or reuse repository
        # print(f"Cloning repository into {local_path}")
        repo = Repo.clone_from(repo_url, local_path)

        # Fetch all branches to ensure updates
        repo.git.fetch("--all")
        # print(f"Fetched all branches for repository at {local_path}")

        # Checkout the specified branch
        if branch:
            # print(f"Switching to branch '{branch}'")
            # if branch not in repo.git.branch("-r"):
            #     raise ValueError(f"Branch '{branch}' not found in the remote repository.")
            # elif branch in os.path.exists(local_path):
            #     repo.git.checkout(branch, force=True)
            #     repo.git.reset("--hard", f"origin/{branch}")  # Reset branch to remote state
            # print(f"Switching to branch '{branch}'")
            remote_branches = repo.git.branch("-r")  # List all remote branches
            if f"origin/{branch}" not in remote_branches:
                raise ValueError(f"Branch '{branch}' not found in the remote repository.")
            else:
                repo.git.checkout(branch, force=True)
                repo.git.reset("--hard", f"origin/{branch}")
                # repo.git.pull()
        else:
            return {"message: No branch specified. Using the default branch."}

        # # Pull the latest changes
        repo.git.pull()
        # repo = Repo(local_path)
        # # Delete the local branch
        # repo.delete_head(branch, force=True)
        # local_path = f"{branch}/{local_path}"
        # print(f"Repository successfully cloned and updated at {local_path}")
        return local_path

    except Exception as e:
        print(f"Error during repository operations: {e}")
        raise

def get_all_files_in_directory(path: str, extensions: list[str]) -> list[str]:
    """Return a list of all files in a directory with the specified extension."""
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    # ensure_clean_directory(path)
    # print("files: ")
    # print(files)
    # print("\n")
    return files


def create_file_tree(code_files: Iterable[str]) -> list[dict[str, str]]:
    file_tree = []
    code_files = sorted(code_files)
    for file in code_files:
        parts = file.split(os.sep)
        current_level = file_tree
        for i, part in enumerate(parts):
            existing = [
                node for node in current_level if node["label"] == part
            ]
            if existing:
                current_level = existing[0].setdefault("children", [])
            else:
                new_node = {
                    "label": part,
                    "value": os.sep.join(parts[: i + 1]),
                }
                current_level.append(new_node)
                if i != len(parts) - 1:
                    current_level = new_node.setdefault("children", [])
    return file_tree

