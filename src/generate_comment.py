# generate_comment.py
# Purpose: Bot to review PR files and post actionable suggestions only.
# Usage: python src/generate_comment.py <PR_NUMBER>

import sys
import os
import logging
import requests
from openai import OpenAI
from github import Github
from settings import settings

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(message)s", level=logging.INFO)

# Load settings
GIT_TOKEN = settings.git_token
GIT_REPO = settings.github_repository
OPENAI_API_KEY = settings.openai_api_key

if not OPENAI_API_KEY or not GIT_TOKEN:
    logger.error("Missing OPENAI_API_KEY or GIT_TOKEN in environment.")
    sys.exit(1)

# Initialize clients
client = OpenAI(api_key=OPENAI_API_KEY)
gh = Github(GIT_TOKEN)
repo = gh.get_repo(GIT_REPO)

# System prompt: enforce Issue/Fix format per file and header once
SYSTEM_PROMPT = (
    "You are a senior software engineer. "
    "For each file, return a section starting with '### filename', then bullet-list issues and fixes. "
    "Each item must use 'Issue: <description>' and 'Fix: <suggestion>' with dash '-' bullets. "
    "If there are no issues, list 'No issues found.' under the header."
)


def get_pr_files(pr_number: int) -> list[str]:
    pr = repo.get_pull(pr_number)
    return [f.filename for f in pr.get_files()]


def get_feedback(filename: str, content: str) -> str:
    """
    Ask the LLM to review file content and return items in Issue/Fix format, or
    'No issues found.' if none.
    """
    
    user_prompt = f"""
Review the file `{filename}`.
For each problem, output:
- Issue: <brief description>
  Fix: <precise fix>
Use dash '-' for bullets.
If there are no issues, output exactly:
No issues found.
```
{content}
```"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


def post_github_comment(git_token: str, repo_name: str, pr_number: int, comment: str, filename: str) -> None:
    url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {git_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {"body": comment}
    res = requests.post(url, headers=headers, json=data)
    if res.status_code != 201:
        logger.error(f"Failed to comment on {filename}: {res.status_code} {res.text}")
        raise Exception("GitHub comment failed")
    logger.info(f"📝 Commented on {filename}")


def main(pr_number: int) -> None:
    files = get_pr_files(pr_number)
    if not files:
        logger.info("No changed files to review.")
        return

    for filename in files:
        path = os.path.join(os.getcwd(), filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            logger.warning(f"File not found locally: {filename}, skipping.")
            continue

        logger.info(f"Reviewing {filename}...")
        feedback = get_feedback(filename, content)
        # Construct comment with header and Issue/Fix list
        file_path = os.path.join(os.getcwd(), filename)
        header = f"### {filename} — {file_path}"
        # Ensure header is printed once per file
        comment = header + "\n\n" + feedback

        # Dry-run print
        print(f"Would post to https://github.com/{GIT_REPO}/pull/{pr_number} for {filename}:")
        print(comment)
        # To enable live comments, uncomment below
        post_github_comment(GIT_TOKEN, GIT_REPO, pr_number, comment, filename)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/generate_comment.py <PR_NUMBER>")
        sys.exit(1)
    pr_number = int(sys.argv[1])
    main(pr_number)
