"""
Connect to vector store and create index
"""
import re
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import VectorStoreIndex
from db import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os

HUGGING_FACE_EMBEDDING_MODEL = os.getenv(
    'HUGGING_FACE_EMBEDDING_MODEL',
    'intfloat/multilingual-e5-large'
)

embed_model = HuggingFaceEmbedding(model_name=HUGGING_FACE_EMBEDDING_MODEL)
print(f'embedding model {embed_model.model_name} loaded')
embedding_model_dimensions = 1024

table_prefix = 'budget_2025-'
model_name_clean = re.sub(r'[^a-zA-Z0-9\-]', '-', embed_model.model_name)
table_name = f'{table_prefix}{model_name_clean}'


vector_store = PGVectorStore.from_params(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            table_name=table_name,
            perform_setup=False,
            embed_dim=embedding_model_dimensions,
        )

vsi = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    embed_model=embed_model
)