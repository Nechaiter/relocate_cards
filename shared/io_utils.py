import inspect
from pathlib import Path
import logging
from .. import flags
logger = logging.getLogger("aqt.mediasrv")
def _get_caller_directory():
    try:
        frame = inspect.stack()[2]
        caller_file = frame.filename
        return Path(caller_file).resolve().parent
    except Exception:
        return Path.cwd()

def load_file_to_string(path: str) -> str:
    path_obj = Path(path)
    
    if not path_obj.is_absolute():
        base_dir = _get_caller_directory()
        full_path = base_dir / path_obj
    else:
        full_path = path_obj

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        if flags.FLAGS["PRINT_DEBUG"]:
            logger.debug(f"Error loading file at {full_path}: {e}")
        return ""

def write_file(path: str, content: str) -> None:
    path_obj = Path(path)

    if not path_obj.is_absolute():
        base_dir = _get_caller_directory()
        full_path = base_dir / path_obj
    else:
        full_path = path_obj

    try:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        if flags.FLAGS["PRINT_DEBUG"]:
            logger.debug(f"File writed in {full_path}")
    except Exception as e:
        if flags.FLAGS["PRINT_DEBUG"]:
            logger.debug(f"Error writing file at {full_path}: {e}")