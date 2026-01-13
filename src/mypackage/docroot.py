import os, git

_git_root, _input_dir, _output_dir, _data_dir = None, None, None, None

# Root directory of the package
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Function to get the Git root directory
def get_git_root(path=ROOT_DIR):
    global _git_root
    if _git_root is None:
        git_repo = git.Repo(path, search_parent_directories=True)
        git_root = git_repo.git.rev_parse("--show-toplevel")
        _git_root = git_root
    return _git_root


def get_input_dir():
    global _input_dir
    if _input_dir is None:
        _input_dir = os.path.join(get_git_root(), "input")
    return _input_dir


def get_output_dir():
    global _output_dir
    if _output_dir is None:
        _output_dir = os.path.join(get_git_root(), "output")
    return _output_dir


def get_data_dir():
    global _data_dir
    if _data_dir is None:
        _data_dir = os.path.join(get_git_root(), "data")
    return _data_dir
