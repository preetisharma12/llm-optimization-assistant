# LLM-Optimization-Assistant

An AI-assisted chat interface that interviews a user about an optimization problem they want solved, then automatically turns that conversation into a structured optimization model and a plain-language description of it.

## How it works

The assistant conducts a structured interview across five fixed concepts, one at a time:

1. **Objective** — what should be maximized or minimized
2. **Decision Variables** — what can actually be changed/chosen
3. **Constraints** — hard limits that must hold
4. **Fixed Parameters** — known, unchangeable inputs
5. **Measurements** — how success/outcomes are judged

Each concept must be explicitly confirmed by the user before the assistant moves to the next one — it won't skip ahead or infer confirmation. Replies are also passed through a jargon filter (prompt instructions plus a regex-based safety net) so the assistant explains things in plain language instead of technical/optimization jargon.

Once all five concepts are confirmed, the backend automatically:
1. Builds a structured optimization model (parameters, variables, objective, constraints) as JSON
2. Generates a natural-language description of that model
3. Saves both to `backend/outputs/`
4. Locks the chat

## Architecture

- **Backend:** FastAPI (Python). Uses [llama-index](https://www.llamaindex.ai/) as an abstraction layer over the underlying chat model, so the provider can be swapped without touching business logic. Conversation state is held in memory per session.
- **Frontend:** React 19 + Vite + Tailwind CSS. A chat panel on the left; a live "Information Panel" on the right rendering an ASCII-style concept tree, a plain-language explanation, and progress indicators as the interview proceeds.
- **LLM connector:** Abstracted behind a small `LLM(params).query(prompt)` class in `backend/llm.py`. Configuration (API key, base URL, model name) is read entirely from environment variables — see `backend/.env.example` — so any OpenAI-compatible model/provider can be used.

## Tech stack

**Backend:** FastAPI, llama-index, openai, pydantic, uvicorn, python-dotenv

**Frontend:** React 19, Vite, Tailwind CSS 4, lucide-react

## Project structure

```
llm-optimization-assistant/
├── backend/
│   ├── main.py              # FastAPI app, interview logic, endpoints
│   ├── llm.py                # generic LLM connector (see IP note above)
│   ├── requirements.txt
│   ├── .env.example
│   └── outputs/               # generated models/descriptions land here (gitignored)
├── src/
│   ├── App.jsx
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── ChatWindow.jsx
│   │   ├── ChatMessage.jsx
│   │   ├── MessageInput.jsx
│   │   └── InformationPanel.jsx
│   ├── data/
│   ├── main.jsx
│   └── index.css
├── index.html
├── package.json
├── vite.config.js
└── .gitignore
```

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/test` | Health check |
| POST | `/chat` | Send a user message, get the assistant's next reply + updated information-panel state |
| POST | `/new_chat` | Reset the conversation |
| POST | `/build_model` | *(debug)* Manually trigger structured-model generation from the current conversation |
| POST | `/generate_json` | *(debug)* Manually trigger the natural-language description step |

## Getting started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and set OPENAI_API_KEY (and OPENAI_API_BASE / LLM_MODEL if needed)

uvicorn main:app --reload      # runs on http://127.0.0.1:8000
```

### Frontend

```bash
npm install
npm run dev                    # runs on http://localhost:5173
```

The frontend expects the backend at `http://127.0.0.1:8000`; CORS is configured for `http://localhost:5173`.

## Usage walkthrough

1. Open the app — the assistant greets you with "Hello! What would you like to optimize?"
2. Describe your problem in plain language, e.g. *"I want to optimize furniture production."*
3. The assistant asks about each of the five concepts in turn (Objective first, then Decision Variables, and so on), confirming each with you before moving on.
4. The Information Panel on the right fills in live: a concept tree, a running explanation, and progress.
5. Once all five concepts are confirmed, the backend automatically builds a structured optimization model and a plain-language description, saves both under `backend/outputs/`, and locks the chat.

## Example outputs

These are real outputs the tool generated, using clearly generic example problems (not tied to any client work).

**Structured model** (`optimization_model.json`, from a small staffing example):

```json
{
    "objective": {
        "name": "maximize_total_haircut_bookings_served",
        "sense": "maximize",
        "expression": "b"
    },
    "parameters": {
        "B": { "value": 100000, "interpretation": "Total budget available for hiring new haircut-skilled staff and training existing nail staff." },
        "H0": { "value": 4, "interpretation": "Initial number of staff already capable of serving haircut bookings." },
        "N0": { "value": 10, "interpretation": "Maximum number of nail staff who can be trained to perform haircuts." },
        "c_hire": { "value": 5000, "interpretation": "Hiring cost per additional haircut-skilled staff member." },
        "c_train": { "value": 3000, "interpretation": "Training cost per nail staff member converted to haircut capability." },
        "cap": { "value": 20, "interpretation": "Daily haircut service capacity contributed by each haircut-capable staff member." }
    },
    "variables": {
        "x": { "type": "integer", "lower_bound": 0, "interpretation": "Number of new haircut-skilled staff hired." },
        "y": { "type": "integer", "lower_bound": 0, "interpretation": "Number of nail staff trained to perform haircuts." },
        "b": { "type": "integer", "lower_bound": 0, "interpretation": "Total number of haircut bookings served during the day." }
    },
    "constraints": [
        { "name": "budget_limit", "expression": "5000*x + 3000*y <= 100000" },
        { "name": "training_availability", "expression": "y <= 10" },
        { "name": "booking_capacity", "expression": "b <= 20*(4 + x + y)" }
    ]
}
```

**Natural-language description** (from a 3D-printing settings example):

> This problem is about finding the best way to run a 3D print so the finished part looks and performs as well as possible, while also taking less time to make and using less filament. In other words, we are trying to balance three things that usually pull against each other: better-looking, more reliable parts, shorter print jobs, and lower material use. [...] The settings we are allowed to tune are the layer height, print speed, nozzle temperature, bed temperature, infill density, and cooling behavior. [...] However we tune the process, the part must still be strong enough to meet the minimum level required for use, and it must stay close enough to the intended size and shape that it does not exceed the allowed dimensional error.

## Limitations

- The interview is fixed to exactly five concepts (Objective, Decision Variables, Constraints, Fixed Parameters, Measurements) — it isn't adaptive to problem shapes that don't fit that structure.
- Conversation state lives in an in-memory dict on the backend; restarting the server clears any in-progress chat.
- Jargon sanitization is regex/keyword-based, so it can miss rephrasings or synonyms not covered by the banned-word list.
- No authentication or access control on the API as shipped — it's built for local/single-user use.
- The debug endpoints (`/build_model`, `/generate_json`) aren't gated behind interview completion, so they can be called independently of conversation state.

## License

MIT — see [LICENSE](LICENSE).
