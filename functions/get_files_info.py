from google.genai import types
import os
import subprocess

def path_is_parent(parent_path: str, child_path: str):
    parent_path = os.path.abspath(parent_path)
    child_path = os.path.abspath(child_path)
    return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])

def get_files_info(working_directory: str, directory: str = "."):
    full_path = os.path.join(working_directory, directory)
    if not path_is_parent(working_directory, full_path):
        print(f'Error: Cannot list "{directory}" as it is outside the permitted working directory')
    elif not os.path.exists(full_path):
        print(f'Error: "{directory}" is not a directory')
    else:
        files = os.listdir(full_path)
        print(f"Result for '{directory if directory != '.' else 'current'} directory':")
        for file in files:
            file_path = os.path.join(full_path, file)
            size = os.path.getsize(file_path)
            print(f" - {file}: file_size={size} bytes, is_dir={os.path.isdir(file_path)}")


def get_file_content(working_directory: str, file_path: str):
    full_path = os.path.join(working_directory, file_path)
    if not path_is_parent(working_directory, full_path):
        print(f'Error: Cannot read "{file_path}" as it is outside the permitted working directory')
    elif not os.path.isfile(full_path):
        print(f'Error: File not found or is not a regular file: "{file_path}"')
    else:
        try:
            with open(full_path, 'r') as f:
                content = f.read()
                if len(content) > 10000:
                    content = content[:10000] + f'[...File "{file_path}" truncated at 10000 characters]'
            print(f"Content of '{file_path}':\n{content}")
        except Exception as e:
            print(f"Error: reading file '{file_path}': {e}")


def write_file(working_directory: str, file_path: str, content) -> str:
    full_path = os.path.join(working_directory, file_path)
    status_string = ""
    if not path_is_parent(working_directory, full_path):
        status_string = f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    else:
        full_dir_path = "/".join(full_path.split("/")[:-1])
        if not os.path.exists(full_dir_path):
            os.makedirs(full_dir_path)
        with open(full_path, "w") as f:
            f.write(content)
        status_string = f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    return status_string


def run_python_file(working_directory: str, file_path: str, args=[]):
    full_path = os.path.join(working_directory, file_path)
    status_string = ""
    if not path_is_parent(working_directory, full_path):
        status_string = f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    elif not os.path.exists(full_path):
        status_string = f'Error: File "{file_path}" not found.'
    elif not file_path.endswith("py"):
        status_string = f'Error: "{file_path}" is not a Python file.'
    else:
        try:
            result = subprocess.run(args=["python3", full_path] + args, timeout=30, capture_output=True, text=True)
            if result.stdout:
                status_string += "STDOUT: " + result.stdout
            if result.stderr:
                status_string += "STDERR: " + result.stderr
            if not (result.stdout or result.stderr):
                status_string += "No output produced"

            if result.returncode != 0:
                if status_string:
                    status_string += '\n'
                status_string += f'Process exited with code {result.returncode}'

        except Exception as e:
            status_string = f"Error: executing Python file: {e}"
    return status_string

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    )
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Get file content in the specified directory for the specified file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to get content from.",
            ),
        },
    )
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a python file as a subprocess.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The python file to run.",
            ),
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to write to.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to write to the file.",
            ),
        },
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file
    ]
)

if __name__ == "__main__":

    print(os.getcwd())
    
    get_files_info("..", "blah")
    get_files_info("..", "calculator")
    get_files_info("calculator", ".")