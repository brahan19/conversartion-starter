# Conversation Starter – CrewAI Hierarchical Networking Research

A **CrewAI** multi-agent project using the **hierarchical process** to turn a LinkedIn URL into accurate, personalized research and conversation starters. The crew uses an **Orchestrator** manager to coordinate research, evidence filtering, critique, and report generation with strict accuracy controls.

## Features

- **Accuracy-first design**: Grounds all facts in tool output; filters web results without concrete evidence; rejects unsupported claims
- **Evidence Filter**: Removes web search results that don't clearly refer to the target person
- **Multi-model setup**: Uses `gpt-4o` for research and report writing, `gpt-4o-mini` for coordination and context
- **Stateful manager**: Orchestrator loop capped at 2 iterations per task
- **Iterative improvement**: Critique agent provides detailed rejection feedback that is passed back to the researcher to prevent repeated mistakes
- **Firecrawl logging**: Visible search queries and results for debugging
- **LinkedIn integration**: Uses Proxycurl API when available as source of truth

## Requirements

- **Python 3.10, 3.11, or 3.12** (CrewAI does not support 3.9 or below)
- API keys: **OpenAI**, **Firecrawl** (Proxycurl optional)

## Setup

1. **Use Python 3.10+ for the virtual environment**

   Check your Python version: `python3 --version` or `python3.10 --version`. If you have 3.9 or lower, install Python 3.10+ (e.g. from [python.org](https://www.python.org/downloads/) or Homebrew: `brew install python@3.11`).

2. **Create the virtual environment with Python 3.10+**

   ```bash
   # Use python3.11 or python3.10 if that's what you have; plain python3 only if it's already 3.10+
   python3.11 -m venv venv
   # or: python3.10 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install --upgrade pip
   pip install --index-url https://pypi.org/simple/ -r requirements.txt
   ```

   If you see `No matching distribution found for crewai>=0.80.0`, your venv is using Python < 3.10. Delete `venv`, then create it with `python3.10` or `python3.11` as above.

   If you see `Cannot fetch index base URL https://pypi.python.org/simple/`, use `--index-url https://pypi.org/simple/` or run `pip install --upgrade pip` first.

3. **Configure environment**

   Copy `.env.example` to `.env` and set:

   - `OPENAI_API_KEY` – for CrewAI agents (required)
   - `FIRECRAWL_API_KEY` – for web search ([firecrawl.dev](https://firecrawl.dev)) (required)
   - `PROXYCURL_API_KEY` – *optional*; for LinkedIn profile data ([nubela.co/proxycurl](https://nubela.co/proxycurl/)). If not set, the researcher uses web search only.

4. **Personal context**

   Edit `my_interests.md` with your focus areas, interests, and expertise. This file is the source of truth for the Personal Context Agent and for personalizing questions and "What I can learn from them."

## Run

```bash
# Required: LinkedIn profile URL
python main.py "https://www.linkedin.com/in/<username>/"

# Optional but recommended: name and current work to disambiguate when many people share the same name
python main.py "https://www.linkedin.com/in/johndoe/" --name "John Doe" --current-work "CTO at Acme Inc"
```

- **`linkedin_url`** (required) – LinkedIn profile URL.
- **`--name`** (optional) – Person's full name. Used by Research and Evidence Filter to target web search and filter results so they refer to this person, not someone else with the same name.
- **`--current-work`** (optional) – Person's current role/company (e.g. `CTO at Acme Inc`). Further disambiguates search and filtering.

When `--name` is provided, the report file is named using the name (e.g. `reports/john_doe_2026-02-18_12-00-00.md`); otherwise the LinkedIn URL slug is used.

The crew will execute 5 tasks in sequence:

1. **Research** – Uses LinkedIn (Proxycurl) + web search (Firecrawl) for career vibe, achievements, and interests. Includes source URLs for each fact.
2. **Context Sync** – Reads `my_interests.md` to represent you.
3. **Evidence Filter** – Filters out web search results that don't have concrete evidence they refer to the target person (same name + company/role match, or explicit mention).
4. **Critique** – Validates filtered research depth and factual grounding; rejects unsupported or invented claims; can delegate back to the researcher with detailed feedback (specific reasons and actionable instructions) to prevent repeated mistakes.
5. **Output** – Produces a Markdown report with a detailed Career Vibe section (3-4 paragraphs telling their life story), Key Points, 10 Pointed Questions, and 10 Conversation Starters based only on filtered research. Optionally adds "What I can learn from them" (up to 10 items) and appends new interests to `my_interests.md`.

Reports are saved to `reports/{person_slug}_{timestamp}.md`.

## Architecture

### Agents (6 total)

1. **Orchestrator** (Manager) – Coordinates the crew, delegates tasks, ensures pipeline completion. When the Critique agent rejects research and delegates back to the Researcher, the Orchestrator passes the complete rejection feedback (with specific reasons and actionable instructions) so the Researcher can address issues without repeating mistakes. Uses `gpt-4o-mini`, capped at 2 iterations per task (`max_iter=2`).
2. **Web Researcher** – Gathers intelligence via LinkedIn + Firecrawl. Uses `gpt-4o` for accuracy. Only reports facts from tool output; never infers or invents.
3. **Personal Context Agent** – Reads `my_interests.md` to represent your interests and expertise. Uses `gpt-4o-mini`.
4. **Research Evidence Filter** – Filters web search results to keep only those with concrete evidence they refer to the target person. Uses `gpt-4o-mini`.
5. **Review & Critique Agent** – Validates research depth and factual accuracy. Rejects unsupported claims. When delegating back to the Researcher, includes detailed rejection feedback with specific reasons and actionable instructions. Uses `gpt-4o-mini`.
6. **Question Architect** – Crafts the final report from filtered research only, including a detailed 3-4 paragraph Career Vibe section that tells the person's life story. Uses `gpt-4o` for quality. Can update `my_interests.md` when relevant.

### Tasks (5 total)

1. **Research Task** – LinkedIn first (source of truth), then web search for additional context. Gathers comprehensive information about career progression, transitions, motivations, and notable experiences to enable writing a detailed life story. Uses **name** and **current work** (when provided) to disambiguate search. Must cite source URLs. Grounds all facts in tool output.
2. **Context Sync Task** – Extracts your focus areas from `my_interests.md`.
3. **Evidence Filter Task** – Filters research to keep only facts with concrete evidence they refer to the target person; uses **name** and **current work** when provided to reject results about other people with the same name.
4. **Critique Task** – Evaluates filtered research on depth and factual grounding. When rejecting, provides detailed feedback with specific reasons and actionable instructions. Can delegate back to researcher with this feedback.
5. **Output Task** – Produces Markdown report with a detailed Career Vibe section (3-4 paragraphs telling their life story), Key Points, questions and starters based only on filtered research.

### Accuracy Controls

- **Grounding rules**: All tasks require facts to be traceable to tool output; no inference or invention.
- **LinkedIn as source of truth**: When available, LinkedIn data (headline, experience, education) is treated as canonical; web search only adds extra context.
- **Evidence filtering**: Web results are filtered to remove those without concrete evidence they refer to the target person. When **name** and **current work** are provided, they are used to ensure results match this specific person (not another with the same name).
- **Factual checks**: Critique agent rejects unsupported or invented details (e.g. specific numbers, achievements not stated).
- **Iterative feedback**: When critique rejects research, detailed rejection reasons and actionable instructions are passed back to the Researcher through the Orchestrator, preventing repeated mistakes.
- **Conservative output**: Question Architect prefers generic but accurate over specific but unsupported.

### Tools

- **LinkedInTool** (`tools/linkedin_tool.py`) – Calls Proxycurl API (`https://nubela.co/proxycurl/api/v2/linkedin`) to fetch structured LinkedIn profile data.
- **FirecrawlSearchTool** (`tools/firecrawl_search_tool.py`) – Calls Firecrawl API (`https://api.firecrawl.dev/v1/search`) with dynamic queries. Returns up to 8 results. Includes logging to show queries and results in console.
- **AppendInterestsTool** (`tools/append_interests_tool.py`) – Appends new interests to `my_interests.md` when the Question Architect identifies relevant expertise.

## Project Layout

- `main.py` – Crew setup, model assignment (`gpt-4o` for research/report, `gpt-4o-mini` for others), hierarchical process with Orchestrator as manager.
- `agents.py` – Six agents: Orchestrator (manager), Web Researcher, Personal Context, Evidence Filter, Review & Critique, Question Architect.
- `tasks.py` – Five tasks: Research, Context Sync, Evidence Filter, Critique, Output.
- `tools/` – Custom tools: LinkedInTool (Proxycurl), FirecrawlSearchTool (with logging), AppendInterestsTool.
- `my_interests.md` – Your interests and expertise (read by Personal Context Agent; updated by Question Architect when appropriate).
- `reports/` – Generated reports saved as `{person_slug}_{timestamp}.md`.

## Technical Notes

- **Hierarchical process** – Orchestrator manager coordinates tasks and can re-delegate to Web Researcher when critique rejects research. The Orchestrator ensures rejection feedback is passed to the Researcher.
- **Memory** – `Crew(..., memory=False)` - each session starts fresh without retaining information from previous runs.
- **Model assignment** – Web Researcher and Question Architect use `gpt-4o`; others use `gpt-4o-mini`.
- **Firecrawl logging** – Search queries and results are printed to console for debugging (see `tools/firecrawl_search_tool.py`).
- **Stateful manager** – Orchestrator has `max_iter=2` to cap iterations per task.
- **Proxycurl** – Optional; if `PROXYCURL_API_KEY` is not set, researcher uses web search only.
- **Rejection feedback loop** – When Critique agent rejects research, it provides detailed feedback (specific reasons and actionable instructions) that is passed to the Researcher via the Orchestrator, enabling iterative improvement without repeating mistakes.

## Example Output

The crew produces a Markdown report with:
- **Career Vibe** – A detailed 3-4 paragraph narrative telling the person's life story, covering their background, education, career progression, key transitions, major roles, achievements, motivations, and current focus. Written as an engaging narrative that helps readers understand their journey.
- **Key Points** – Bullet points highlighting major achievements and roles (filtered and grounded)
- **10 Pointed Questions** – Specific questions bridging their background with your interests
- **10 Conversation Starters** – Openers grounded in filtered research
- **Optional "What I can learn from them" section** – Up to 10 items when relevant
- **Optional update to `my_interests.md`** – When the person has expertise relevant to your interests

All facts in the report are traceable to the filtered research; no unsupported claims are included. The Career Vibe section weaves together verified facts into a compelling narrative while maintaining strict accuracy.
