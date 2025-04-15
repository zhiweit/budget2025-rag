from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def load_embed_model(embed_model_name: str):
    embed_model = HuggingFaceEmbedding(model_name=embed_model_name)
    embedding_model_dimensions = 1024
    return embed_model, embedding_model_dimensions
