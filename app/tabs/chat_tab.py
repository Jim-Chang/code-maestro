import google.generativeai as genai
import gradio as gr

from app.utils import state


def layout():
    gr.Markdown("# CodeMaestro")
    chatbot = gr.Chatbot(elem_id="chatbot", show_label=False)
    message = gr.Textbox(placeholder="Type your message here...", show_label=False)

    message.submit(submit_message, [message, chatbot], [message, chatbot]).then()


def submit_message(user_input, history):
    history = history or []
    response = get_llm_response(user_input, history)

    history.append((user_input, response))
    return "", history


def get_llm_response(user_input, history):
    system_message = _prepare_system_message()
    code_prompts = _prepare_code_prompts()

    model = _prepare_model(system_message)

    message_history = []
    for user_msg, ai_msg in history:
        message_history.append(f"user: {user_msg}")
        message_history.append(f"ai: {ai_msg}")

    prompt_parts = [
        *code_prompts,
        *message_history,
        f"user:\n{user_input}",
    ]

    response = model.generate_content(prompt_parts)
    return response.text


def _prepare_system_message():
    return "你是一個資深的軟體工程師，精通 typescript, javascript, python，依照提供的程式碼，解答使用者的問題"


def _prepare_code_prompts():
    return [
        "程式碼是由多個檔案組成，每份檔案的內容由 code block 包夾，每個 code block 起始處前一行會提供該檔案的路徑與檔名，回覆時請務必依照檔案對應的檔名提供給使用者",
        "## Source Code Begin ##",
        state["all_file_contents_prompt"],
        "## Source Code End ##",
    ]


def _prepare_model(system_message):
    generation_config = {
        "temperature": state["temperature"],
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 8192,
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    return genai.GenerativeModel(
        model_name=state["model"],
        generation_config=generation_config,
        safety_settings=safety_settings,
        system_instruction=system_message,
    )
