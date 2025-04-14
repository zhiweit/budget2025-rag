from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model_name = "intfloat/multilingual-e5-large"
embed_model = HuggingFaceEmbedding(model_name=embed_model_name)
embedding_model_dimensions = 1024