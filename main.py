import os
import sys
from dotenv import load_dotenv
from google import genai

from functions.get_files_info import *
from functions.function_calling import available_functions, call_function


load_dotenv(".env")
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""


def main():
    args = sys.argv[1:]
    if len(args) < 1:
        print("Usage: python main.py \"<prompt>\"")
        sys.exit(1)
    user_prompt = args[0]
    verbose = '--verbose' in args
    messages = [
        genai.types.Content(role="user", parts=[
                            genai.types.Part(text=user_prompt)]),
    ]
    count = 1
    while True:
        count += 1
        if count > 20:
            print(f"Maximum iterations ({20}) reached.")
            sys.exit(1)

        final_response = generate_content(client, messages, verbose)
        if final_response:
            print("Final response:")
            print(final_response)
            break


def generate_content(client, messages, verbose):
    resp = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=genai.types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt
        )
    )

    candidates = resp.candidates
    for candidate in candidates:
        messages.append(candidate.content)
        
    if not resp.function_calls:
        return resp.text

    function_responses = []
    for function_call_part in resp.function_calls:
        function_call_result = call_function(function_call_part, verbose)
        if (
            not function_call_result.parts
            or not function_call_result.parts[0].function_response
        ):
            raise Exception("empty function call result")
        if verbose:
            print(
                f"-> {function_call_result.parts[0].function_response.response}")
        function_responses.append(function_call_result.parts[0])

    if not function_responses:
        raise Exception("no function responses generated, exiting.")

    messages.append(genai.types.Content(role="tool", parts=function_responses))


if __name__ == "__main__":
    main()
