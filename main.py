import os
import sys
from dotenv import load_dotenv
from google import genai


load_dotenv(".env")
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)



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
        contents=messages
    )
    print(resp.text)
    
    if "--verbose" in args:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {resp.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {resp.usage_metadata.candidates_token_count}")


if __name__ == "__main__":
    main()
