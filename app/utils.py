import json
import os
import pathlib
import shutil
import subprocess

import google.generativeai as genai
from git import Repo

STATE_FILE = "state.json"
REPO_DIR = "code_base"
PARENT_DIR = pathlib.Path(__file__).resolve().parent.parent

state = {
    "api_key": "",
    "model": "gemini-1.5-pro-latest",
    "temperature": 0.3,
    "all_file_contents_prompt": None,
    "repo_url": "",
    "repo_url_options": [],
    "branch": "default",
    "file_extensions": [],
}


def load_state():
    global state
    if os.path.exists(os.path.join(PARENT_DIR, STATE_FILE)):
        with open(os.path.join(PARENT_DIR, STATE_FILE), "r") as f:
            try:
                data = json.loads(f.read())
                state.update(data)
            except json.JSONDecodeError:
                pass


def save_state():
    with open(STATE_FILE, "w") as f:
        data = state.copy()
        del data["all_file_contents_prompt"]
        f.write(json.dumps(data, indent=4))


def update_state(data):
    global state
    state.update(data)
    save_state()


def init_google_genai():
    if state["api_key"]:
        genai.configure(api_key=state["api_key"])


def clone_repo_with_branch(repo_url, branch):
    target_dir = os.path.join(PARENT_DIR, REPO_DIR)

    if os.path.exists(target_dir):
        print("Removing existing repo...")
        shutil.rmtree(target_dir)

    print(f"Cloning repo with branch {branch}...")
    if branch != "default":
        Repo.clone_from(repo_url, target_dir, depth=1, branch=branch)
    else:
        Repo.clone_from(repo_url, target_dir, depth=1)


def init_submodules():
    target_dir = os.path.join(PARENT_DIR, REPO_DIR)
    subprocess.run(
        ["git", "submodule", "update", "--init", "--depth", "1"], cwd=target_dir
    )
    print("Submodules initialized successfully!")


def combine_code_base_and_upload_to_gemini(file_extensions):
    print("Combining source code and uploading to Gemini...")
    target_dir = os.path.join(PARENT_DIR, REPO_DIR)

    all_file_contents = ""

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                relative_file_path = os.path.relpath(file_path, target_dir)

                with open(file_path, "r") as f:
                    file_content = f.read()

                all_file_contents += f"# Source File Path: {relative_file_path}\n"
                all_file_contents += "```\n"
                all_file_contents += file_content
                all_file_contents += "\n```\n"

    with open(os.path.join(target_dir, "all_file_contents.txt"), "w") as f:
        f.write(all_file_contents)

    all_file_contents_prompt = genai.upload_file(
        os.path.join(target_dir, "all_file_contents.txt")
    )
    state["all_file_contents_prompt"] = all_file_contents_prompt
    print("Source code uploaded to Gemini successfully!")
