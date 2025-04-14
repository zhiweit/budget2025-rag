from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.llms.litellm import LiteLLM
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.response_synthesizers.type import ResponseMode

import os

OLLAMA_API_BASE = os.getenv(
    'OLLAMA_API_BASE',
    'http://localhost:11434'
)

LITELLM_LLM_RERANKER_MODEL_NAME = os.getenv(
    'LITELLM_LLM_RERANKER_MODEL',
    'ollama_chat/llama3.2:3b'
)

LLM_RERANKER_TOP_N = os.getenv(
    'LLM_RERANKER_TOP_N',
    4
)

LLM_RERANKER_CHOICE_BATCH_SIZE = os.getenv(
    'LLM_RERANKER_CHOICE_BATCH_SIZE',
    5
)

LITELLM_RESPONSE_SYNTHESIZER_MODEL = os.getenv(
    'LITELLM_RESPONSE_SYNTHESIZER_MODEL',
    'ollama_chat/llama3.2:3b'
)

SIMILARITY_TOP_K = os.getenv(
    'SIMILARITY_TOP_K',
    12
)

SIMILARITY_CUTOFF = os.getenv(
    'SIMILARITY_CUTOFF',
    0.7
)

LITELLM_CHAT_ENGINE_LLM_MODEL_NAME = os.getenv(
    'LITELLM_CHAT_ENGINE_LLM_MODEL_NAME',
    'ollama_chat/llama3.2:3b'
)

SENTENCE_TRANSFORMER_RERANKER_MODEL = os.getenv(
    'SENTENCE_TRANSFORMER_RERANKER_MODEL',
    'cross-encoder/mmarco-mMiniLMv2-L12-H384-v1'
)

SENTENCE_TRANSFORMER_RERANKER_TOP_N = os.getenv(
    'SENTENCE_TRANSFORMER_RERANKER_TOP_N',
    4
)

# region Chat Engine Components
# Similarity cutoff processor
similarity_postprocessor = SimilarityPostprocessor(
    similarity_cutoff=SIMILARITY_CUTOFF
)

# Sentence Transformer Reranker
sentence_transformer_reranker = SentenceTransformerRerank(
    model=SENTENCE_TRANSFORMER_RERANKER_MODEL, top_n=SENTENCE_TRANSFORMER_RERANKER_TOP_N
)


# LLM Reranker
# llm_reranker_model = LiteLLM(
#     LITELLM_LLM_RERANKER_MODEL_NAME,
#     api_base=OLLAMA_API_BASE
# )

# llm_reranker = LLMRerank(
#     llm=llm_reranker_model,
#     top_n=LLM_RERANKER_TOP_N,
#     choice_batch_size=LLM_RERANKER_CHOICE_BATCH_SIZE
# )

# Response Synthesizer
response_synthesizer_llm = LiteLLM(LITELLM_RESPONSE_SYNTHESIZER_MODEL)

response_synthesizer = get_response_synthesizer(
    llm=response_synthesizer_llm, response_mode=ResponseMode.COMPACT
)
# endregion

chat_engine_llm = LiteLLM(LITELLM_CHAT_ENGINE_LLM_MODEL_NAME)
