# Optimization chat Assistant

A conversational assistant that converts natural-language problem descriptions into structured optimization models, built with FastAPI, React, and an LLM backend.

## Project Overview

This project explores using an LLM as the front end to an optimization pipeline: instead of requiring users to formally specify an optimization problem, the assistant holds a conversation to incrementally extract the concepts, constraints, and parameters needed, then emits a structured (JSON) representation for a downstream optimization solver.

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


## Technologies

Backend: Python, FastAPI. Frontend: React. LLM: GPT  Azure OpenAI  Communication: REST APIs.


## Methodology

Design a conversational flow to elicit optimization concepts from unstructured natural language, use an LLM (with prompting/validation logic) to extract and incrementally validate parameters, collect and structure the final output as JSON, then hand off the structured output to a downstream optimization step.






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




Preeti Sharma - Research Assistant, AI & Industrial Automation, Fraunhofer IOSB-INA, Lemgo, Germany.

