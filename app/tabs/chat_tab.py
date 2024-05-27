import gradio as gr


def chat_with_gpt(prompt):
    return "#hello"


def submit_message(history, user_input):
    history = history or []
    response = chat_with_gpt(user_input)
    history.append((user_input, response))
    return history, ""


def layout():
    gr.Markdown("# CodeMaestro")
    chatbot = gr.Chatbot(elem_id="chatbot", show_label=False)

    message = gr.Textbox(placeholder="Type your message here...", show_label=False)

    message.submit(submit_message, [chatbot, message], [chatbot, message])
