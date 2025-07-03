# fetch_pr.py
# Purpose: Utility script to fetch and list changed files in a GitHub Pull Request.
# Usage: python src/fetch_pr.py <PR_NUMBER>
# Example: python src/fetch_pr.py 42
# This script is a standalone helper and is NOT called by your main application logic.
# It can be kept in the codebase as a useful tool for developers to quickly verify GitHub integration.

import sys
import logging
from github import Github, BadCredentialsException, UnknownObjectException
from settings import settings

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(message)s", level=logging.INFO)

def main(pr_number: int):
    """
    Connects to GitHub using the PAT from settings and prints the filenames
    changed in the specified Pull Request.

    Args:
        pr_number (int): Pull Request number to inspect.
    """
    # Validate settings
    if not settings.git_token or not settings.github_repository:
        logger.error("GitHub token or repository not set in settings.")
        sys.exit(1)

    # Initialize GitHub client
    try:
        github_connection = Github(settings.git_token)
    except BadCredentialsException:
        logger.error("Invalid GitHub token.")
        sys.exit(1)

    # Validate repository
    try:
        repo = github_connection.get_repo(settings.github_repository)
    except UnknownObjectException:
        logger.error(f"Repository '{settings.github_repository}' not found or inaccessible.")
        sys.exit(1)

    # Validate PR existence
    try:
        pr = repo.get_pull(pr_number)
    except UnknownObjectException:
        logger.error(f"Pull Request #{pr_number} not found or inaccessible.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error fetching PR #{pr_number}: {e}")
        sys.exit(1)

    # Fetch files
    try:
        files = pr.get_files()
    except Exception as e:
        logger.error(f"Error fetching files for PR #{pr_number}: {e}")
        sys.exit(1)

    # Output changed files
    logger.info(f"PR #{pr_number} has {files.totalCount} changed files:")
    for f in files:
        logger.info(f"- {f.filename}")

if __name__ == "__main__":
    # Validate CLI args
    if len(sys.argv) != 2:
        logger.error("Usage: python fetch_pr.py <PR_NUMBER>")
        sys.exit(1)
    # Validate PR number is positive integer
    try:
        pr_number = int(sys.argv[1])
        if pr_number <= 0:
            raise ValueError
    except ValueError:
        logger.error("PR number must be a positive integer.")
        sys.exit(1)

    main(pr_number)
