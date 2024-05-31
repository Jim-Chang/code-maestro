from google.api_core import exceptions
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
                print("\nContent generation interrupted by user.")
                break

            print(chunk.text, end="")

            history[-1][1] = (history[-1][1] or "") + chunk.text
            yield history

        print("\nContent generation completed.")

    except exceptions.ResourceExhausted as e:
        print(f"Error: {e}")
        raise gr.Error("The model has run out of resources. Please try again later.")

    except Exception as e:
        print(f"Error: {e}")
        raise gr.Error("An error occurred while generating content.")


def _prepare_code_prompts():
    prompts = [
        "The original code documentation consists of several files. Each file's content is enclosed within code blocks, with the file path and name indicated at the beginning of each block. When referencing specific sections of the code, always include the file name and path to help users identify the source file accurately.",
        "When returning the code to the user, if it is necessary to mention the file path, please include the file path within the code block. Each section of the code should have the corresponding file path and name at the beginning of the code block for clarity.",
        "<Source Code Begin>",
        state["all_file_contents_prompt"],
        "<Source Code End>",
    ]

    if state["is_enable_diff"]:
        prompts.extend(
            [
                f"The diff content between the two branches `{state['diff_branch_1']}` and `{state['diff_branch_2']}` is as follows:",
                "<Diff Content Begin>",
                state["diff_content_prompt"],
                "<Diff Content End>",
            ]
        )

    return prompts


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
