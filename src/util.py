import sys
import logging
import os

def get_logger():
    logger = logging.getLogger()
    formatter = logging.Formatter("%(message)s")
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)
    return logger


def get_api_key():
    API_KEY = os.environ.get("OPENAI_API_KEY")
    if API_KEY is None:
        raise ValueError("You need to specify OPENAI_API_KEY environment variable!")
    return API_KEY

def get_git_creds():
    GIT_TOKEN = os.getenv("GIT_TOKEN")
    GITHUB_REPO = os.getenv("GITHUB_REPO")
    PR_NUMBER = os.getenv("PR_NUMBER")
    if GIT_TOKEN is None:
        raise ValueError("You need to specify GIT_TOKEN environment variable!")
    if GITHUB_REPO is None:
        raise ValueError("You need to specify GITHUB_REPO environment variable!")
    if PR_NUMBER is None:
        raise ValueError("You need to specify PR_NUMBER environment variable!")
    return GIT_TOKEN, GITHUB_REPO, PR_NUMBER

def get_changed_files():
    CHANGED_FILES = os.environ.get("CHANGED_FILES")
    if CHANGED_FILES is None:
        raise ValueError("You need to specify CHANGED_FILES environment variable!")
    if not CHANGED_FILES:
        return []
    changed_files_list = CHANGED_FILES.split(',')
    for file in changed_files_list:
        if not os.path.exists(file):
            raise ValueError(f"`{file}` not found. Please make sure all files exist.")
    return changed_files_list

