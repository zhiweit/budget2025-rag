# budget2025-rag

Chatbot for Budget 2025 with RAG using open source models.

Demo


https://github.com/user-attachments/assets/51c94003-5d33-42f5-a874-e91938faacb3



## Features

- Support multilingual input and output (english, chinese, malay, tamil)
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

- (Parsing PDF files) [Mistral OCR API](https://docs.mistral.ai/capabilities/document/) to parse PDF files into markdown (with image as base64 if needed)
- (RAG Framework) [Llama Index](https://docs.llamaindex.ai/en/stable/getting_started/concepts/) as a framework because of:
  - module usage examples (e.g. chunking modules, query engine, response synthesizer with the different response modes, etc.)
  - integrations with multiple LLM providers, vector databases, observability, etc.
- (Vector Database) Postgres with pgvector extension to store the vector embeddings of the text chunks
- (Observability) [Arize Phoenix](https://docs.llamaindex.ai/en/stable/module_guides/observability/#arize-phoenix-local) to observe chatbot workflow steps, latency, token usage, etc.
- (Structured output) [Guardrails AI](https://www.guardrailsai.com/docs/how_to_guides/generate_structured_data) library to enforce structured output from the LLM e.g. generating questions from retrieved chunks (only if it thinks a question can be generated from the chunk) for evaluation
- (Evaluation) [Arize Phoenix](https://docs.arize.com/phoenix/evaluation/concepts-evals/evaluation) to evaluate the chatbot's retrieval and response performance

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

Done in `notebooks/eval.ipynb` using [Arize Phoenix](https://docs.arize.com/phoenix/use-cases-evals/rag-evaluation#evaluation) for retrieval and response evaluation, over sample 100 LLM generated questions from the nodes/chunks in the vector store.

Sample query engine trace 
![sample-query-engine-trace](https://github.com/user-attachments/assets/0b99c2a3-50c9-4a31-9420-ebb16394d8e5)


### Retrieval Evaluation

- Normalized Cumulative Discounted Gain (NCDG) (~0.78): For most queries, the retrieval system is able to identify relevant documents and usually (but not always) place the most relevant documents at the top. But sometimes less relevant documents are ranked higher than more relevant ones.
- Precision at 2 (~0.65): Average LLM relevance score of top 2 retrieved nodes. On average, top 2 retrieved nodes are relevant to the question.
- Hit rate: Check if there's at least one relevant node in the top 2 retrieved nodes. Obtained 0.97, suggesting that of the 97% of questions, the retrieval system retrieved at least one relevant document in its top 2 retrieved nodes.

### Response Evaluation

- QA Correctness: Calculate the correctness of the answer generated by the chatbot. Obtained 0.90, suggesting that the chatbot's answer is correct for 90% of the questions.
- Hallucinations: Calculate the hallucinations of the answer generated by the chatbot. Obtained 0.05, suggesting that the chatbot's answer is hallucinated for 5% of the questions.

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

You may have to wait for several minutes for the packages to be installed in the docker container.

```bash
docker compose up -d
```

### Pulling model

This needs to be run for the first time to pull the models into the ollama container
E.g. Pulling llama3.2:3b into ollama container

```bash
docker compose exec ollama ollama pull llama3.2:3b
```

To follow the logs of the docker containers, run

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
app-1     | Chat engine LLM model: ollama_chat/llama3.2:3b
app-1     | Startup completed
```

Navigate to `http://localhost:6006` to access the Arize Phoenix app to observe the chatbot workflow steps, latency, token usage, etc.

If you face memory issues when running the streamlit app, you can try running the chat in `notebooks/chat.ipynb` for an easier and interactive experience with the ability to look at the components and see the output at each cell.

Running the chat in `notebooks/chat.ipynb` jupyter notebook requires the following steps:

- Download [uv](https://docs.astral.sh/uv/getting-started/installation/#homebrew) as the package manager for python
- Create a virtual environment and activate it

```bash
uv venv
source .venv/bin/activate
uv sync # sync the dependencies from the lockfile into your virtual environment
docker compose up -d # from the notebooks folder
```

Open the jupyter notebook `notebooks/chat.ipynb` and select the kernel to be the virtual environment you just created, and the cells should be able to be run.

### Limitations, constraints and mitigation approaches

- LLM may not respond in the same language when the user changes language midway e.g. change from english to chinese, the bot may still respond in english. This might be mitigated by changing the prompts.
- Response generated are generally short and not detailed. Mitigations:
  - use a simpler RAG architecture (use a workflow where we literally define the steps we want to take e.g. embed -> retrieve -> rerank -> generate answer with prompt templates) as opposed to currently using a ReAct agent to reason on the answer and decide if it needs to invoke the tool again or not, which may add a lot of 'thinking' steps into the context and cause the LLM to generate short answers as the context window is filled up with 'thinking' steps.
  - use a more powerful model that have larger context window e.g. openai gpt models.
- Latency

  - Running open-source models (embedding model, llm) on local hardware using CPU is slow. To mitigate this, run the ollama docker container on a machine with GPU by uncommenting the gpu settings in the `docker-compose.yml` file of Ollama service. E.g. running ollama with NVIDIA GeForce RTX 3050 Laptop GPU reduces the latency from 1-2mins on average to 10-30s on average.

### Further improvements

- Improving Retrieval
  - [AutoMergingRetriever](https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/modules/#hierarchicalnodeparser) Idea is to merge chunks that are similar to each other to improve retrieval.
  - Set prompt in the embedding if the embedding model supports it, to say embed only keywords or use a prompt to instruct the embedding model how to embed the text.
- Allow uploading of pdf on streamlit app
