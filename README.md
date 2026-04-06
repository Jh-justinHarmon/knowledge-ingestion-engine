# Knowledge Ingestion Engine

## Why I Built This

I wanted a structured way to take raw documents, notes, and artifacts and turn them into **usable system knowledge**, not just stored files.

Most ingestion systems just store and embed documents. This pipeline is designed to **process, structure, store, and track knowledge artifacts** so they can be used by agents and systems later with traceability and context.

The goal is repeatable, inspectable knowledge ingestion — not just file parsing.

---

## What This Is

A multi-stage knowledge ingestion pipeline that processes input artifacts, extracts and structures information, stores it, and generates artifacts and telemetry for each run.

It includes:

* Pipeline orchestration
* Structured data models
* Storage layer
* Context storage
* Artifact generation
* Telemetry and run tracking
* CLI interface for running ingestion jobs

This is infrastructure for **knowledge ingestion**, not just document processing.

---

## What It Demonstrates

This project demonstrates how to design ingestion systems with:

* Multi-stage pipelines instead of single scripts
* Structured models instead of loose JSON
* Separation of pipeline, storage, and models
* Artifact generation for reproducibility
* Telemetry for observability
* CLI interface for controlled execution

The focus is on building a **repeatable ingestion system**, not a one-off script.

---

## How to Run

```bash
python cli.py
```

Place files in `sample_inputs/` and run the CLI to execute the ingestion pipeline.

---

## Repo Structure

```
knowledge-ingestion-engine/
├── cli.py              # Command-line interface
├── pipeline.py         # Pipeline orchestration
├── config.py           # Configuration
├── stages/             # Processing stages
├── models/             # Data models
├── store/              # Storage layer
├── context_store/      # Context data
├── sample_inputs/      # Sample input files
├── artifacts/          # Output artifacts
└── telemetry/          # Telemetry data
```

---

## What This Project Is (In One Sentence)

This project is a structured pipeline for turning raw files into **tracked, structured, and usable knowledge artifacts** for AI systems.
