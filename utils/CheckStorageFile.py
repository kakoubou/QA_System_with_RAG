from pathlib import Path

class CheckStorageFile:
    def __init__(self, storage_dir = "./storage"):
        self.storage_path = Path(storage_dir)
        self.document_file = self.storage_path / "document.json"
        self.vector_file = self.storage_path / "vectors.json"

    def check_files(self) -> bool:
        doc_exists = self.document_file.exists()
        vec_exists = self.vector_file.exists()

        if doc_exists and vec_exists:
            return True
        elif not doc_exists and not vec_exists:
            return False
        else:
            raise FileNotFoundError("ベクトルデータベースが不完全です：document.json と vectors.json の両方が存在している必要があります。")

# 使用例
if __name__ == "__main__":
    checker = CheckStorageFile()
    try:
        result = checker.check_files()
        print(result)  # True または False
    except FileNotFoundError as e:
        print(f"エラー：{e}")
