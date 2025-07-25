import os
import sys
from dotenv import load_dotenv
from google import genai

from functions.get_files_info import *


load_dotenv(".env")
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""



def main():
    args = sys.argv[1:]
    if len(args) < 1:
        print("Usage: python main.py \"<prompt>\"")
        sys.exit(1)
    user_prompt = args[0]
    messages = [
        genai.types.Content(role="user", parts=[genai.types.Part(text=user_prompt)]),
    ]   

    resp = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=genai.types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt)
    )
    if resp.function_calls:
        for function_call_part in resp.function_calls:
            print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(resp.text)
    
    if "--verbose" in args:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {resp.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {resp.usage_metadata.candidates_token_count}")


if __name__ == "__main__":
    main()
