# PH HR Assistant — Intelligent HR Policy Knowledge Assistant

An intelligent document knowledge assistant built to explore and implement **Context Engineering techniques for Retrieval-Augmented Generation (RAG)**.

The project uses a synthetic 98-page HR Policy Manual as its knowledge source. It focuses on transforming unstructured policy documents into structured, searchable, context-aware knowledge that can support accurate and evidence-grounded question answering.

Rather than treating RAG as a simple PDF-to-vector-database workflow, this project explores the engineering challenges involved in document understanding, policy-aware chunking, metadata management, retrieval, context construction, and grounded response generation.

---

## Project Overview

HR policy documents often contain multiple levels of information:

- Major sections and policy categories
- Individual policies and subsections
- Headings, paragraphs, and page boundaries
- Rules, conditions, exceptions, and eligibility criteria
- Information that may require different access permissions

A naive RAG implementation that splits documents into fixed-size chunks can lose relationships between these elements.

This project investigates how to preserve document structure and contextual relationships throughout the knowledge pipeline.

### Objectives

- Build a structured document ingestion pipeline.
- Extract and preserve the hierarchy of HR policies.
- Implement policy-aware and token-aware document chunking.
- Explore parent-child chunking for better retrieval and context reconstruction.
- Maintain metadata and document provenance.
- Build a foundation for hybrid retrieval and reranking.
- Construct relevant context for grounded LLM responses.
- Evaluate individual stages of the Context Engineering pipeline.
- Explore security and access-control considerations in document retrieval.

## Knowledge Source

The project uses a **synthetic HR Policy Manual**, designed for experimentation without exposing confidential company information.

| Property          | Details                                          |
| ----------------- | ------------------------------------------------ |
| Document          | HR Policy Manual                                 |
| Format            | PDF                                              |
| Total pages       | 98                                               |
| Major sections    | 4                                                |
| Policies          | 14                                               |
| Subsections       | 110                                              |
| Extraction method | Page-level PDF text extraction                   |
| OCR requirement   | Not required for the initial document extraction |

The document processing work also generated structured intermediate artifacts:

- `hr_policy_pages.jsonl` — extracted page-level document data.
- `hr_toc_registry.json` — structured table-of-contents and policy hierarchy information.

## Architecture

The project follows a modular Context Engineering architecture.

```text
                 SYNTHETIC HR POLICY MANUAL
                           |
                           v
                 DOCUMENT INGESTION
                           |
              +------------+------------+
              |                         |
              v                         v
        PDF Extraction             Text Cleaning
              |                         |
              +------------+------------+
                           |
                           v
                 DOCUMENT PROCESSING
                           |
                           v
                STRUCTURE UNDERSTANDING
                           |
              +------------+------------+
              |                         |
              v                         v
        TOC Extraction           Policy Identification
              |                         |
              +------------+------------+
                           |
                           v
                  METADATA VALIDATION
                           |
                           v
                  POLICY-AWARE CHUNKING
                           |
              +------------+------------+
              |                         |
              v                         v
        Parent Chunks              Child Chunks
              |                         |
              +------------+------------+
                           |
                           v
                   EMBEDDING PIPELINE
                           |
                           v
                       CHROMADB
                           |
                           v
                    USER QUESTION
                           |
                           v
                  QUERY UNDERSTANDING
                           |
                           v
                  RETRIEVAL PIPELINE
                           |
             +-------------+-------------+
             |                           |
             v                           v
        Dense Retrieval             BM25 Retrieval
             |                           |
             +-------------+-------------+
                           |
                           v
                 HYBRID RESULT FUSION
                    (RRF approach)
                           |
                           v
                   METADATA FILTERING
                           |
                           v
                      RERANKING
                           |
                           v
                 PARENT CONTEXT RECOVERY
                           |
                           v
                  CONTEXT CONSTRUCTION
                           |
                           v
                 GROUNDED GENERATION
                           |
                           v
                  ANSWER EVALUATION
```

The diagram represents the overall engineering architecture being developed. Individual components are implemented and validated progressively; not every stage should be considered production-ready.

---

## Technology Stack

| Technology             | Purpose                                      |
| ---------------------- | -------------------------------------------- |
| Python                 | Core application and pipeline implementation |
| Ollama                 | Local LLM and embedding model runtime        |
| Qwen3 8B               | Local language model                         |
| mxbai-embed-large      | Embedding model                              |
| ChromaDB               | Vector database                              |
| PyPDF                  | PDF text extraction                          |
| Hugging Face ecosystem | Model and tokenizer support                  |

### Local Model Configuration

The project is configured to use locally running Ollama models.

**Generation model**

```text
qwen3:8b
```

**Embedding model**

```text
mxbai-embed-large:latest
```

**Ollama endpoint**

```text
http://localhost:11434
```

**ChromaDB collection**

```text
hr_policy_chunks
```

The intention is to keep model inference and embedding generation local rather than requiring a paid hosted LLM API.

---

## Implemented Engineering Components

### 1. Document Ingestion

The ingestion pipeline extracts text from the HR Policy Manual page by page.

Key responsibilities:

- PDF loading and page-level extraction.
- Source and page metadata preservation.
- Text cleaning and normalization.
- Document processing and validation.
- Structured intermediate output generation.

Representative modules:

```text
document_loader.py
text_cleaner.py
document_processor.py
metadata_validator.py
```

**Initial extraction validation:**

| Metric                       | Result |
| ---------------------------- | -----: |
| Total pages                  |     98 |
| Pages with extracted text    |     98 |
| Pages without extracted text |      0 |

The initial extraction was successful, so OCR was not necessary for this document.

### 2. Document Structure Understanding

Instead of treating the HR manual as plain text, the project extracts its document hierarchy.

Implemented modules include:

```text
toc_extractor.py
toc_registry.py
build_toc_registry.py
section_identifier.py
heading_identifier.py
```

Key concepts:

- Table-of-contents extraction.
- Policy identification.
- Section and heading identification.
- Hierarchical document representation.
- Policy-level structural metadata.

Intermediate artifacts:

```text
hr_policy_pages.jsonl
hr_toc_registry.json
```

### 3. Policy-Aware and Token-Aware Chunking

A major focus of this project is avoiding arbitrary chunk boundaries.

The chunking pipeline explores:

- Policy boundary preservation.
- Cross-page text combination.
- Token-aware splitting.
- Overlap between adjacent chunks.
- Page and character-offset tracking.
- Parent-child chunk relationships.

For example, when a policy spans multiple pages, its text can be combined before token-aware splitting rather than treating each PDF page as an independent document.

**Cross-page chunking validation**

The Performance Appraisal Policy spanning pages 35–42 was tested.

| Metric                 |     Result |
| ---------------------- | ---------: |
| Pages combined         |          8 |
| Chunks generated       |          4 |
| Maximum chunk size     | 445 tokens |
| Configured maximum     | 460 tokens |
| Chunks exceeding limit |          0 |

Character offsets and page tracking were also validated to preserve source positioning.

### 4. Parent-Child Chunking

The project implements a parent-child chunking approach.

**Parent chunks**

Contain larger contextual units to preserve surrounding policy information.

**Child chunks**

Contain smaller retrieval-oriented units to improve matching with user queries.

The relationship allows a system to retrieve a focused child chunk and subsequently recover its broader parent context.

**Observed parent-child processing results:**

| Metric                         |     Result |
| ------------------------------ | ---------: |
| Total processed records        |        213 |
| Parent chunks                  |         40 |
| Child chunks                   |        173 |
| Maximum parent size            | 900 tokens |
| Maximum child size             | 250 tokens |
| Orphan child chunks            |          0 |
| Policy relationship mismatches |          0 |

Output artifact:

```text
data/processed/chunks/parent_child/parent-child.jsonl
```

These results demonstrate that the parent-child relationships and the associated structural validations were working in the tested dataset.

### 5. Metadata and Document Provenance

Metadata is important for more than filtering search results. It helps preserve where a piece of information came from and how it relates to the original document.

The project includes metadata validation and structural metadata processing.

Relevant considerations include:

- Source document.
- Page number and location.
- Section and policy identity.
- Heading and subsection relationships.
- Parent-child relationships.
- Access-related metadata.

The architecture also considers metadata-based access control so that retrieval can respect document permissions rather than relying exclusively on semantic similarity.

---

## Retrieval and Context Engineering Roadmap

The following components form the broader retrieval and answer-generation architecture.

| Component                    | Engineering purpose                                          |
| ---------------------------- | ------------------------------------------------------------ |
| Query understanding          | Identify the user's information need                         |
| Dense retrieval              | Find semantically relevant chunks                            |
| BM25 retrieval               | Find keyword-based matches                                   |
| Hybrid retrieval             | Combine semantic and lexical retrieval                       |
| Reciprocal Rank Fusion (RRF) | Combine ranked retrieval results                             |
| Metadata filtering           | Restrict results using document metadata                     |
| Reranking                    | Improve the relevance ordering of retrieved chunks           |
| Parent context recovery      | Restore surrounding information                              |
| Context construction         | Build a relevant context for the LLM                         |
| Grounded generation          | Generate responses from retrieved evidence                   |
| Evaluation                   | Measure retrieval and answer quality                         |
| Security                     | Consider authentication, authorization, and access filtering |

These are architectural areas under development and validation. Their presence in this section describes the intended system design, not a claim that every component is already complete.

---

## Evaluation Strategy

The project uses stage-level validation rather than evaluating only the final generated answer.

Important evaluation dimensions include:

**Document processing**
- Extraction completeness.
- Text quality.
- Metadata correctness.
- Structural consistency.

**Chunking**
- Token-limit compliance.
- Policy-boundary preservation.
- Chunk overlap.
- Parent-child relationship integrity.
- Source traceability.

**Retrieval**
- Precision@K.
- Recall@K.
- Hit Rate.
- Mean Reciprocal Rank (MRR).
- Retrieval relevance.

**Generation**
- Answer correctness.
- Faithfulness to retrieved evidence.
- Context relevance.
- Unsupported-answer prevention.

The goal is to identify which stage causes an incorrect answer rather than treating every failure as an LLM generation problem.

---

## Project Structure

The repository is organized into modular source code, experiments, tests, evaluation, and data directories.

```text
ph_hr_assistance/
│
├── data/
│   ├── raw/
│   │   └── hr_policy_manual.pdf
│   └── processed/
│       ├── hr_policy_pages.jsonl
│       ├── hr_toc_registry.json
│       └── chunks/
│           └── parent_child/
│               └── parent-child.jsonl
│
├── src/
│   └── hr_assistant/
│       ├── ingestion/
│       ├── metadata/
│       ├── chunking/
│       ├── query_understanding/
│       ├── retrieval/
│       ├── context/
│       ├── generation/
│       └── security/
│
├── experiments/
│   ├── ingestion/
│   ├── chunking/
│   ├── retrieval/
│   └── context/
│
├── tests/
│
├── evaluation/
│
├── main.py
├── build_toc_registry.py
├── requirements.txt
├── .gitignore
└── README.md
```

The tree above is a representative view of the project organization; individual experiment and test files may evolve as implementation progresses.

---

## Getting Started

### Prerequisites

- Python installed on your system.
- Git.
- Ollama installed and running.
- Sufficient local resources to run the selected language and embedding models.

### 1. Clone the repository

```bash
git clone https://github.com/sairamsenthil/ph_hr_assistance.git
```

```bash
cd ph_hr_assistance
```

### 2. Create a virtual environment

**Windows**

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

### 4. Configure Ollama

Start Ollama and download the required models:

```bash
ollama pull qwen3:8b
```

```bash
ollama pull mxbai-embed-large:latest
```

Verify that the models are available:

```bash
ollama list
```

The configured Ollama endpoint is:

```text
http://localhost:11434
```

### 5. Run the application

The project contains a `main.py` entry point. Run it from the project root:

```bash
python main.py
```

Individual ingestion, chunking, and experiment modules can also be executed using their Python module paths. Refer to the corresponding experiment files for their specific commands.

---

## Engineering Principles

The project is guided by the following principles:

1. **Structure before retrieval:** Understand the source document before creating searchable chunks.
2. **Preserve relationships:** Maintain policy, section, heading, and parent-child relationships.
3. **Context over similarity alone:** A semantically similar chunk is not necessarily sufficient to answer a question.
4. **Traceability:** Preserve source information so retrieved evidence can be traced back to the document.
5. **Evaluate each stage:** Identify failures at ingestion, chunking, retrieval, context construction, or generation.
6. **Local-first experimentation:** Prefer locally executed models and tools for development.
7. **Security-aware retrieval:** Consider access permissions before returning retrieved information.

## Current Development Status

This is an actively developed learning and engineering project.

| Area                                         | Status                           |
| -------------------------------------------- | -------------------------------- |
| PDF text extraction                          | Implemented and validated        |
| Text cleaning and document processing        | Implemented                      |
| TOC and policy structure extraction          | Implemented                      |
| Metadata validation                          | Implemented                      |
| Cross-page token-aware chunking              | Implemented and tested           |
| Parent-child chunking                        | Implemented and tested           |
| Local Ollama configuration                   | Configured                       |
| ChromaDB integration                         | Configured                       |
| Full retrieval pipeline                      | Under development and validation |
| Hybrid retrieval and reranking               | Part of the broader architecture |
| Context construction and grounded generation | Part of the broader architecture |
| End-to-end evaluation                        | Ongoing                          |
| Security and access-control integration      | Under development                |

The status table reflects the implementation evidence available at this stage and will be updated as more components are completed.

---

## Why This Project?

The purpose is to develop practical expertise in **Context Engineering for Agentic AI systems**.

A reliable knowledge assistant requires more than connecting a PDF, an embedding model, and an LLM.

It requires deliberate engineering across the entire information lifecycle:

- How information is extracted.
- How document structure is represented.
- How chunks are created.
- How metadata is preserved.
- How relevant information is retrieved.
- How context is assembled.
- How the model is grounded in evidence.
- How the resulting answers are evaluated and secured.

This project serves as a practical implementation of those concepts.

## Author

**Sairam S.**

Agentic AI Engineering | Context Engineering | RAG | Python | LLM Applications

GitHub: [@sairamsenthil](https://github.com/sairamsenthil)

---

*This project uses a synthetic HR policy document for educational and experimentation purposes. It is not an official HR decision-making system or a substitute for professional HR or legal advice.*