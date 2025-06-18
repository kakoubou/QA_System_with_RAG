import os
from typing import Dict, List, Optional, Tuple, Union

import PyPDF2
import markdown
import html2text
import json
from tqdm import tqdm
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")


class ReadFiles:
    """
    ファイルを読み込むクラス
    """

    def __init__(self, path: str) -> None:
        self._path = path
        self.file_list = self.get_files()

    def get_files(self):
        # 引数: dir_path は対象フォルダのパス
        file_list = []
        for filepath, dirnames, filenames in os.walk(self._path):
            # os.walk 関数で指定されたフォルダを再帰的に探索
            for filename in filenames:
                # 拡張子によって対象ファイルかを判断
                if filename.endswith(".md"):
                    # 対象であれば絶対パスをリストに追加
                    file_list.append(os.path.join(filepath, filename))
                elif filename.endswith(".txt"):
                    file_list.append(os.path.join(filepath, filename))
                elif filename.endswith(".pdf"):
                    file_list.append(os.path.join(filepath, filename))
        return file_list

    def get_content(self, max_token_len: int = 600, cover_content: int = 150):
        docs = []
        # ファイルの内容を読み込む
        for file in self.file_list:
            content = self.read_file_content(file)
            chunk_content = self.get_chunk(
                content, max_token_len=max_token_len, cover_content=cover_content)
            docs.extend(chunk_content)
        return docs

    @classmethod
    def get_chunk(cls, text: str, max_token_len: int = 600, cover_content: int = 150):
        chunk_text = []

        curr_len = 0
        curr_chunk = ''

        lines = text.split('\n')  # 改行でテキストを行に分割

        for line in lines:
            line = line.replace(' ', '')
            line_len = len(enc.encode(line))
            if line_len > max_token_len:
                print('警告 line_len = ', line_len)
            if curr_len + line_len <= max_token_len:
                curr_chunk += line
                curr_chunk += '\n'
                curr_len += line_len
                curr_len += 1
            else:
                chunk_text.append(curr_chunk)
                curr_chunk = curr_chunk[-cover_content:] + line
                curr_len = line_len + cover_content

        if curr_chunk:
            chunk_text.append(curr_chunk)

        return chunk_text

    @classmethod
    def read_file_content(cls, file_path: str):
        # 拡張子に応じて適切な読み込み方法を選択
        if file_path.endswith('.pdf'):
            return cls.read_pdf(file_path)
        elif file_path.endswith('.md'):
            return cls.read_markdown(file_path)
        elif file_path.endswith('.txt'):
            return cls.read_text(file_path)
        else:
            raise ValueError("対応していないファイル形式です")

    @classmethod
    def read_pdf(cls, file_path: str):
        # PDFファイルを読み込む
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
            return text

    @classmethod
    def read_markdown(cls, file_path: str):
        # Markdownファイルを読み込む
        with open(file_path, 'r', encoding='utf-8') as file:
            md_text = file.read()
            html_text = markdown.markdown(md_text)
            # HTMLからプレーンテキストを抽出
            text_maker = html2text.HTML2Text()
            text_maker.ignore_links = True
            text = text_maker.handle(html_text)
            return text

    @classmethod
    def read_text(cls, file_path: str):
        # テキストファイルを読み込む
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()


class Documents:
    """
    分類済みの JSON 形式ドキュメントを取得するクラス
    """
    def __init__(self, path: str = '') -> None:
        self.path = path

    def get_content(self):
        with open(self.path, mode='r', encoding='utf-8') as f:
            content = json.load(f)
        return content
