import streamlit as st
from utils import ChatOperate, ensure_vector_storage


def main():
    # Initialize page
    st.set_page_config(page_title="データベース質問応答システム", layout="centered")

    # Initialize history in session_state
    if "history" not in st.session_state:
        st.session_state.history = []

    try:
        # Load vector storage and model
        if "chat" not in st.session_state:
            with st.spinner("読み込み中...お待ちください。"):
                ensure_vector_storage()
                st.session_state.chat = ChatOperate()
        chat = st.session_state.chat

        st.title("🧠データベース回答システム")
        st.markdown("質問を入力してください。データベースの情報に基づいて回答します。")

        user_question = st.text_input("💬質問を入力してください：")

        # When the "Ask" button is clicked and the question is not empty
        if st.button("🔍質問する") and user_question:
            # Show thinking spinner while processing
            with st.spinner("考えています...しばらくお待ちください。"):
                response = chat.chat_require(user_question)
                #_, response, _ = chat.chat_require(user_question)

            st.markdown("### 📝 回答：")
            st.success(response)
            # Append question and answer to history
            st.session_state.history.append((user_question, response))

        # Show history in sidebar
        with st.sidebar:
            st.header("🕘 履歴")
            if st.session_state.history:
                for idx, (q, r) in enumerate(reversed(st.session_state.history), 1):
                    with st.expander(f"質問 {idx}: {q}"):
                        st.markdown(f"**回答：** {r}")
            else:
                st.info("履歴はまだありません。")

    except FileNotFoundError as e:
        st.error(f"❌ エラー：{e}")
    except Exception as e:
        st.error(f"❗ 不明なエラー：{e}")


if __name__ == "__main__":
    main()



