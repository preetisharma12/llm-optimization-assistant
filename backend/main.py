from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import re
import uuid
from datetime import datetime


from llm import LLM

# =====================================================
# JARGON FILTER
# =====================================================
# Safety net for the chat-facing text: the prompt asks the LLM to avoid
# these category words, but it isn't 100% reliable, so anything that
# slips through gets swapped for plain wording here too.

_JARGON_REPLACEMENTS = [
    (r"\bdecision variables\b", "adjustable settings"),
    (r"\bdecision variable\b", "adjustable setting"),
    (r"\bfixed parameters\b", "fixed setup details"),
    (r"\bfixed parameter\b", "fixed setup detail"),
    (r"\bconstraints\b", "requirements"),
    (r"\bconstraint\b", "requirement"),
    (r"\bmeasurements\b", "things to track"),
    (r"\bmeasurement\b", "thing to track"),
    (r"\bobjective\b", "goal"),
    (r"\bparameters\b", "settings"),
    (r"\bparameter\b", "setting"),
    (r"\bvariables\b", "settings"),
    (r"\bvariable\b", "setting"),
]


def sanitize_jargon(text):
    if not text:
        return text
    for pattern, replacement in _JARGON_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

# =====================================================
# FASTAPI
# =====================================================

app = FastAPI()

# =====================================================
# LLM INITIALIZATION
# =====================================================

llm_params = {
    "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
    "reasoning": {"effort": "medium"},
    "request_timeout": 1000.0,
    "max_retries": 3
}

llm = LLM(llm_params)

# =====================================================
# FIXED CONCEPT STRUCTURE
# =====================================================

FIXED_CONCEPTS = ["Objective", "Decision Variables", "Constraints", "Fixed Parameters", "Measurements"]

# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# REQUEST MODEL
# =====================================================

class ChatRequest(BaseModel):
    message: str

# =====================================================
# CONVERSATION MEMORY
# =====================================================

conversation = {
    "messages": [],
    "information": [],
    "finished": False,
    "concept_items": {name: [] for name in FIXED_CONCEPTS},
    "problem_title": ""
}

# =====================================================
# HOME
# =====================================================

@app.get("/")
def home():
    return {"message": "Backend is running!"}

# =====================================================
# TEST
# =====================================================

@app.get("/test")
def test():

    response = llm.query("Say hello in one sentence.")

    return {
        "response": response
    }

# =====================================================
# CHAT
# =====================================================

@app.post("/chat")
def chat(request: ChatRequest):

    # ----------------------------------------
    # Save user message
    # ----------------------------------------

    conversation["messages"].append({
        "role": "user",
        "content": request.message
    })

    # ----------------------------------------
    # Build conversation history
    # ----------------------------------------

    history = ""

    for msg in conversation["messages"]:
        history += f'{msg["role"]}: {msg["content"]}\n'

    # ----------------------------------------
    # Prompt
    # ----------------------------------------

    prompt = f"""
You are an optimization assistant.

Your ONLY task is to understand the optimization problem.

Return ONLY valid JSON.

Never write anything outside JSON.

Read the ENTIRE conversation.

There are EXACTLY five concepts, always discussed in this fixed order:

- Objective — what should be minimized or maximized, and why.
- Decision Variables — the adjustable settings the optimizer can choose.
- Constraints — hard limits and requirements that must be satisfied.
- Fixed Parameters — everything about the system that is given and NOT
  adjustable (equipment, workspace, payload, dimensions, fixed conditions).
- Measurements — the outputs that will actually be measured/observed to
  evaluate performance (e.g. cycle time, throughput, error, energy use).

Only work on ONE concept at a time, in that order.

Also maintain a short "problem_title" (2-5 words, Title Case, e.g.
"Robotic Arm Optimization" or "Conveyor System Optimization") that names
the specific system being optimized. Infer it as soon as it's clear from
context and keep returning it every turn once known (empty string until
then).

STRICT PROGRESSION RULE — a concept may ONLY become "completed" after the
user has explicitly confirmed it in reply to a direct question about that
concept. Never mark a concept "completed" the first time it is mentioned,
even if the user's message already seems to fully describe it. Instead:

- If this is the first time you have enough information about the current
  concept, summarize your understanding of it and ask "Did I understand
  correctly?" — keep it "current", NOT "completed", this turn.
- Only mark it "completed" on a LATER turn, once the user has replied
  confirming that specific question (a "yes", a correction, or restating
  the same facts back both count as confirmation).
- Do not skip this confirmation step just because the information seems
  unambiguous. Every concept must be explicitly asked about and confirmed
  before moving on, in order.

HANDLING VOLUNTEERED INFORMATION — if the user's message includes details
about a concept OTHER than the current one (e.g. they mention a constraint
while you are still on Objective), do NOT change which concept is
"current" and do NOT mark that other concept "completed" early. Instead:

- Record that information under the correct concept's "concept_items" now,
  so it is not lost.
- Keep asking about and confirming the CURRENT concept until it is done.
- When you later reach that other concept in order, use the
  already-volunteered information to ask a short confirmation question
  about it (e.g. "You mentioned X earlier for Constraints — did I
  understand that correctly?") instead of asking from scratch.

PLAIN LANGUAGE IN THE CHAT — the "explanation" and "assistant_question"
fields are read directly by an end user who is NOT an optimization
expert. These EXACT words/phrases are BANNED from ever appearing in
"explanation" or "assistant_question", in any form (including inside
longer words or different tenses):

  objective, decision variable, variable, constraint, fixed parameter,
  parameter, measurement

Before writing "explanation" and "assistant_question", check each
sentence for these banned words and rewrite the sentence if any appear.
Use these replacements instead:

- decision variable(s) → "the settings you can adjust" / "what the
  optimizer is allowed to change"
- constraint(s) → "rules", "limits", or "requirements that must always
  hold true"
- fixed parameter(s) → "the things that stay fixed / can't be changed" /
  "the given setup"
- measurement(s) → "what we'll track" / "how we'll judge whether it
  worked"
- objective → "the goal" / "what you're trying to achieve"

These category names are still used internally (in "concept",
"concepts_status", "concept_items") to drive the panel the user does not
read from — just never say them out loud in the conversation itself.

If the current concept is unclear:

- Explain it briefly, in plain language, without naming the category.
- Ask ONE question.
- End with:
"Did I understand correctly?"

If the current concept has already been confirmed:

- Move automatically to the next concept.

When ALL concepts are confirmed:

Return a short summary of the optimization problem.

Do NOT ask another concept question.

For EVERY response, classify ALL FIVE concepts (Objective, Decision
Variables, Constraints, Fixed Parameters, Measurements) into a
"concepts_status" object mapping each concept name exactly to one of these
statuses:

- "completed" — already confirmed
- "current" — being discussed right now
- "pending" — not reached yet

Exactly one concept must be "current" unless every concept is "completed".

For every concept that is "current" or "completed", also break it down into
its concrete sub-items in a "concept_items" object. Each sub-item is a
{{"name": "...", "class": "..."}} pair.

"name" MUST be a SHORT KEYWORD or phrase, 1-4 words maximum — never a full
sentence. Strip it down to the key term/value only. For example write
"Cycle time", "Damage < 2%", "Belt speed 0.5-2.5 m/s", or "Payload" — NOT
"Minimize the total cycle time for each pick and place operation" or
"Package damage must remain below 2 percent at all times".

"class" is a short 1-3 word label describing what KIND of item it is
within that concept (for example, under Fixed Parameters you might
classify items as "workspace" vs "payload" vs "gripper"; under Decision
Variables as "movement setting"; under Constraints as "hard constraint"
vs "soft constraint"; under Measurements as "performance metric"). Choose
whatever class labels make sense for that concept — only use classes that
genuinely help distinguish the items, and only include items actually
mentioned or confirmed so far.
Concepts that are still "pending" must have an empty list.

IMPORTANT: "concept_items" is NOT optional. If the user's message confirms
or mentions several concepts at once (for example one long message that
answers Objective, Decision Variables, Constraints, Fixed Parameters and
Measurements all together), you MUST still list sub-items for EVERY one of
those concepts in this same response, not just the one you set as
"current". A concept marked "completed" must never have an empty item list
if anything about it was ever said in the conversation.

Return JSON using this structure:

{{
    "concept":"",
    "problem_title":"",
    "concepts_status":{{
        "Objective":"pending",
        "Decision Variables":"pending",
        "Constraints":"pending",
        "Fixed Parameters":"pending",
        "Measurements":"pending"
    }},
    "concept_items":{{
        "Objective":[],
        "Decision Variables":[],
        "Constraints":[],
        "Fixed Parameters":[],
        "Measurements":[]
    }},
    "explanation":"",
    "assistant_question":"",
    "attributes":[
    ],
    "confidence":0,
    "progress":"",
    "finished":false
}}

When everything has been confirmed, return:

{{
     "concept":"Finished",
    "problem_title":"Robotic Arm Optimization",
    "concepts_status":{{
        "Objective":"completed",
        "Decision Variables":"completed",
        "Constraints":"completed",
        "Fixed Parameters":"completed",
        "Measurements":"completed"
    }},
    "concept_items":{{
        "Objective":[{{"name":"Cycle time","class":"minimize"}}],
        "Decision Variables":[{{"name":"Movement speed","class":"movement setting"}}],
        "Constraints":[{{"name":"Positioning error < 1 mm","class":"hard constraint"}}],
        "Fixed Parameters":[{{"name":"Payload","class":"fixed property"}}],
        "Measurements":[{{"name":"Cycle time","class":"performance metric"}}]
    }},
    "explanation":"All concepts have been confirmed.",
    "assistant_question":"I understood everything correctly. I will now generate the optimization model.",
    "attributes":[
        "Payload = 5 kg",
        "Workspace = 1.2 m radius",
        "Positioning error limit = 1 mm"
    ],
    "confidence":100,
    "progress":"100%",
    "finished":true
}}

For every concept, also extract the confirmed attributes related to that concept and return them in the "attributes" array.

Never solve the optimization problem.

Never generate equations.

Never generate variables.

Never generate constraints.

Never generate objectives.

Conversation:

{history}
"""

    # ----------------------------------------
    # Ask GPT
    # ----------------------------------------

    raw = llm.query(prompt)

    print(raw)

    # ----------------------------------------
    # Parse JSON
    # ----------------------------------------

    try:
        result = json.loads(raw)
        conversation["finished"] = result.get("finished", False)

    except Exception:
        result = {
            "concept": "Unknown",
            "concepts_status": {},
            "concept_items": {},
            "explanation": raw,
            "assistant_question": raw,
            "confidence": 0,
            "progress": "0/0",
            "finished": False
        }

    # ----------------------------------------
    # Strip any category jargon that slipped into the
    # user-facing text despite the prompt instructions
    # ----------------------------------------

    result["explanation"] = sanitize_jargon(result.get("explanation", ""))
    result["assistant_question"] = sanitize_jargon(result.get("assistant_question", ""))

    # ----------------------------------------
    # Save assistant message
    # ----------------------------------------

    conversation["messages"].append({
        "role": "assistant",
        "content": result["assistant_question"]
    })

    # ----------------------------------------
    # Information Panel
    # ----------------------------------------

    concepts_status = result.get("concepts_status", {})
    concept_items_this_turn = result.get("concept_items", {})

    # Keep the last known problem title once inferred, in case a later
    # turn's response omits it.
    new_title = (result.get("problem_title") or "").strip()
    if new_title:
        conversation["problem_title"] = new_title

    def is_near_duplicate(candidate, existing_names):
        candidate = candidate.lower()
        for existing_name in existing_names:
            if candidate == existing_name:
                return True
            # Catches paraphrases like "X below 2%" vs "X must remain below 2%"
            if len(candidate) > 12 and (candidate in existing_name or existing_name in candidate):
                return True
        return False

    # The LLM only reliably lists items for the concept it's actively
    # discussing right now — it tends to drop earlier concepts' items
    # when asked to redeclare everything every turn. So merge new items
    # into what's already been accumulated instead of trusting a full
    # redeclaration each time.
    for name in FIXED_CONCEPTS:
        new_items = concept_items_this_turn.get(name, [])
        if not new_items:
            continue

        existing = conversation["concept_items"].get(name, [])
        existing_names = [item["name"].strip().lower() for item in existing]

        for item in new_items:
            item_name = (item.get("name") or "").strip()
            if item_name and not is_near_duplicate(item_name, existing_names):
                existing.append({"name": item_name, "class": item.get("class", "")})
                existing_names.append(item_name.lower())

        conversation["concept_items"][name] = existing

    information = {
        "concepts": [
            {
                "name": name,
                "status": concepts_status.get(
                    name,
                    "current" if name == result["concept"] else "pending"
                ),
                "items": conversation["concept_items"].get(name, []),
                "confidence": result.get("confidence", 0)
                    if name == result["concept"] else None
            }
            for name in FIXED_CONCEPTS
        ],
        "currentConcept": result["concept"],
        "problemTitle": conversation.get("problem_title", ""),
        "explanation": result["explanation"],
        "attributes": result.get("attributes", []),
        "progress": result["progress"]
    }

    response_payload = {
        "assistant_reply": result["assistant_question"],
        "information": information
    }

    # ----------------------------------------
    # Auto-run the rest of the pipeline the moment
    # the interview is finished, so the JSON lands
    # in outputs/ without touching Swagger.
    # ----------------------------------------

    if conversation["finished"]:
        build_model_internal()
        final_description = generate_description_internal()
        response_payload["final_description"] = final_description
        response_payload["description_saved_to"] = conversation.get("description_path", "")
        response_payload["chat_closed"] = True

        closing_message = "Thank you for interacting with me. This chat is now closed."
        response_payload["assistant_reply"] = closing_message
        response_payload["information"]["explanation"] = closing_message

        # Reset for the next interview so a new chat doesn't reuse old messages
        conversation["messages"] = []
        conversation["information"] = []
        conversation["finished"] = False
        conversation["concept_items"] = {name: [] for name in FIXED_CONCEPTS}
        conversation["problem_title"] = ""
        conversation.pop("model", None)
        conversation.pop("description", None)
        conversation.pop("description_path", None)

    return response_payload

# =====================================================
# BUILD OPTIMIZATION MODEL
# =====================================================

def build_model_internal():

    # ----------------------------------------
    # Build conversation history
    # ----------------------------------------

    history = ""

    for msg in conversation["messages"]:
        history += f'{msg["role"]}: {msg["content"]}\n'

    # ----------------------------------------
    # Prompt
    # ----------------------------------------

    prompt = f"""
You are an optimization expert.

The following conversation contains all confirmed information
about an optimization problem.

Your task is ONLY to build the optimization model.

Do NOT ask questions.

Do NOT explain your reasoning.

Do NOT solve the optimization problem.

Return ONLY valid JSON.

Return EXACTLY this format:

{{
    "objective": "",

    "decision_variables": [
    ],

    "constraints": [
    ],

    "fixed_parameters": [
    ],

    "measurements": [
    ]
}}

Conversation:

{history}
"""

    print("========== Conversation ==========")
    print(history)
    print("==================================")

    answer = llm.query(prompt)

    # Save the optimization model for the next step
    conversation["model"] = answer

    print("========== OPTIMIZATION MODEL ==========")
    print(answer)
    print("========================================")

    return answer


@app.post("/build_model")
def build_model():

    # Don't build until the interview is finished
    if not conversation["finished"]:
        return {
            "model": "Interview not finished yet."
        }

    answer = build_model_internal()

    return {
        "model": answer
    }

# =====================================================
# GENERATE FINAL DESCRIPTION
# =====================================================

def generate_description_internal():

    model = conversation.get("model", "")

    if model == "":
        return "Optimization model has not been generated yet."

    prompt = f"""
You are an optimization expert explaining your understanding of a problem
to a non-technical reader, in your own words.

Write a natural-language description of this optimization problem as a
few flowing paragraphs of plain prose. Do NOT use section headers, labels,
or technical jargon words like "Objective", "Parameter", "Variable",
"Constraint", "Demand", or "Measurement" anywhere in the text — describe
everything conversationally instead, the way you'd explain it to a
colleague who isn't an optimization expert.

Do NOT return JSON, bullet points, or markdown symbols like ** or #.

Across the paragraphs, naturally cover:
- What is being optimized, and why
- What can be adjusted, and within what limits
- What rules or requirements must always be respected
- What stays fixed about the setup
- What will actually be measured to judge success

Whenever you mention a specific number, threshold, or setting, weave in
where it came from and how confident you are about it, as part of the
sentence rather than as a labeled field.

Optimization model:

{model}
"""

    answer = llm.query(prompt)

    conversation["description"] = answer

    os.makedirs("outputs", exist_ok=True)

    # Unique filename per finished chat, so results never overwrite each other
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_id = uuid.uuid4().hex[:6]
    filename = f"optimization_description_{timestamp}_{short_id}.txt"
    filepath = os.path.join("outputs", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(answer)

    conversation["description_path"] = os.path.abspath(filepath)

    print("========== FINAL DESCRIPTION ==========")
    print(answer)
    print(f"Saved to: {filepath}")
    print("========================================")

    return answer


@app.post("/generate_json")
def generate_json():

    model = conversation.get("model", "")

    if model == "":
        return {
            "description": "Optimization model has not been generated yet."
        }

    final_description = generate_description_internal()

    return {
        "description": final_description
    }