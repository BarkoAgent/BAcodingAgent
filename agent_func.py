import os

driver = {}
run_test_id = ""


###############################################################################
# Below are your selenium-related functions
###############################################################################
def read_files(_run_test_id='1'):
    """
    Reads all the files from the root folder of the test repository and returns a list of file paths,
    skipping directories such as virtual environments, target folders, __pycache__, or any other
    directories that contain irrelevant information.
    """
    import os

    root_test_path = os.getenv("ROOT_TEST")
    if not root_test_path:
        raise EnvironmentError("The ROOT_TEST environment variable is not set.")

    # Define directories to ignore
    ignored_dirs = {"venv", "target", "__pycache__", ".git", "node_modules", "build"}

    # Define allowed file extensions
    allowed_extensions = {'.py', '.js', '.c', '.ts', '.java', '.md', '.txt', '.xml', '.css'}

    file_paths = []
    # Walk through the directory tree rooted at root_test_path
    for dirpath, dirnames, filenames in os.walk(root_test_path):
        # Modify dirnames in-place to skip ignored directories
        dirnames[:] = [d for d in dirnames if d not in ignored_dirs]
        for filename in filenames:
            # Check that the file has one of the allowed extensions
            _, ext = os.path.splitext(filename)
            if ext.lower() in allowed_extensions:
                file_paths.append(os.path.join(dirpath, filename))
    
    return file_paths


def read_specific_file(file, _run_test_id='1'):
    """
    Reads the specified file if it is located in the ROOT_TEST directory and has an allowed extension.
    Allowed extensions are: .py, .js, .c, .ts, .java, .md, .txt, .css or .xml.
    
    The file parameter has to be absolute path.
    The function raises an error if the file is not within the ROOT_TEST directory or if the extension is not allowed.
    
    Returns:
        a string text with the contents of the file.
    """
    root_test_path = os.getenv("ROOT_TEST")
    if not root_test_path:
        raise EnvironmentError("The ROOT_TEST environment variable is not set.")

    allowed_extensions = {'.py', '.js', '.c', '.ts', '.java', '.md', '.txt', '.xml', '.css'}

    # Resolve absolute paths
    abs_file = os.path.abspath(file)
    
    # Check that the file has one of the allowed extensions
    _, ext = os.path.splitext(abs_file)
    if ext.lower() not in allowed_extensions:
        raise ValueError("File extension is not allowed.")

    # Read and return the file content
    content = '```code\n'
    with open(abs_file, 'r', encoding='utf-8') as f:
        content += f.read()
    content += '\n```'
    return content
