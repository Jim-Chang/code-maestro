import gradio as gr

from app.utils import (
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
    gr.Row(
        [
            _layout_model_setting(),
            _layout_repo_setting(),
        ]
    )


def _layout_model_setting():
    print("_layout_model_setting", state)
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


def _layout_repo_setting():
    gr.Markdown("# Repository Setting")

    repo_url = gr.Dropdown(
        choices=state.get("repo_url_options", []),
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
    update_state(data)
    init_google_genai()


def _update_repo_settings(repo_url, branch, file_extensions):
    data = {
        "branch": branch,
        "file_extensions": file_extensions,
    }

    if repo_url:
        data["repo_url"] = repo_url

        if repo_url not in state["repo_url_options"]:
            state["repo_url_options"].append(repo_url)

    update_state(data)
