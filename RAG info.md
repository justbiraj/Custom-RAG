# Understanding Retrieval-Augmented Generation (RAG)

This README provides a concise overview of Retrieval-Augmented Generation (RAG): an architecture that combines retrieval from external documents with a generative LLM to produce more accurate, relevant, and verifiable answers.

---

## Concept
Think of RAG as an "open-book exam" for an LLM. Rather than relying solely on model memory, the model is given relevant external text at query time. This grounds responses in real documents and reduces hallucinations.

---

## High-level Architecture
Two main phases:

1. Indexing (offline / data preparation)  
2. Retrieval & Generation (real-time answering)

---

## Phase 1 — Indexing (Preparing the library)

Goal: convert documents into a searchable, semantic knowledge base.

1. Document loading
    - Extract raw text from sources (.pdf, .txt, .docx, HTML, etc.).

2. Splitting (chunking)
    - Break large documents into smaller chunks to fit LLM context windows and improve retrieval precision.
    - Why chunk:
      - Fits model token limits
      - Reduces noise and distractions
      - Improves semantic matching

    - Common strategies:
      - Recursive character splitting (prioritized separators: paragraphs -> sentences -> spaces)
      - Semantic splitting (split where topic/meaning shifts)

3. Creating embeddings
    - Convert each chunk to a vector using an embedding model (e.g., text-embedding-3-small, or open-source models like all-MiniLM-L6-v2).
    - Similar text -> vectors close in high-dimensional space.

4. Store in vector DB
    - Save embeddings + chunk text + metadata (source, title, offset).
    - Vector DB examples: Pinecone, Qdrant, Weaviate, Milvus.

---

## Phase 2 — Retrieval & Generation (Answering a question)

1. User query -> embedding
    - Encode the user's question with the same embedding model used during indexing.

2. Retrieval
    - Perform similarity search in the vector DB and return top-k relevant chunks.

3. Augmenting the prompt
    - Construct a prompt that includes:
      - Retrieved context (text chunks)
      - Optional chat history
      - The user's original question
    - Example prompt template:
      ```
      You are a helpful AI assistant. Answer the user's question based ONLY on the context provided below.
      If the information is not in the context, say so.

      --- CONTEXT ---
      [Retrieved chunk 1]
      [Retrieved chunk 2]
      ...
      QUESTION: [User's original question]
      ```

4. Generation
    - Send the augmented prompt to the LLM (e.g., GPT-3.5/4 or other models).
    - The LLM generates an answer grounded in the retrieved content.

---

## Simple Flow Diagram (ASCII)

Indexing Phase:
PDF/TXT/DOCX -> Load Text -> Chunking -> Create Embeddings -> Store in Vector DB

Generation Phase:
User Question -> Create Embedding -> Search Vector DB -> Retrieve Chunks -> Augment Prompt -> LLM Generates Answer

---

## Practical tips & best practices
- Use the same embedding model for both indexing and querying.
- Keep chunk size balanced (often 200–800 tokens) depending on domain and model context limits.
- Store document metadata (source, URL, timestamp) to enable traceable answers.
- Filter retrieved chunks for relevance and freshness (especially for time-sensitive data).
- Limit number of chunks (k) to avoid exceeding prompt token limits and to minimize irrelevant context.
- Consider reranking retrieved candidates with a lightweight cross-encoder if higher precision is needed.

---

## Tooling & model suggestions
- Embeddings: OpenAI embeddings (text-embedding-3-*), SentenceTransformers (all-MiniLM-L6-v2), etc.
- Vector DBs: Pinecone, Qdrant, Weaviate, Milvus
- LLMs: GPT-4/3.5, or open-source LLMs with instruction-tuning
- Parsers/loaders: pdfminer, PyMuPDF, python-docx, BeautifulSoup

---

## Example minimal pseudocode
```
# Indexing
docs = load_documents(path)
chunks = chunk_documents(docs)
embeddings = embed(chunks)
vector_db.upsert(chunks, embeddings, metadata)

# Query
q_emb = embed([user_query])
results = vector_db.search(q_emb, top_k=4)
prompt = build_prompt(results, user_query)
answer = llm.generate(prompt)
```

---

## References & next steps
- Implement a simple pipeline: loader -> chunker -> embedder -> vector DB -> prompt builder -> LLM
- Add tests for chunking quality and retrieval relevance
- Add logging and provenance tracking so answers can cite sources

---

License: adapt as needed for your project.