from typing import Dict, List, Optional, Tuple, Union
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

PROMPT_TEMPLATE = dict(
    RAG_PROMPT_TEMPALTE="""以下の文脈を参考にして、ユーザーの質問に答えてください。答えが分からない場合は、知らないと正直に答えてください。
        質問: {question}
        参考用の文脈：
        ···
        {context}
        ···
        もし上記の文脈から答えを導き出せない場合は、「データベースにその情報は存在しないため、分かりません」と答えてください。
        有益な回答：""",
    InternLM_PROMPT_TEMPALTE="""まず、以下の文脈を要約してください。その後、文脈をもとにユーザーの質問に答えてください。答えが分からない場合は、知らないと正直に答えてください。
        質問: {question}
        参考用の文脈：
        ···
        {context}
        ···
        もし上記の文脈から答えを導き出せない場合は、「データベースにその情報は存在しないため、分かりません」と答えてください。
        有益な回答：""",
    LLMJP_PROMPT_TEMPALTE="""以下のデータベースを参考にして、ユーザーの質問に自然言語150文字数以内で答えてください。データベースに関係内容がない場合は、知らないと正直に答えてください。
        質問: {question}
        参考用のデータベース：
        ···
        {context}
        ···
        もし上記のデータベースから答えを導き出せない場合は、「データベースにその情報は存在しないため、分かりません」と答えてください。
        有益な回答：""",
    LLMJP_SYSTEM="""あなたは知識ベースを参照してユーザーの質問に答えるAIアシスタントです。
        質問に対しては、提供されたデータベースの情報のみを使って回答してください。
        もしデータベースに答えがない場合は、「データベースにその情報は存在しないため、分かりません」と正直に答えてください。
        回答はわかりやすく、150文字数以内にお願いします。"""
)


class BaseModel:
    def __init__(self, path: str = '') -> None:
        self.path = path

    def chat(self, prompt: str, history: List[dict], content: str) -> str:
        pass

    def load_model(self):
        pass

class OpenAIChat(BaseModel):
    def __init__(self, path: str = '', model: str = "gpt-3.5-turbo-1106") -> None:
        super().__init__(path)
        self.model = model

    def chat(self, prompt: str, history: List[dict], content: str) -> str:
        from openai import OpenAI
        client = OpenAI()   
        history.append({'role': 'user', 'content': PROMPT_TEMPLATE['RAG_PROMPT_TEMPALTE'].format(question=prompt, context=content)})
        response = client.chat.completions.create(
            model=self.model,
            messages=history,
            max_tokens=150,
            temperature=0.1
        )
        return response.choices[0].message.content

class InternLMChat(BaseModel):
    def __init__(self, path: str = '') -> None:
        super().__init__(path)
        self.load_model()

    def chat(self, prompt: str, history: List = [], content: str='') -> str:
        prompt = PROMPT_TEMPLATE['InternLM_PROMPT_TEMPALTE'].format(question=prompt, context=content)
        response, history = self.model.chat(self.tokenizer, prompt, history)
        return response


    def load_model(self):
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        self.tokenizer = AutoTokenizer.from_pretrained(self.path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(self.path, torch_dtype=torch.float16, trust_remote_code=True).cuda()


class LlmJp(BaseModel):
    MAX_HISTORY_LEN = 7  # 最大の対話履歴数（systemを含む）

    def __init__(self, path: str = 'llm-jp/llm-jp-3.1-1.8b-instruct4') -> None:
        super().__init__(path)
        self.path = path
        self.history: List[dict] = []  # インスタンスの対話履歴を初期化
        self.load_model()

    def chat(self, prompt: str, content: str = '') -> str:
        # 最初に system メッセージを追加
        if len(self.history) == 0:
            self.history.append({
                'role': 'system',
                'content': PROMPT_TEMPLATE['LLMJP_SYSTEM']
            })

        # ユーザーの入力を追加
        self.history.append({
            'role': 'user',
            'content': PROMPT_TEMPLATE['LLMJP_PROMPT_TEMPALTE'].format(question=prompt, context=content)
        })

        # モデルへの入力を構築
        tokenized_input = self.tokenizer.apply_chat_template(
            self.history,
            add_generation_prompt=True,
            tokenize=True,
            return_tensors="pt"
        ).to(self.model.device)

        # 応答を生成
        with torch.no_grad():
            output = self.model.generate(
                tokenized_input,
                max_new_tokens=500,
                do_sample=True,
                top_p=0.95,
                temperature=0.7,
                repetition_penalty=1.05,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id  # 終了トークンが出現したら生成を停止
            )[0]

        # モデルの出力をデコードし、入力部分を除外
        input_len = tokenized_input.shape[1]
        response = self.tokenizer.decode(output[input_len:], skip_special_tokens=True).strip()

        #response = response.split('\n')[0] if '\n' in response else response

        # モデルの応答を履歴に追加
        self.history.append({
            'role': 'assistant',
            'content': response
        })

        # 履歴の長さを制限。最初の system を残して古い対話を削除
        if len(self.history) > self.MAX_HISTORY_LEN:
            system_entry = self.history[0]
            excess = len(self.history) - self.MAX_HISTORY_LEN
            del self.history[1:1 + excess]
            self.history[0] = system_entry

        return response

    def load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.path,
            device_map=None,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True
        )
        self.model.to("cpu")