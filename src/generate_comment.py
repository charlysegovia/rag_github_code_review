import os
import sys
import requests
import logging
from openai import OpenAI
from github import Github
from settings import settings


logger = logging.getLogger()
formatter = logging.Formatter("%(message)s")
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

GIT_TOKEN = settings.git_token
GIT_REPO = settings.github_repository
OPENAI_API_KEY = settings.openai_api_key

if OPENAI_API_KEY is None:
    raise ValueError("You need to specify OPENAI_API_KEY environment variable!")

client = OpenAI(api_key=OPENAI_API_KEY)
# top of file, after you set up your OpenAI client
gh = Github(GIT_TOKEN)
repo = gh.get_repo(GIT_REPO)

def get_pr_files(pr_number):
    pr = repo.get_pull(pr_number)
    files = pr.get_files()
    changes = [f.filename for f in files]
    return changes


def get_feedback(filename: str, system_prompt: str, user_prompt: str) -> str:
  comment = ''
  response = client.chat.completions.create(
      model="gpt-4",
      messages=[
          {"role": "system", "content": system_prompt},
          {"role": "user", "content": user_prompt},
      ],
      temperature=0,
  )
  comment = response.choices[0].message.content
  text = f"This is a LLM-generated comment for `{filename}`: \n{comment if comment else 'Tests passed. No feedback generated for testing purposes.'}"
  return text


def post_github_comment(git_token, repo, pr_number, comment, filename):
  url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
  headers = {
      "Accept": "application/vnd.github+json",
      "Authorization": f"Bearer {git_token}",
      "X-GitHub-Api-Version": "2022-11-28"
  }
  data = {"body": comment}
  response = requests.post(url, headers=headers, json=data)
  if response.status_code != 201:
    logger.error(f"Failed to create comment. Status code: {response.status_code} \n{response.text}")
    raise Exception(f"Failed to create comment. Status code: {response.status_code} \n{response.text}")
  logger.info(f"✅ Added review comment for {filename} at https://github.com/{repo}/pull/{pr_number}")


def main(files_to_process: list):
  if not files_to_process:
    logger.warning('No file changes were detected in the current push so no comments were generated. Please modify one or more of your submission files to receive LLM-generated feedback.')
    return None
  local_solutions_dir = os.path.join(os.getcwd(), 'src')
  os.makedirs(local_solutions_dir, exist_ok=True)
  system_prompt = """
    You are a senior software engineer looking to give feedback on every PR you see in this repo
  
  """

  for filename in files_to_process:
    logger.info("processing:" +filename)
    try:
        with open(filename, 'r') as file:
            content = file.read()
            print(content)
            prompt = f"Make sure this file {filename} with this content: {content} follows all the right naming and python conventions. Make any call outs you see!"
            comment = get_feedback(filename, system_prompt, prompt)
            if GIT_TOKEN and GIT_REPO and pr_number:
              # (dry-run) show us what we’d send
              print(f"Would post to https://github.com/{GIT_REPO}/pull/{pr_number}:")
              # print(comment)            
              post_github_comment(GIT_TOKEN, GIT_REPO, pr_number, comment, filename)

    except Exception as e:
        print(e)


if __name__ == "__main__":
  pr_number = int(sys.argv[1])
  changes = get_pr_files(pr_number)
  main(changes)
