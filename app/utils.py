import json
import os
import pathlib
import shutil

from git import Repo

SETTING_FILE = "settings.json"
REPO_DIR = "code_base"
PARENT_DIR = pathlib.Path(__file__).resolve().parent.parent

state = {
    "api_key": "",
    "model": "",
    "temperature": 0,
    "all_file_contents": "",
}


def init_state():
    global state
    settings = read_settings()
    set_model_settings_to_state(
        settings.get("api_key", ""),
        settings.get("model", ""),
        settings.get("temperature", 0),
    )


def set_model_settings_to_state(api_key, model, temperature):
    global state
    state["api_key"] = api_key
    state["model"] = model
    state["temperature"] = temperature


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


def clone_repo(repo_url, branch):
    target_dir = os.path.join(PARENT_DIR, REPO_DIR)

    if os.path.exists(target_dir):
        print("Removing existing repo...")
        shutil.rmtree(target_dir)

    print("Cloning repo...")
    repo = Repo.clone_from(repo_url, target_dir, depth=1)

    if branch != "default":
        print(f"Checking out to branch {branch}...")
        repo.git.checkout(branch)

    print("Initializing submodules...")
    repo.git.submodule("init")
    repo.git.submodule("update")
    repo.git.pull()

    print("Repo cloned successfully!")
