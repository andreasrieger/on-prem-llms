import os, git
from pypdf import PdfReader


# Function to get the Git root directory
def get_git_root():
    path = os.path.dirname(os.path.abspath(__file__))
    git_repo = git.Repo(path, search_parent_directories=True)
    return git_repo.git.rev_parse("--show-toplevel")


def get_download_folder():
    if os.name == 'nt':
        import ctypes
        from ctypes import windll, wintypes
        from uuid import UUID

        # ctypes GUID copied from MSDN sample code
        class GUID(ctypes.Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", wintypes.BYTE * 8)
            ]

            def __init__(self, uuidstr):
                uuid = UUID(uuidstr)
                ctypes.Structure.__init__(self)
                self.Data1, self.Data2, self.Data3, \
                    self.Data4[0], self.Data4[1], rest = uuid.fields
                for i in range(2, 8):
                    self.Data4[i] = rest>>(8-i-1)*8 & 0xff

        SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
        SHGetKnownFolderPath.argtypes = [
            ctypes.POINTER(GUID), wintypes.DWORD,
            wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)
        ]

        def _get_known_folder_path(uuidstr):
            pathptr = ctypes.c_wchar_p()
            guid = GUID(uuidstr)
            if SHGetKnownFolderPath(ctypes.byref(guid), 0, 0, ctypes.byref(pathptr)):
                raise ctypes.WinError()
            return pathptr.value

        FOLDERID_Download = '{374DE290-123F-4565-9164-39C4925E467B}'

        # def get_download_folder():
        return _get_known_folder_path(FOLDERID_Download)
    else:
        # def get_download_folder():
        home = os.path.expanduser("~")
        return os.path.join(home, "Downloads")


def get_file_list(input_dir, extensions=None) -> list:
    file_list = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if extensions is None or any(file.lower().endswith(ext.lower()) for ext in extensions):
                file_list.append(os.path.join(root, file))
    return file_list


def print_enumerated_list(lst):
    for idx, lst_elem in enumerate(lst):
        print(f"{idx + 1}. {lst_elem}")


def get_file_content(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def get_file_content_dict(filehandler) -> dict:
    file_content_dict = {}
    for page_num, page in enumerate(filehandler.pages):
        text = page.extract_text()
        file_content_dict[f"page_{page_num + 1}"] = text
    return file_content_dict


def get_pdf_contents(file) -> list:
    reader = PdfReader(file)
    contents = []
    for page_num, page in enumerate(reader.pages):
        contents.append(page.extract_text())
    return contents


def summarize_text_chunk(text_chunk: str, max_tokens: int = 100) -> str:
    # Placeholder for text summarization logic
    # In a real implementation, this could call an LLM or other summarization service
    summary = text_chunk[:max_tokens] + "..." if len(text_chunk) > max_tokens else text_chunk
    return summary


# Function to reorder DataFrame columns
def reorder_dataframe_columns(dataframe, cols_to_move):
    cols = list(dataframe.columns)
    for col in cols_to_move:
        if col in cols:
            cols.insert(cols_to_move.index(col), cols.pop(cols.index(col)))
    return dataframe[cols]
