from langchain.chains import LLMChain
from langchain.chains import RetrievalQA  # A common chain for RAG Q&A applications [6, 7]
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter  # For splitting large documents [4, 5]
from langchain_community.vectorstores import FAISS  # FAISS for in-memory vector store [1]
from langchain_openai import ChatOpenAI  # OpenAI's chat models for generation [8-11]
from langchain_openai import OpenAI
from langchain_openai import OpenAIEmbeddings  # For creating embeddings using OpenAI models [2, 3]
import argparse


def get_response(user_input):
    llm = OpenAI(temperature=0.7)  # Setting temperature for creativity
    prompt_template = PromptTemplate(
        input_variables=["user_input"],
        template="Create a poem based on lyrics from the Grateful Dead from the following: {user_input}",
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)

    response = chain.run(user_input)

    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Grateful Dead poem from lyrics.")
    parser.add_argument("--lyrics", type=str, help="Lyrics to base the poem on")
    parser.add_argument("--load", type=str, help="Path to JSONL file to load")

    args = parser.parse_args()
    lyrics = args.lyrics
    jsonl_file = args.load

    if lyrics:
        response = get_response(lyrics)
        print(f"A Grateful Dead Poem based on '{lyrics}'", response)

    if jsonl_file:
        from langchain_community.document_loaders import JSONLoader

        loader = JSONLoader(
            file_path=jsonl_file,
            jq_schema='{title, venue, date, views_all_time, views_last_30day, views_last_7day}',
            text_content=False,
            json_lines=True)

        documents = loader.load()

        print(f"--- 1. Loaded {len(documents)} documents from JSONL. ---")
        for i, doc in enumerate(documents[:2]):
            print(f"Document {i + 1} Content: {doc.page_content[:150]}...")
            print(f"Document {i + 1} Metadata: {doc.metadata}")

        print("\n--- 2. Transform Documents (Text Splitting) ---")
        # For larger real-world documents, it's essential to break them into smaller, semantically coherent chunks [14].
        # This helps the LLM process information within its context window and improves retrieval accuracy [14, 15].
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        split_documents = text_splitter.split_documents(documents)  # [18]

        print(f"**Split documents into {len(split_documents)} chunks**.")
        # Display content and metadata of the first few chunks
        for i, doc in enumerate(split_documents[:2]):
            print(f"\nChunk {i + 1} Content: {doc.page_content[:250]}...")
            print(f"Chunk {i + 1} Metadata: {doc.metadata}")

        print("\n--- 3. Embedding Documents ---")
        # The "Embed Phase" involves converting text chunks into numerical representations called embeddings [15, 19].
        # LangChain's `OpenAIEmbeddings` uses OpenAI's embedding models (e.g., `text-embedding-ada-002` by default) [2, 3].
        embeddings_model = OpenAIEmbeddings()

        # The "Store Phase" involves storing these embeddings in a vector database [20, 21].
        # For this example, we use FAISS, an in-memory vector store, for simplicity [1, 22, 23].
        print("\nCreating FAISS vector store from document chunks and OpenAI embeddings...")
        vectorstore = FAISS.from_documents(split_documents, embeddings_model)
        print("**FAISS vector store created**.")

        print("\n--- 4. Setting up Retrieval-Augmented Generation (RAG) ---")
        # Initialize the OpenAI LLM. `ChatOpenAI` is suitable for conversational applications [8-11, 24].
        # `temperature=0` encourages more deterministic (less creative) responses.
        llm = ChatOpenAI(model="gpt-4.1", temperature=0)

        retriever = vectorstore.as_retriever()  # [6, 23]

        # Build the RAG chain using `RetrievalQA`. This chain combines the retriever with the LLM [6, 7].
        # The "stuff" chain type typically puts all retrieved documents directly into the LLM's prompt [6, 7].
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",  # This dictates how the retrieved documents are passed to the LLM
            retriever=retriever,
            return_source_documents=True  # To show which documents were used as context
        )
        print("**RetrievalQA chain initialized** for RAG.")

        print("\n--- 5. Querying the OpenAI Model with RAG ---")

        query_1 = "which dead and co shows have the most views_all_time?"
        print(f"\n**User Query 1:** {query_1}")

        response_1 = qa_chain.invoke({"query": query_1})  # Invoke the RAG chain with the query [6]

        print("\n**Sources Retrieved for Query 1:**")
        for i, doc in enumerate(response_1["source_documents"]):
            print(f"Source Document {i + 1}:")
            print(doc.page_content[:250] + "...")
            print("-" * 30)

        print("\n**AI Assistant Response 1:**")
        print(response_1["result"])
