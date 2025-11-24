from langchain_huggingface import HuggingFaceEmbeddings

def get_embedding_function():
    """
    Returns the embedding function used in MITREembed.
    """
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L12-v2"
    )
