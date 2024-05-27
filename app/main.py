import gradio as gr

from app.tabs.chat_tab import layout as layout_chat_tab
from app.tabs.setting_tab import layout as layout_setting_tab

APP_CSS = """
#chatbot {
    height: calc(100vh - 300px) !important;
    overflow-y: auto !important;
}
"""


def main():
    with gr.Blocks(css=APP_CSS) as app:
        with gr.Tab("Chat"):
            layout_chat_tab()

        with gr.Tab("Settings"):
            layout_setting_tab()

        app.launch()


if __name__ == "__main__":
    main()
