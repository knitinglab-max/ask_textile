from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma


def get_retriver():

    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory="./chroma_qwen_db"
    )
    main_retriever = vectorstore.as_retriever(search_type= "similarity", search_kwargs = {"k":2})

    return main_retriever

# new = vector_DB()
# query = "what is warf"
# vec_retriver = new.similarity_search(query,k=4)

# # query = "what is yarn strength"

# # result = vec_retriver.invoke(query)

# for i, result in enumerate(vec_retriver):
#   print(f"------ result{i}------- \n")
#   print(f"{result.page_content}")