import gradio as gr

MODEL_OPTIONS = ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest"]
FILE_EXTENSION_OPTIONS = ["py", "js", "ts", "tsx", "json"]


def _update_settings(api_key, model, temperature):
    pass


def _layout_model_setting():
    gr.Markdown("# Model Setting")
    api_key = gr.Textbox(label="API Key")

    model = gr.Dropdown(choices=MODEL_OPTIONS, label="Select a Model")
    temperature = gr.Slider(
        label="Temperature",
        minimum=0,
        maximum=1,
        value=0.3,
        step=0.05,
    )

    save_button = gr.Button("Save Settings")

    save_button.click(
        _update_settings,
        [api_key, model, temperature],
        [],
    )


def _layout_repo_setting():
    gr.Markdown("# Repository Setting")

    repo_url_to_add = gr.Textbox(label="Add New Repository URL to Selector")
    add_repo_url_button = gr.Button("Add Repository URL")

    repo_url = gr.Dropdown(choices=[], label="Select a Repository")
    file_extensions = gr.CheckboxGroup(
        choices=FILE_EXTENSION_OPTIONS, label="Select File Extensions for AI Model"
    )
    upload_button = gr.Button("Use Repository For Chat")


def layout():
    gr.Row([_layout_model_setting(), _layout_repo_setting()])
