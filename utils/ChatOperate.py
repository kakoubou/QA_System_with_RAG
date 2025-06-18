from pathlib import Path
from RAG import VectorStore, ReadFiles, OpenAIChat, InternLMChat, LlmJp, JinaEmbedding, ZhipuEmbedding, E5Embedding


class ChatOperate:
    def __init__(self):
        storage_path = "./storage"

        # ベクトルデータベースを初期化し、ローカルデータを読み込む
        self.vector = VectorStore()
        self.vector.load_vector(storage_path)

        # 埋め込みモデルとLLMモデルを初期化（長期利用を想定）
        self.embedding = E5Embedding()
        self.llm = LlmJp(path="llm-jp/llm-jp-3.1-1.8b-instruct4")

    def chat_require(self, question: str):
        """
        質問を入力 → 関連コンテキストを検索 → 応答を生成 → 結果を返す
        """
        # 最も関連性の高いコンテキスト（トップ1）を検索
        context = self.vector.query(question, EmbeddingModel=self.embedding, k=1)[0]

        # 言語モデルを呼び出してQ&Aを実行
        response = self.llm.chat(prompt=question, content=context)

        return response

       




