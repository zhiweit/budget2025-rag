import os
from llama_index.storage.chat_store.postgres import PostgresChatStore

DB_HOST = os.getenv('DB_HOST')
assert DB_HOST is not None
DB_PORT = os.getenv('DB_PORT')
assert DB_PORT is not None
DB_USER = os.getenv('DB_USER')
assert DB_USER is not None
DB_PASSWORD = os.getenv('DB_PASSWORD')
assert DB_PASSWORD is not None
DB_NAME = os.getenv('DB_NAME')
assert DB_NAME is not None

DB_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

chat_store = PostgresChatStore.from_uri(DB_URL)
