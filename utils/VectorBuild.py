from pathlib import Path
from RAG import VectorStore, ReadFiles, OpenAIChat, InternLMChat, LlmJp, JinaEmbedding, ZhipuEmbedding, E5Embedding

class VectorBuild:
    def __init__(self):
        # 稳定地定位到 ../data 目录
        #data_path = Path(__file__).resolve().parent.parent / "data"
        data_path = "./data"
        docs = ReadFiles(str(data_path)).get_content(max_token_len=600, cover_content=150)

        vector = VectorStore(docs)
        embedding = E5Embedding()
        vector.get_vector(EmbeddingModel=embedding)  
        vector.persist(path='storage')
