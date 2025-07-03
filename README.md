# Auto Feedback Example

This repository provides two primary scripts to automate code review feedback on GitHub Pull Requests using GitHub’s API and OpenAI’s GPT-4 and serves as a simple example of applying Retrieval-Augmented Generation (RAG) in practice.

1. **fetch_pr.py** – A helper script to list changed files in a given PR.
2. **generate_comment.py** – A bot that analyzes each changed file, generates actionable feedback via GPT-4, and (optionally) posts comments back to the PR.

**Note:** This project is based on the original code from https://github.com/DataExpert-io/auto-feedback-example

---

## Repository Structure

```
auto-feedback-example/
├── .env.example           # Template for environment variables
├── requirements.txt       # Project dependencies (version-pinned recommended)
├── src/
│   ├── settings.py        # Loads and validates configuration via Pydantic
│   ├── fetch_pr.py        # Script to list files changed in a PR
│   └── generate_comment.py# Reviews PR files and posts feedback
└── .github/
    └── workflows/
        └── autofeedback.yml # GitHub Actions workflow
```

---

## Prerequisites

- **Python 3.8+**
- **GitHub Personal Access Token (PAT)** with `Contents (read/write)` and `Pull requests (read/write)` scopes
- **OpenAI API Key** with access to GPT-4
- **Git** and basic CLI familiarity

---

## Local Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/charlysegovia/auto-feedback-example.git
   cd auto-feedback-example
   ```

2. **Create & activate a virtual environment**

   ```bash
   python -m venv .venv
   # macOS/Linux
   source .venv/bin/activate
   # Windows (PowerShell)
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   - Copy the template:

     ```bash
     cp .env.example .env
     ```

   - Edit `.env`, replace placeholders:

     ```ini
     git_token=ghp_your_real_github_pat
     openai_api_key=sk_your_real_openai_key
     github_repository=your-username/auto-feedback-example
     ```

   > **Do not commit** `.env` to version control.

5. **Verify config loader**

   ```bash
   cd src
   python -c "from settings import settings; print(settings)"
   ```

---

## fetch_pr.py

Lists changed files in a PR:

```bash
python src/fetch_pr.py <PR_NUMBER>
# Example:
python src/fetch_pr.py 42
```

---

## generate_comment.py

Retrieves each changed file, requests Issue/Fix feedback from GPT-4, and prints (or posts) comments.

### Dry-run

Prints intended comments without posting:

```bash
python src/generate_comment.py <PR_NUMBER>
```

### Live mode

1. Uncomment the `post_github_comment(...)` line in `generate_comment.py`.
2. Run the same command.

---

## GitHub Actions (optional)

The workflow file is named **autofeedback.yml** under `.github/workflows/`.

Include the following in `autofeedback.yml` to run on each PR:

```yaml
name: Auto Feedback CI
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    env:
      GIT_TOKEN: ${{ secrets.GIT_TOKEN }}
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      GITHUB_REPOSITORY: ${{ github.repository }}
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        run: |
          python -m venv .venv
          source .venv/bin/activate
          pip install -r requirements.txt
      - name: Run feedback bot
        run: python src/generate_comment.py ${{ github.event.pull_request.number }}
```

---

## Best Practices

- Keep `.env` out of source control (`.gitignore`).
- Pin dependencies in `requirements.txt`.
- Extend tests for coverage.
- Customize prompts in `generate_comment.py` to fit your coding standards.
