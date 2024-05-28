import google.generativeai as genai
import gradio as gr

from app.utils import state


def layout():
    gr.Markdown("# CodeMaestro")

    chatbot = gr.Chatbot(elem_id="chatbot", show_label=False)

    message = gr.Textbox(placeholder="Type your message here...", show_label=False)
    clear_history = gr.Button("Clear Chat History")

    (
        message.submit(
            _on_submit_message, [message, chatbot], [message, chatbot], queue=False
        )
        .success(lambda: [_disable(), _disable()], [], [message, clear_history])
        .then(
            _streaming_llm_response,
            [message, chatbot],
            chatbot,
        )
        .then(lambda: [_enable(), _enable()], [], [message, clear_history])
    )

    clear_history.click(_on_clear_history, [], [chatbot])


def _disable():
    return gr.update(interactive=False)


def _enable():
    return gr.update(interactive=True)


def _on_clear_history():
    return []


def _on_submit_message(user_input, history):
    history = history or []

    if state["all_file_contents_prompt"] is None:
        raise gr.Error("Please select a repository first.")

    history.append((user_input, None))
    return "", history


def _streaming_llm_response(user_input, history):
    code_prompts = _prepare_code_prompts()

    model = _prepare_model()

    message_history = []
    for user_msg, ai_msg in history:
        message_history.append(f"user: {user_msg}")
        message_history.append(f"ai: {ai_msg}")

    prompt_parts = [
        *code_prompts,
        *message_history,
        f"user:\n{user_input}",
    ]

    print("Start generating content...")
    response = model.generate_content(prompt_parts, stream=True)
    for chunk in response:
        history[-1][1] = (history[-1][1] or "") + chunk.text
        yield history


def _prepare_code_prompts():
    return [
        "程式碼是由多個檔案組成，每份檔案的內容由 code block 包夾，每個 code block 起始處前一行會提供該檔案的路徑與檔名，回覆時請務必依照檔案對應的檔名提供給使用者",
        "## Source Code Begin ##",
        state["all_file_contents_prompt"],
        "## Source Code End ##",
    ]


def _prepare_model():
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
        system_instruction=state["system_message"],
    )
