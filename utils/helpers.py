from utils import CheckStorageFile, CheckDataFile, VectorBuild

def ensure_vector_storage():
    storage_checker = CheckStorageFile()

    if not storage_checker.check_files():
        data_checker = CheckDataFile()
        if data_checker.has_valid_files():
            VectorBuild()
        else:
            raise FileNotFoundError("data フォルダに有効なファイル（.md / .txt / .pdf）が見つかりませんでした")
    # すでに storage ファイルが存在する場合はスキップ

