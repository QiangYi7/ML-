import json
import openai  # For managing the API key


openai.api_key = ''

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    documents = []
    for episode, content in data.items():
        for character, details in content["characters"].items():
            if "Musical Note Hairpin" in details.get("Interactions_with_Key_Items", {}):
                documents.append(f"Episode {episode}: {json.dumps(details, ensure_ascii=False)}")
    return documents


def initialize_qa_system(documents):

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_text("\n".join(documents))

 
    embeddings = OpenAIEmbeddings(openai_api_key="")
    vectorstore = FAISS.from_texts(texts, embeddings)

    llm = ChatOpenAI(model="gpt-4", openai_api_key="")
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever())
    return qa


def ask_question(qa):
    while True:
        query = input("\n请输入你的问题（或输入 'exit' 退出）：")
        if query.lower() == 'exit':
            print("退出程序。")
            break
        # Directly call the qa object with the query
        result = qa({"query": query})
        print(f"答案：{result['result']}")


if __name__ == "__main__":
    file_path = "/Users/qiangyi/Desktop/rag/发卡_all_episodes_analysis_third version.json"
    documents = load_data(file_path)
    qa_system = initialize_qa_system(documents)
    ask_question(qa_system)
