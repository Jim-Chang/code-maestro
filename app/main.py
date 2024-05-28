import gradio as gr

from app.tabs.chat_tab import layout as layout_chat_tab
from app.tabs.setting_tab import layout as layout_setting_tab
from app.utils import init_state, init_google_genai

APP_CSS = """
#chatbot {
    height: calc(100vh - 300px) !important;
    overflow-y: auto !important;
}
"""


def main():
    init_state()
    init_google_genai()

    with gr.Blocks(css=APP_CSS) as app:
        app.title = "CodeMaestro"

        with gr.Tab("Chat"):
            layout_chat_tab()

        with gr.Tab("Settings"):
            layout_setting_tab()

        app.launch()


if __name__ == "__main__":
    main()
