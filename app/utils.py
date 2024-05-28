import json
import os
import pathlib
import shutil
import subprocess

import google.generativeai as genai
from git import Repo

SETTING_FILE = "settings.json"
REPO_DIR = "code_base"
PARENT_DIR = pathlib.Path(__file__).resolve().parent.parent

state = {
    "api_key": "",
    "model": "",
    "temperature": 0.3,
    "all_file_contents_prompt": None,
    "repo_url": "",
    "branch": "default",
    "file_extensions": [],
}


def init_state():
    global state
    settings = read_settings()

    update_state(
        {
            "api_key": settings.get("api_key", ""),
            "model": settings.get("model", ""),
            "temperature": settings.get("temperature", 0),
            "repo_url": settings.get("repo_url", ""),
            "branch": settings.get("branch", "default"),
            "file_extensions": settings.get("file_extensions", []),
        }
    )


def update_state(data):
    global state
    state.update(data)


def init_google_genai():
    if state["api_key"]:
        genai.configure(api_key=state["api_key"])


def read_settings():
    _ensure_settings()
    with open(SETTING_FILE, "r") as f:
        return json.loads(f.read())


def save_settings(data):
    old_setting = read_settings()
    old_setting.update(data)
    with open(SETTING_FILE, "w") as f:
        f.write(json.dumps(old_setting))


def _ensure_settings():
    if not os.path.exists(SETTING_FILE):
        with open(SETTING_FILE, "w") as f:
            f.write("{}")


def clone_repo_with_branch(repo_url, branch):
    target_dir = os.path.join(PARENT_DIR, REPO_DIR)

    if os.path.exists(target_dir):
        print("Removing existing repo...")
        shutil.rmtree(target_dir)

    print("Cloning repo...")
    repo = Repo.clone_from(repo_url, target_dir, depth=1)

    if branch != "default":
        print(f"Checking out to branch {branch}...")
        repo.git.checkout(branch)


def init_submodules():
    target_dir = os.path.join(PARENT_DIR, REPO_DIR)
    subprocess.run(
        ["git", "submodule", "update", "--init", "--depth", "1"], cwd=target_dir
    )
    print("Submodules initialized successfully!")


def combine_code_base_and_upload_to_gemini(file_extensions):
    print("Combining source code and uploading to Gemini...")
    print(file_extensions)
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
