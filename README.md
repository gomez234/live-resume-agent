# Live Resume Agent

Live Resume Agent is an AI-powered interactive resume that allows users to chat with an AI version of Samuel Gomez. Instead of reading a static resume, recruiters, professors, employers, and collaborators can ask questions about Samuel’s background, projects, technical experience, internships, research, and career interests.

The system uses AutoGen, Gradio, OpenAI, Supabase PostgreSQL, pgvector, semantic retrieval, web search, and an evaluator feedback loop to create a conversational and document-grounded experience.

## Project Overview

The purpose of this project is to transform a traditional resume into a live conversational AI system.

Users can ask questions such as:

- Tell me about your internship.
- What was your project?
- What technical skills do you have?
- What experience do you have?
- What kind of roles are you interested in?

The agent answers in a natural first-person style, as if the visitor is speaking directly with Samuel.

## Key Features

### Conversational Resume Experience

The assistant is designed to speak naturally in first person. It avoids robotic resume summaries and instead responds in a warm, professional, and engaging tone.

### AutoGen Multi-Agent Workflow

The system uses specialized agents rather than a single prompt-based chatbot:

- Router Agent
- Web Search Agent
- Answer Writer Agent
- Evaluator Agent
- Escalation Agent

Each agent has a specific responsibility in the workflow.

### Semantic RAG with pgvector

The project uses Retrieval-Augmented Generation to ground answers in verified documents. Resume documents are processed into chunks, embedded using OpenAI embeddings, and stored in Supabase PostgreSQL with pgvector.

During chat, the user question is embedded and compared against stored document chunks using vector similarity search.

### Web Search Capability

The Web Search Agent can search online for current or public information when the question requires external context.

This allows the system to answer questions about technologies, companies, universities, or recent public information without relying only on static resume documents.

### Evaluator Feedback Loop

The Answer Writer Agent drafts a response, and the Evaluator Agent reviews it.

The evaluator checks whether the answer is:

- conversational
- first person
- professional
- grounded in context
- not robotic
- not overly structured

If the response is not strong enough, the evaluator sends feedback back to the Answer Writer Agent. This loop repeats up to a fixed number of attempts before returning the final answer.

### Escalation Workflow

If the system cannot answer confidently, it routes the user toward direct contact.

The escalation workflow:

1. Detects that the question should not be answered automatically.
2. Asks the visitor for their email.
3. Stores the question in Supabase.
4. Sends Samuel an email notification with the unanswered question and visitor contact information.

This helps prevent hallucinations while creating a professional follow-up system.

## How It Works

### Document Ingestion

Resume and profile documents are stored locally in the `data/` folder.

The ingestion pipeline:

1. Loads documents.
2. Extracts text from PDFs.
3. Splits text into chunks.
4. Creates embeddings using OpenAI.
5. Stores chunks and embeddings in Supabase PostgreSQL with pgvector.

Run ingestion with:

```bash
uv run ingest.py
```

### Semantic Retrieval

When a user asks a question, the app creates an embedding for the question and searches Supabase for the most relevant information chunks.

The retrieval chunks are passed to the Answer Write Agent as verified context.

### Routing

The Router Agent decides whether a question should use:

- Resume RAG
- Web Search

Questions about Samuel's personal experience, project, skills, and background use the resume database.

Questions about public or current information use the Web Search Agent.

### Answer Generation

The Answer Writer Agent creates a first-person response as Samuel.

### Evaluation Loop

The Evaluator Agent reviews the draft answer. If it is too robotic, too formal, not first-person, or not grounded enough, it requests a revision

### Escalation

If the system cannot safely answer, it asks the users' email and send Samuel a notification.

## Local Setup

### Clone the repository

```bash
git clone https://github.com/gomez234/live-resume-agent.git
cd live-resume-agent
```

### Install dependencies with uv

```bash
uv sync
```

### Create `.env`

```env
OPENAI_API_KEY=your_openai_key
DATABASE_URL=your_supabase_postgres_url
SERPER_API_KEY=your_serper_key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
NOTIFY_EMAIL_FROM=your_email@gmail.com
NOTIFY_EMAIL_PASSWORD=your_gmail_app_password
NOTIFY_EMAIL_TO=your_email@gmail.com
```

### Run document ingestion

```bash
uv run ingest.py
```

### Run the app

```bash
uv run app.py
```

