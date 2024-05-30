import google.generativeai as genai
import gradio as gr

from app.utils import state

_is_interrupted = False


def layout():
    gr.Markdown("# CodeMaestro")

    chatbot = gr.Chatbot(elem_id="chatbot", show_label=False)

    message = gr.Textbox(placeholder="Type your message here...", show_label=False)

    with gr.Row():
        with gr.Column(1):
            clear_btn = gr.ClearButton([chatbot, message])
        with gr.Column(1):
            interrupt_btn = gr.Button("Stop", interactive=False)

    (
        message.submit(
            _on_submit_message,
            [message, chatbot],
            [message, chatbot, interrupt_btn],
            queue=False,
        )
        .success(lambda: [_disable(), _disable()], [], [message, clear_btn])
        .then(
            _streaming_llm_response,
            [chatbot],
            chatbot,
        )
        .then(
            lambda: [_enable(), _enable(), _disable()],
            [],
            [message, clear_btn, interrupt_btn],
        )
    )

    interrupt_btn.click(_on_click_interrupt, [], [interrupt_btn])


def _disable():
    return gr.update(interactive=False)


def _enable():
    return gr.update(interactive=True)


def _on_click_interrupt():
    global _is_interrupted
    _is_interrupted = True
    return _disable()


def _on_submit_message(user_input, history):
    history = history or []

    if state["all_file_contents_prompt"] is None:
        raise gr.Error("Please select a repository first.")

    history.append((user_input, None))
    return "", history, _enable()


def _streaming_llm_response(history):
    global _is_interrupted

    model = _prepare_model()

    user_input, _ = history[-1]
    code_prompts = _prepare_code_prompts()

    message_history = []
    for user_msg, ai_msg in history[:-1]:
        message_history.append(f"user: {user_msg}")
        message_history.append(f"ai: {ai_msg}")

    prompt_parts = [
        *code_prompts,
        *message_history,
        f"user:\n{user_input}",
    ]

    print(f"User input: {user_input}")
    print("Start generating content...")

    try:
        response = model.generate_content(prompt_parts, stream=True)
        print("AI: ", end="")

        for chunk in response:
            if _is_interrupted:
                _is_interrupted = False
                break

            print(chunk.text, end="")

            history[-1][1] = (history[-1][1] or "") + chunk.text
            yield history

        print("\nContent generation completed.")

    except Exception as e:
        print(f"Error: {e}")
        raise gr.Error("An error occurred while generating content.")


def _prepare_code_prompts():
    return [
        "程式碼是由多個檔案組成，每份檔案的內容由 code block 包夾，每個 code block 起始處前一行會提供該檔案的路徑與檔名，回覆時若需提及程式碼所處原始檔位置，請務必依照檔案對應的檔名提供給使用者",
        "## Source Code Begin ##",
        state["all_file_contents_prompt"],
        "## Source Code End ##",
        "回傳結果給使用者時，避免將檔案路徑寫於 code block 中，以免造成使用者無法正確閱讀",
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
