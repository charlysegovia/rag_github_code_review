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
t_logger = logging.getLogger(__name__)
logging.basicConfig(format="%(message)s", level=logging.INFO)

# Load settings
GIT_TOKEN = settings.git_token
GIT_REPO = settings.github_repository
OPENAI_API_KEY = settings.openai_api_key

if not OPENAI_API_KEY or not GIT_TOKEN:
    t_logger.error("Missing OPENAI_API_KEY or GIT_TOKEN in environment.")
    sys.exit(1)

# Initialize clients
client = OpenAI(api_key=OPENAI_API_KEY)
gh = Github(GIT_TOKEN)
repo = gh.get_repo(GIT_REPO)

# System prompt focuses on actionable corrections only
SYSTEM_PROMPT = (
    "You are a senior software engineer. "
    "Provide only concise, actionable suggestions for code improvements. "
    "Do not mention what is already correct or offer praise. "
    "List each issue and its fix clearly."
)


def get_pr_files(pr_number: int) -> list[str]:
    pr = repo.get_pull(pr_number)
    return [f.filename for f in pr.get_files()]


def get_feedback(filename: str, content: str) -> str:
    """
    Ask the LLM to review file content and return only corrections.
    """
    # Use a triple-quoted f-string to include newlines and backticks properly
    user_prompt = f"""
Review the following file `{filename}` and list only the issues along with precise fixes.
Respond in bullet form. Do not mention correct parts.
```
{content}
```
"""
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
        t_logger.error(f"Failed to comment on {filename}: {res.status_code} {res.text}")
        raise Exception("GitHub comment failed")
    t_logger.info(f"📝 Commented on {filename}")


def main(pr_number: int) -> None:
    files = get_pr_files(pr_number)
    if not files:
        t_logger.info("No changed files to review.")
        return

    for filename in files:
        # read file content
        path = os.path.join(os.getcwd(), filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            t_logger.warning(f"File not found locally: {filename}, skipping.")
            continue

        t_logger.info(f"Reviewing {filename}...")
        comment = get_feedback(filename, content)
        # Dry-run print
        print(f"Would post to https://github.com/{GIT_REPO}/pull/{pr_number} for {filename}:")
        print(comment)
        # To enable live comments, uncomment below
        # post_github_comment(GIT_TOKEN, GIT_REPO, pr_number, comment, filename)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/generate_comment.py <PR_NUMBER>")
        sys.exit(1)
    main(int(sys.argv[1]))
