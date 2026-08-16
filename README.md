# LLM-Based Optimization Assistant

> **Before publishing this repo:** this work was done at Fraunhofer IOSB-INA. Written confirmation from the supervisor/IP office that this can be public (code, write-up, and any images) has not yet been obtained. Until that confirmation is in hand, this repo intentionally contains no proprietary datasets, internal prompts, client-specific use cases, or proprietary business logic -- only a generic technical description of the approach, plus placeholders marked below for what will be filled in once cleared. A generic re-implementation (same architecture/approach, different -- own or synthetic -- example domain) is the safest path to a public portfolio piece.

One-line description: A conversational assistant that converts natural-language problem descriptions into structured optimization models, built with FastAPI, React, and an LLM backend.

## Project Overview

This project explores using an LLM as the front end to an optimization pipeline: instead of requiring users to formally specify an optimization problem, the assistant holds a conversation to incrementally extract the concepts, constraints, and parameters needed, then emits a structured (JSON) representation for a downstream optimization solver.

## Problem Statement

Missing -- please provide. What optimization domain was this built for (e.g. production scheduling, resource allocation, routing)? What made manual problem specification a bottleneck for the intended users?

## Key Features

Natural-language-to-structured-optimization-model conversion. A conversational workflow that incrementally identifies concepts, validates input, and collects parameters. A REST API connecting a React frontend to an LLM-backed Python service. Structured JSON output designed for downstream optimization tooling.

## System Architecture

```
User (React frontend)
        |  conversational input
        v
 FastAPI backend
        |  prompts / conversation state
        v
 LLM (GPT)
        |  extracted concepts & parameters
        v
 Structured JSON output --> downstream optimization model/solver
```

Missing -- please confirm this is accurate, and add detail on how conversation state is managed, how validation works (rule-based checks on top of LLM output?), and what "downstream optimization" actually consumes the JSON (is a solver included in this repo, or is that out of scope?).

## Technologies

Backend: Python, FastAPI. Frontend: React. LLM: GPT (missing -- which provider/model? OpenAI API directly, or Azure OpenAI? -- matters for install instructions and for accurately describing the stack). Communication: REST APIs.

## Dataset

Not a traditional ML dataset. Missing -- please provide any details on prompt engineering, few-shot examples, or evaluation conversations used during development, if there's anything shareable.

## Methodology

Design a conversational flow to elicit optimization concepts from unstructured natural language, use an LLM (with prompting/validation logic) to extract and incrementally validate parameters, collect and structure the final output as JSON, then hand off the structured output to a downstream optimization step.

Missing -- please provide: actual prompt design approach, validation logic details, and how correctness of extracted parameters is checked before hand-off.

## Installation

Missing -- needs input once the codebase exists in a publishable form (API keys, environment variables, frontend/backend setup steps).

## Usage

Missing -- needs input. At minimum, how to start the FastAPI backend and React frontend locally, and a sample conversation showing the assistant in action.

## Project Structure

Recommended structure for a FastAPI + React project like this:

```
llm-optimization-assistant/
├── README.md
├── LICENSE
├── .gitignore
├── backend/
│   ├── requirements.txt
│   ├── app/            # FastAPI routes, LLM integration, conversation logic
│   ├── configs/
│   └── tests/
├── frontend/
│   ├── package.json
│   └── src/
└── docs/                # architecture notes, example conversation transcripts
```

## Results

Missing -- do not publish without real evidence. No results have been provided, so none are included here. Worth considering what's demonstrable and shareable: example conversation transcripts, accuracy of parameter extraction on a test set of prompts, or qualitative before/after comparisons.

## Evaluation Metrics

Missing -- please provide. Was this evaluated quantitatively (e.g. extraction accuracy against a labeled set of example requests) or only qualitatively/informally? Either is fine to state honestly -- it just needs to be accurate.

## Example Outputs

Missing -- please provide, ideally a sample conversation transcript and the resulting structured JSON output, using a generic (non-client) example problem.

## Limitations

Missing -- please provide. Worth being explicit about: LLM reliability/hallucination risk in parameter extraction, what happens on ambiguous input, and any constraints on problem complexity the assistant can handle.

## Future Improvements

Missing -- please provide.

## License

MIT - see LICENSE.

## Author

Preeti Sharma - Research Assistant, AI & Industrial Automation, Fraunhofer IOSB-INA, Lemgo, Germany.
