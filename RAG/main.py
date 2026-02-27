from langchain_core.runnables import RunnableLambda,RunnableParallel,RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from .retreiver import get_retriver
from .llm import get_llm
from .prompts import get_prompts

main_retriever = get_retriver()
llm = get_llm()
prompt = get_prompts()

def context(docs):
  return "\n\n".join(doc.page_content for doc in docs)

context_chain = RunnableParallel({
    "context" : main_retriever | RunnableLambda(context),
    "question" : RunnablePassthrough()

})

parser = StrOutputParser()

main_chain = context_chain | prompt | llm | parser

answer = main_chain.invoke("can you create 30 neche questions from the context")
print(answer)