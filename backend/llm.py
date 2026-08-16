"""
llm.py -- LLM connector

Thin wrapper around an OpenAI-compatible chat model, used throughout the
app via:

    llm = LLM(params)
    reply = llm.query(prompt)

All configuration (API key, base URL, model name) is read from environment
variables -- see .env.example. No credentials are hardcoded in this file.
Point OPENAI_API_BASE at any OpenAI-compatible endpoint (OpenAI itself,
Azure OpenAI, a local proxy, etc.) to switch providers without touching
the rest of the codebase.
"""

import math
import os

from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI


class LLM:
    """
    Minimal LLM connector used by main.py.

    params (dict, all optional):
        model            -- model name (default: env LLM_MODEL, else "gpt-4o-mini")
        reasoning        -- optional dict passed through to the provider,
                             e.g. {"effort": "medium"} for reasoning models
        request_timeout  -- request timeout in seconds (default: 60.0)
        max_retries      -- retries on transient failures (default: 3)
    """

    def __init__(self, params=None):
        params = params or {}

        self.model = params.get("model", os.getenv("LLM_MODEL", "gpt-4o-mini"))
        self.reasoning = params.get("reasoning")
        self.request_timeout = params.get("request_timeout", 60.0)
        self.max_retries = params.get("max_retries", 3)

        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE")  # optional

        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Copy backend/.env.example to "
                "backend/.env and fill in your own credentials."
            )

        self._client = self._build()

    # -- accessors -----------------------------------------------------

    def get_model(self):
        return self.model

    def get_reasoning(self):
        return self.reasoning

    def get_request_timeout(self):
        return self.request_timeout

    def get_max_retries(self):
        return self.max_retries

    # -- internals -------------------------------------------------------

    def _build(self):
        """Construct the underlying llama-index LLM client."""
        kwargs = {
            "model": self.model,
            "api_key": self.api_key,
            "timeout": self.request_timeout,
            "max_retries": self.max_retries,
        }
        if self.api_base:
            kwargs["api_base"] = self.api_base
        if self.reasoning:
            kwargs["reasoning_effort"] = self.reasoning.get("effort")

        return OpenAI(**kwargs)

    # -- public API --------------------------------------------------------

    def query(self, prompt, log_probs=None):
        """
        Send a single-turn prompt to the configured model and return the
        plain-text reply.

        log_probs: optional list of candidate strings. If provided, the
        model is queried with logprobs enabled and the normalized
        probability mass over those candidates is returned as a dict
        instead of free-form text -- useful for small fixed-choice
        classification calls.
        """
        messages = [ChatMessage(role="user", content=prompt)]

        if log_probs:
            response = self._client.chat(
                messages,
                logprobs=True,
                top_logprobs=max(5, len(log_probs)),
            )
            return self._aggregate_logprobs(response, log_probs)

        response = self._client.chat(messages)
        return response.message.content

    def _aggregate_logprobs(self, response, candidates):
        """
        Aggregate probability mass over a small set of candidate
        tokens/words from a logprobs-enabled response and return the
        normalized distribution.
        """
        try:
            top = response.raw["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
        except (KeyError, IndexError, TypeError):
            return {c: 0.0 for c in candidates}

        scores = {c: 0.0 for c in candidates}
        for entry in top:
            token = entry.get("token", "").strip().lower()
            for c in candidates:
                if token == c.strip().lower():
                    scores[c] += math.exp(entry.get("logprob", float("-inf")))

        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        return scores
