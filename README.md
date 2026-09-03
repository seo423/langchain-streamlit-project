# Perplexity Clone

An AI-powered search assistant inspired by Perplexity, built with **LangChain, LangGraph, OpenAI, and Streamlit**.

## 🚀 Live Demo

**[Try the application](https://langchain-proj.streamlit.app/)**

The deployed application can be accessed directly through a web browser without local installation.

## ✨ Features

* 🔎 **Agentic Web Search** — LLM-powered agent that can search the web and incorporate real-time information into responses
* 💬 **Multi-turn Conversations** — Maintains conversation context across multiple queries
* ⚡ **Streaming Responses** — Displays AI-generated responses in real time
* ⚙️ **Search Customization** — Configure search result count, topics, and domains
* 🤖 **LLM Selection** — Supports GPT-4o and GPT-4o-mini
* 📊 **LangSmith** — LLM tracing and observability

## 🏗️ Architecture

```text
User Query
    ↓
LLM Agent
    ↓
Web Search Tool
    ↓
Search Results
    ↓
LLM
    ↓
Streaming Response
```

## 🛠️ Tech Stack

**LangChain · LangGraph · OpenAI · Streamlit · LangSmith**

## 📁 Project Structure

```text
├── main.py
├── modules/
│   ├── agent.py
│   ├── handler.py
│   └── tools.py
├── pyproject.toml
└── README.md
```

## ▶️ Run Locally

```bash
poetry install
poetry run streamlit run main.py
```

Set your API keys in `.env` before running the application.

## ☁️ Deployment

Deployed with **Streamlit Community Cloud**.

**[Live Application →](https://langchain-proj.streamlit.app/)**
