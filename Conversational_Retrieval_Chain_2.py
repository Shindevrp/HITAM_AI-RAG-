from langchain_community.callbacks import get_openai_callback
from langchain.chains import ConversationalRetrievalChain
from creds import openai_key, PINECONE_API_KEY, index_name
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.chat_message_histories import SQLChatMessageHistory
from prompts import context_prompt, condence_qstn_prompt

# Initialize qstn and instruction prompts
condense_question_prompt = PromptTemplate(input_variables=['question','chat_history'], template=condence_qstn_prompt())
qa_prompt = PromptTemplate(template=context_prompt(), input_variables=["context", "question"])

# Initialize LLM object
chat = ChatOpenAI(temperature=0, openai_api_key=openai_key, model="gpt-3.5-turbo-0125")
# Initialize Embedding model
embeddings = OpenAIEmbeddings(api_key=openai_key, model="text-embedding-ada-002")
# Initialize vector databse object
vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings, 
                                      pinecone_api_key=PINECONE_API_KEY, text_key="chunk")

# Create conversational chain
chain = ConversationalRetrievalChain.from_llm(llm=chat, retriever=vectorstore.as_retriever(search_kwargs={'k': 3}),
                                              chain_type="stuff", combine_docs_chain_kwargs = {"prompt": qa_prompt},
                                              condense_question_prompt=condense_question_prompt)
# Initialize chat history DB object
chat_history = SQLChatMessageHistory(session_id="11AABC11", connection_string="sqlite:///sqlite.db")
# Initialize langchain memory object
memory = ConversationBufferMemory(
                memory_key="chat_history",
                input_key="question",
                output_key='answer',
                return_messages=True,
                chat_memory=chat_history
            )


while True:
    question = input("user: ")
    if question.lower() == "exit" or question.lower() == "quit":
        break
    else:
        with get_openai_callback() as cb:
            result = chain.invoke({"question": question, "chat_history": memory.buffer})
            print("------------------- TOEKN DETAILS ---------------------------")
            print("PROMPT TOEKNS --- ", cb.prompt_tokens)
            print("COMPLETION TOEKNS --- ", cb.completion_tokens)
            print("TOTAL TOEKNS --- ", cb.total_tokens)
        # chat_history.append((question, result["answer"]))
        # memory.save_context({"question": question}, {"answer": result["answer"]})
        chat_history.add_user_message(question)
        chat_history.add_ai_message(result["answer"])
        print("-------------ANSWER------------")
        print(result['answer'])
        # print("-------------CHAT HISTORY------------")
        # print(chat_history)
        print("-------------------memory buffer----------------")
        print(memory.buffer)
