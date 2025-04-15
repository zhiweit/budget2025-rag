# budget2025-rag

Chatbot for Budget 2025 with RAG using open source models.

Demo


https://github.com/user-attachments/assets/51c94003-5d33-42f5-a874-e91938faacb3



## Features

- Support multilingual input and output (english, chinese, malay, tamil)
- Support streaming response
- Support chat history and memory for conversations
- Observability into the chatbot workflow with Arize Phoenix

## Data collection and proprocessing approach

Data are stored in `data` folder, namely pdf files of

- budget debate round up speech
- budget booklet (in english, chinese, malay, tamil)
- budget statement

### Preprocessing

PDF files are parsed into markdown text using Mistral OCR API

## System architecture description and data flow overview

### System architecture

- (Parsing PDF files) Mistral OCR API to parse PDF files into markdown (with image as base64 if needed)
- (RAG Framework) Llama Index as a framework to build the RAG pipeline and integrations with multiple LLM providers and vector databases
- (Vector Database) Postgres with pgvector extension to store the vector embeddings of the text chunks
- (Observability) Arize Phoenix to observe chatbot workflow steps, latency, token usage, etc.

### Data flow

- (Getting data) Information about the budget are saved as PDF files in the `data` folder
- (Indexing) Indexing the documents into the vector database are done in `notebooks/index.ipynb`. Indexing pipeline:

  - (Parse into markdown) The PDF files are parsed into markdown text using Mistral OCR API
    = (Chunk the markdown) Parse the markdown into chunks using Markdown Node Parser from llama index
  - (Semantic chunking) The markdown chunks are further chunked using the embedding model as the semantic chunker with looking at 1 sentence before and after the current sentence and comparing the embedding similarity, combining similar chunks and splitting dissimilar chunks.
  - (Embed and store) Embeddings of the text chunks are obtained using the embedding model and stored in the Postgres database table.

- (Chat) Chatbot components are selected and integrated in `notebooks/chat.ipynb`.

## Model and tool selection rationale with implementation details

### Model and Tool Selection Rationale

- Embedding model: [intfloat/multilingual-e5-large](https://huggingface.co/intfloat/multilingual-e5-large)
  - Support multilingual input and output
  - 1024 dimensions
- Jina reranker: [jina-reranker-v2-base-multilingual](https://huggingface.co/jinaai/jina-reranker-v2-base-multilingual)
  - To rerank chunks retrieved to be relevant to the query
- LLM (via LiteLLM): [llama3.2:3b](https://ollama.com/library/llama3.2:3b)
  - Multilingual input and output
  - Context window 2048 tokens
  - Supports function calling
  - Fits 8gb RAM hardware constraints

### Implementation details (Chat Engine)

1. ReAct agent to decompose the query, handle any language translation and continuously reasoning on the question and tool call response and act on the response to decide if it needs to invoke the tool again or not
1. Tool: `RetrieverQueryEngine` to query the knowledge base. This tool takes in a query string and:

   - Embed the query using the embedding model from the vector index
   - Retrieve the top K most similar nodes/chunks from the vector store (similarity computed using cosine similarity score)
   - Postprocess the retrieved nodes to only include nodes whose similarity score is greater than the similarity cutoff (set to 0.7)
   - Rerank the nodes to `reranker_top_n` (set to 4) using jina reranker that compares the query with the node/chunk and returns how semantically similar they are to each other
   - Generate answer to the question via the response synthesizer with the context from the reranked nodes using a [compact](https://docs.llamaindex.ai/en/stable/module_guides/querying/response_synthesizers/#configuring-the-response-mode) response mode which stuffs the chunks up to the context window with the question to generate the answer.
   - Generated answer is returned to the ReAct agent to reason on the answer and decide if it needs to invoke the tool again or not

1. ReAct agent continuously goes between tool call and reasoning on the answer up to `max_iterations` (set to 30) to handle complex queries
1. Chat response is saved as chat history in the postgres database
1. Memory is obtained from chat history messaged using llm's context window \* 0.75 (default ratio from llama_index) as the memory to be passed in context when it begins the next interaction

## Testing methodology and evaluation metrics

Not completed, to be done in `notebooks/eval.ipynb` using [Arize Phoenix](https://docs.arize.com/phoenix/use-cases-evals/rag-evaluation#evaluation) for retrieval and response evaluation

## Installation and deployment guidelines

### Prerequisites

- Docker and Docker Compose
- Environment variables

### Installation

```bash
cp .envrc.sample .envrc
```

Edit the `.envrc` file with the correct environment variables.

Run this script to load the environment variables from the `.envrc` file

```bash
source load_env.sh
```

The postgres database hosted on AWS RDS has been indexed with the documents in the `data` folder, so the DB_HOST should be an AWS RDS url.

If you have GPU on your machine, leave the default settings in the `docker-compose.yml` file of Ollama service. Otherwise if you do not have GPU, comment out the gpu settings in the `docker-compose.yml` file of Ollama service. Note running on CPU will be slow.

You may have to wait for about 5 minutes for the packages to be installed in the docker container.

```bash
docker compose up -d
```

### Pulling model

This needs to be run for the first time to pull the models into the ollama container
E.g. Pulling llama3.2:3b into ollama container

```bash
docker compose exec ollama ollama pull llama3.2:3b
```

To follow the logs

```bash
docker compose logs -f
```

Navigate to `http://localhost:8501` to access the chatbot. You may have to wait for a few minutes for the embedding model weights to be downloaded from hugging face. Check the logs to see that 'Startup completed' to ensure that the models e.g. embedding model (from hugging face) are loaded successfully.
Something like this should be shown in the logs:

```bash
app-1     | embedding model intfloat/multilingual-e5-large loaded
app-1     | Thread ID: 6037cb40-a3d2-4b55-890f-3f90902a3d16
app-1     | 🌍 To view the Phoenix app in your browser, visit http://localhost:6006/
app-1     | 📖 For more information on how to use Phoenix, check out https://docs.arize.com/phoenix
app-1     | Phoenix launched
app-1     | Startup completed
```

Navigate to `http://localhost:6006` to access the Arize Phoenix app to observe the chatbot workflow steps, latency, token usage, etc.

### Limitations, constraints and mitigation approaches

- LLM may not respond in the same language when the user changes language midway e.g. change from english to chinese, the bot may still respond in english. This might be mitigated by changing the prompts.
- Response generated are generally short and not detailed. This might be mitigated by changing to a model with a larger context window or more powerful model e.g. openai gpt models.
- Latency

  - Running open-source models (embedding model, llm) on local hardware using CPU is slow. To mitigate this, run the ollama docker container on a machine with GPU by uncommenting the gpu settings in the `docker-compose.yml` file of Ollama service. E.g. running ollama with NVIDIA GeForce RTX 3050 Laptop GPU reduces the latency from 1-2mins on average to 10-30s on average.
