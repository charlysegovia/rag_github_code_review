# fetch_pr.py
# Purpose: Utility script to fetch and list changed files in a GitHub Pull Request.
# This script is a standalone helper and is NOT called by your main application logic.
# It can be kept in the codebase as a useful tool for developers to quickly verify GitHub integration.

import sys
from github import Github
from settings import settings


def main(pr_number: int):
    """
    Connects to GitHub using the PAT from settings and prints the filenames
    changed in the specified Pull Request.

    Args:
        pr_number (int): Pull Request number to inspect.
    """
    gh = Github(settings.git_token)
    repo = gh.get_repo(settings.github_repository)
    pr = repo.get_pull(pr_number)

    files = pr.get_files()
    print(f"PR #{pr_number} has {files.totalCount} changed files:")
    for f in files:
        print(" –", f.filename)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fetch_pr.py <PR_NUMBER>")
        sys.exit(1)
    main(int(sys.argv[1]))
