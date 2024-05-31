import gradio as gr

from app.utils import (
    clone_repo_with_branch,
    init_submodules,
    combine_code_base_and_upload_to_gemini,
    init_google_genai,
    state,
    update_state,
    unshallow_repo,
    prepare_diff_content_and_upload_to_gemini,
    fetch_branch,
)

MODEL_OPTIONS = ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest"]
BRANCH_OPTIONS = ["default", "master", "main", "stage", "develop"]
FILE_EXTENSION_OPTIONS = ["py", "js", "ts", "tsx", "json"]


def layout():
    _layout_model_setting()
    _layout_repo_setting()
    _layout_diff_setting()


def _layout_model_setting():
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
    system_message = gr.Textbox(
        label="System Message",
        value=state["system_message"],
    )

    progress_text = gr.Markdown()
    save_button = gr.Button("Save Settings")

    save_button.click(
        _on_click_model_settings,
        [api_key, model, temperature, system_message],
        [progress_text],
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
        allow_custom_value=True,
        label="Select a Branch",
    )
    file_extensions = gr.CheckboxGroup(
        choices=FILE_EXTENSION_OPTIONS,
        label="Select File Extensions for AI Model",
        value=state["file_extensions"],
    )

    progress_text = gr.Markdown()
    save_button = gr.Button("Use Repository For Chat")

    save_button.click(
        _on_click_save_repo_handler,
        [repo_url, branch, file_extensions],
        [progress_text],
    )


def _layout_diff_setting():
    gr.Markdown("# Diff Setting")
    is_enable = gr.Checkbox(label="Enable Diff", value=state["is_enable_diff"])

    branch_1 = gr.Dropdown(
        choices=BRANCH_OPTIONS,
        allow_custom_value=True,
        interactive=state["is_enable_diff"],
        label="Select a Branch For Diff",
        value=state["diff_branch_1"],
    )

    branch_2 = gr.Dropdown(
        choices=BRANCH_OPTIONS,
        allow_custom_value=True,
        interactive=state["is_enable_diff"],
        label="Select a Branch For Diff",
        value=state["diff_branch_2"],
    )

    progress_text = gr.Markdown()
    save_button = gr.Button(
        "Save Diff Setting",
        interactive=state["is_enable_diff"],
    )

    is_enable.change(
        _on_change_enable_diff_handler,
        [is_enable],
        [branch_1, branch_2, save_button],
    )
    save_button.click(
        _on_click_save_diff_handler,
        [branch_1, branch_2],
        [progress_text],
    )


def _on_click_model_settings(api_key, model, temperature, system_message):
    if not api_key:
        raise gr.Error("API Key is required!")

    if not system_message:
        raise gr.Error("System Message is required!")

    data = {
        "api_key": api_key,
        "model": model,
        "temperature": temperature,
        "system_message": system_message,
    }
    update_state(data)
    init_google_genai()
    return "Done!"


def _on_click_save_repo_handler(repo_url, branch, file_extensions):
    if not repo_url:
        raise gr.Error("Repository URL is required!")

    if not branch:
        raise gr.Error("Branch is required!")

    if not file_extensions:
        raise gr.Error("File Extensions is required!")

    _update_repo_settings(repo_url, branch, file_extensions)
    clone_repo_with_branch(repo_url, branch)
    init_submodules()
    combine_code_base_and_upload_to_gemini(file_extensions)
    return "Done!"


def _on_change_enable_diff_handler(is_enable):
    update_state({"is_enable_diff": is_enable})
    return (
        gr.update(interactive=is_enable),
        gr.update(interactive=is_enable),
        gr.update(interactive=is_enable),
    )


def _on_click_save_diff_handler(branch_1, branch_2):
    if not branch_1:
        raise gr.Error("Branch 1 is required!")

    if not branch_2:
        raise gr.Error("Branch 2 is required!")

    if not state["all_file_contents_prompt"]:
        raise gr.Error("Please select a repository first.")

    _update_diff_settings(branch_1, branch_2)

    unshallow_repo()
    fetch_branch(branch_1)
    fetch_branch(branch_2)
    prepare_diff_content_and_upload_to_gemini(branch_1, branch_2)

    return "Done!"


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


def _update_diff_settings(branch_1, branch_2):
    data = {
        "diff_branch_1": branch_1,
        "diff_branch_2": branch_2,
    }
    update_state(data)
