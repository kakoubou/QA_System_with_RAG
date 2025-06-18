from pathlib import Path

class CheckDataFile:
    def __init__(self, data_dir = "./data"):
        self.data_path = data_dir

    def has_valid_files(self) -> bool:
        valid_extensions = {'.md', '.txt', '.pdf'}

        # パスが存在し、かつディレクトリであるか確認
        if not self.data_path.exists():
            raise FileNotFoundError(f"パスが存在しません：{self.data_path}")
        if not self.data_path.is_dir():
            raise NotADirectoryError(f"パスはディレクトリではありません：{self.data_path}")

        # 条件に合うファイルが存在するか確認
        for file in self.data_path.iterdir():
            if file.is_file() and file.suffix.lower() in valid_extensions:
                return True

        # 条件に合うファイルが見つからなかった場合
        raise FileNotFoundError(f"{self.data_path} に .md/.txt/.pdf ファイルが見つかりませんでした")

    def __str__(self):
        return f"CheckDataFile(data_path='{self.data_path}')"


# 使用例
if __name__ == "__main__":
    try:
        checker = CheckDataFile()
        result = checker.has_valid_files()
        print("有効なファイルがあります：", result)
    except Exception as e:
        print("チェックに失敗しました：", e)
