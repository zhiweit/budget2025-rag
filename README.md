# budget2025-rag

## Todo

- Observability into the RAG pipeline
- Evaluate answer generated
  - Groundedness
- Allow choice of different embedding models

### Selecting LLM

- Support function calling for
  - Structured output parsing in guardrails
  - Query decomposition
  - Invoke tools
  - ReAct loop to reason on question, ools and continuously invoking tools to answer question natively

Configurable hyperparameters

- LLM temperature
- Prompt template
- context window
- response mode for response synthesiser
- similarity top k for retriever
- rerank top k for reranker

### Justification

Llama 3.2:3b

- Open source
- Multilingual input and output
- Context window 2048 tokens
- Supports function calling
- Fits 8gb RAM hardware constraints

### Chat architecture

- Chatengine uses LLM with ReAct agent for tool use
- Response synthesizer uses compact and refine

### Architectures

- ✔️ Chat engine: Selected because it fits the use case of asking questions from indexed knowledge base where every question should be obtained from the knowledge base. Chat engine is also a actually a ReAct agent with tool use in its llama index implementation. Just that its only tool is to query the knowledge base.
- ReAct agent with tool: Extensible and flexible to add new tools to augment agent knowledge
- Workflow: Control over the flow of events; technically works for the use case too, with fine-grained event streaming e.g. when retrieval happens, reranking happens, etc.

## Running Ollama

```bash
docker compose up
```

### Pulling model

E.g. Pulling llama3.2:3b

```bash
docker compose exec ollama ollama pull llama3.2:3b
```

### Running chat

```bash
docker compose exec ollama ollama run llama3.2:3b
```

To follow the logs

```bash
docker compose logs -f ollama
```
