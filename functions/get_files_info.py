import os
import subprocess

def path_is_parent(parent_path: str, child_path: str):
    parent_path = os.path.abspath(parent_path)
    child_path = os.path.abspath(child_path)
    return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])

def get_files_info(working_directory: str, directory: str = "."):
    full_path = os.path.join(working_directory, directory)
    if not path_is_parent(working_directory, full_path):
        text = f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    elif not os.path.exists(full_path):
        text = f'Error: "{directory}" is not a directory'
    else:
        files = os.listdir(full_path)
        text =f"Result for '{directory if directory != '.' else 'current'} directory':"
        for file in files:
            file_path = os.path.join(full_path, file)
            size = os.path.getsize(file_path)
            text += f"\n - {file}: file_size={size} bytes, is_dir={os.path.isdir(file_path)}"
    print(text)
    return text


def get_file_content(working_directory: str, file_path: str):
    full_path = os.path.join(working_directory, file_path)
    if not path_is_parent(working_directory, full_path):
        text = f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        
    elif not os.path.isfile(full_path):
        text = f'Error: File not found or is not a regular file: "{file_path}"'
    else:
        try:
            with open(full_path, 'r') as f:
                content = f.read()
                if len(content) > 10000:
                    content = content[:10000] + f'[...File "{file_path}" truncated at 10000 characters]'
            text = f"Content of '{file_path}':\n{content}"
        except Exception as e:
            text = f"Error: reading file '{file_path}': {e}"
    print(text)
    return text


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


if __name__ == "__main__":

    print(os.getcwd())
    
    get_files_info("..", "blah")
    get_files_info("..", "calculator")
    get_files_info("calculator", ".")