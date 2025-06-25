import os
from werkzeug.utils import secure_filename

def save_file(file, subfolder):
    """
    Sauvegarde un FileStorage dans `subfolder`.
    Renvoie (filename, full_path).
    """
    filename = secure_filename(file.filename)
    os.makedirs(subfolder, exist_ok=True)
    dst = os.path.join(subfolder, filename)
    file.save(dst)
    return filename, dst
