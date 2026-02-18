# Conversation Starter – CrewAI Hierarchical Networking Research

A **CrewAI** multi-agent project using the **hierarchical process** to turn a LinkedIn URL into personalized research, critique, and conversation starters. The crew uses a manager (GPT-4o) to delegate and iterate between research, your personal context, a critique step, and a question architect.

## Requirements

- Python 3.10+
- API keys: **OpenAI**, **Proxycurl**, **Firecrawl** (see below)

## Setup

1. **Create a virtual environment and install dependencies**

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install --upgrade pip
   pip install --index-url https://pypi.org/simple/ -r requirements.txt
   ```

   If you see `Cannot fetch index base URL https://pypi.python.org/simple/`, your pip is using the old index. Use the command above with `--index-url https://pypi.org/simple/` or run `pip install --upgrade pip` first.

2. **Configure environment**

   Copy `.env.example` to `.env` and set:

   - `OPENAI_API_KEY` – for CrewAI agents and the hierarchical manager (e.g. GPT-4o)
   - `PROXYCURL_API_KEY` – for LinkedIn profile data ([nubela.co/proxycurl](https://nubela.co/proxycurl/))
   - `FIRECRAWL_API_KEY` – for web search ([firecrawl.dev](https://firecrawl.dev))

3. **Personal context**

   Edit `my_interests.md` with your focus areas, interests, and expertise. This file is the source of truth for the Personal Context Agent and for personalizing questions and “What I can learn from them.”

## Run

```bash
python main.py "https://www.linkedin.com/in/<username>/"
```

The crew will:

1. **Research** – Use LinkedIn (Proxycurl) + web search (Firecrawl) for career vibe, achievements, and non-obvious interests.
2. **Context sync** – Read `my_interests.md` to represent you.
3. **Critique** – Compare research to your context; delegate back to the researcher if it’s too generic.
4. **Output** – Produce a Markdown report with 5 Pointed Questions and 3 Conversation Starters, optionally add “What I can learn from them,” and append new interests to `my_interests.md` when relevant.

## Project layout

- `main.py` – Crew kickoff, `Process.hierarchical`, `manager_llm=LLM(model="gpt-4o")`, `memory=True`.
- `agents.py` – Five agents: Orchestrator, Web Researcher, Personal Context, Review & Critique, Question Architect.
- `tasks.py` – Four tasks: Research, Context Sync, Critique (with `allow_delegation=True`), Output.
- `tools/` – Custom **LinkedInTool** (Proxycurl), **FirecrawlSearchTool** (dynamic query), **AppendInterestsTool** (update `my_interests.md`).
- `my_interests.md` – Your interests and expertise (read by the crew; updated by the Question Architect when appropriate).

## Technical notes

- **Hierarchical process** – Manager LLM coordinates and can re-delegate to the Web Researcher when the critique step rejects the research.
- **Memory** – `Crew(..., memory=True)` keeps state across agents.
- **Proxycurl** – `LinkedInTool` calls `https://nubela.co/proxycurl/api/v2/linkedin` with the profile URL.
- **Firecrawl** – Custom tool calls `https://api.firecrawl.dev/v1/search` with a query so the researcher can run multiple searches.
