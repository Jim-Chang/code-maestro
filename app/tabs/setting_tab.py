import gradio as gr

from app.utils import (
    read_settings,
    save_settings,
    clone_repo_with_branch,
    init_submodules,
    combine_code_base_and_upload_to_gemini,
    init_google_genai,
    state,
    update_state,
)

MODEL_OPTIONS = ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest"]
BRANCH_OPTIONS = ["default", "master", "main", "stage", "develop"]
FILE_EXTENSION_OPTIONS = ["py", "js", "ts", "tsx", "json"]


def layout():
    settings = read_settings()
    gr.Row(
        [
            _layout_model_setting(settings),
            _layout_repo_setting(settings),
        ]
    )


def _layout_model_setting(settings):
    gr.Markdown("# Model Setting")
    api_key = gr.Textbox(label="API Key", value=state["api_key"])

    model = gr.Dropdown(
        choices=MODEL_OPTIONS, label="Select a Model", value=state["model"]
    )
    temperature = gr.Slider(
        label="Temperature",
        minimum=0,
        maximum=1,
        value=state["temperature"],
        step=0.05,
    )

    progress_text = gr.Markdown()
    save_button = gr.Button("Save Settings")

    save_button.click(
        lambda: (gr.update(interactive=False), "Saving..."),
        [],
        [save_button, progress_text],
    ).then(
        _update_model_settings,
        [api_key, model, temperature],
        [],
    ).then(
        lambda: (gr.update(interactive=True), "Done!"),
        [],
        [save_button, progress_text],
    )


def _layout_repo_setting(settings):
    gr.Markdown("# Repository Setting")

    repo_url = gr.Dropdown(
        choices=settings.get("repo_url_options", []),
        label="Select a Repository",
        allow_custom_value=True,
        value=state["repo_url"],
    )
    branch = gr.Dropdown(
        choices=BRANCH_OPTIONS,
        value=state["branch"],
        label="Select a Branch",
    )
    file_extensions = gr.CheckboxGroup(
        choices=FILE_EXTENSION_OPTIONS,
        label="Select File Extensions for AI Model",
        value=state["file_extensions"],
    )

    progress_text = gr.Markdown()
    save_button = gr.Button("Use Repository For Chat")

    (
        save_button.click(
            lambda: (gr.update(interactive=False), "Clone Repo..."),
            [],
            [save_button, progress_text],
        )
        .then(
            _update_repo_settings,
            [repo_url, branch, file_extensions],
            [],
        )
        .then(
            clone_repo_with_branch,
            [repo_url, branch],
            [],
        )
        .then(
            lambda: "Init Submodules...",
            [],
            [progress_text],
        )
        .then(
            init_submodules,
            [],
            [],
        )
        .then(
            lambda: "Prepare for chat...",
            [],
            [progress_text],
        )
        .then(
            combine_code_base_and_upload_to_gemini,
            [file_extensions],
            [],
        )
        .then(
            lambda: (gr.update(interactive=True), "Done!"),
            [],
            [save_button, progress_text],
        )
    )


def _update_model_settings(api_key, model, temperature):
    data = {
        "api_key": api_key,
        "model": model,
        "temperature": temperature,
    }
    save_settings(data)
    update_state(data)
    init_google_genai()


def _update_repo_settings(repo_url, branch, file_extensions):
    if repo_url is None:
        print("repo_url is None")
        return

    data = {
        "repo_url": repo_url,
        "branch": branch,
        "file_extensions": file_extensions,
    }

    settings = read_settings()
    if "repo_url_options" not in settings:
        settings["repo_url_options"] = []

    if repo_url not in settings["repo_url_options"]:
        settings["repo_url_options"].append(repo_url)

    settings.update(data)
    save_settings(settings)

    update_state(data)
