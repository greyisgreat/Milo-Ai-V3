"""
M.I.L.O — Machine Intelligence Liaison Operator
src/core/self_healer.py

Self-Healing Engine.
Captures OperationResult failures, sends them to the Brain (Gemini),
receives a proposed code patch, optionally applies it, and retries.
"""

from __future__ import annotations

import textwrap
import re
import importlib
import sys
import types
from typing import Callable, Any

import google.generativeai as genai

from src.tools.system_ops import OperationResult, execute


# ──────────────────────────────────────────────────────────────────────────────
# Prompt builder
# ──────────────────────────────────────────────────────────────────────────────

_HEAL_PROMPT_TEMPLATE = textwrap.dedent("""
    You are the self-healing core of M.I.L.O., an AI assistant.
    A system operation just failed. Your job is to:
    1. Diagnose the root cause clearly.
    2. Propose a minimal, safe Python code patch that fixes it.
    3. Return ONLY a JSON object with this exact shape:

    {{
      "diagnosis": "<one-sentence root cause>",
      "patch_description": "<what the patch does>",
      "patched_code": "<complete corrected Python function as a string, or null if no patch is possible>",
      "safe_to_auto_apply": <true|false>
    }}

    Do NOT include any markdown fences or extra text. Return raw JSON only.

    --- FAILED ACTION ---
    Action   : {action}
    Arguments: {kwargs}

    --- ERROR ---
    {error}

    --- TRACEBACK ---
    {traceback}

    --- ORIGINAL SOURCE ---
    {source}
""")


# ──────────────────────────────────────────────────────────────────────────────
# Self-Healer
# ──────────────────────────────────────────────────────────────────────────────

class SelfHealer:
    """
    Wraps any system operation call.
    On failure → sends context to Gemini → receives patch → optionally retries.
    """

    def __init__(self, gemini_model: genai.GenerativeModel, auto_apply: bool = False):
        """
        Args:
            gemini_model: An initialised Gemini GenerativeModel instance.
            auto_apply:   If True, auto-apply patches marked safe_to_auto_apply.
                          Keep False in production until you trust the patch quality.
        """
        self.model = gemini_model
        self.auto_apply = auto_apply
        self._patch_log: list[dict] = []

    # ── Public API ────────────────────────────────────────────────────────────

    def run(self, action: str, max_retries: int = 1, **kwargs) -> OperationResult:
        """
        Execute an action. If it fails, invoke the healing cycle.
        Returns the final OperationResult (healed or still-failed).
        """
        result = execute(action, **kwargs)

        if result.success:
            return result

        for attempt in range(max_retries):
            print(f"[SelfHealer] Attempt {attempt + 1}: healing '{action}'…")
            heal_result = self._heal_cycle(action, result, kwargs)

            if heal_result is None:
                break  # Brain couldn't produce a patch

            # If auto_apply is on and patch is safe, re-execute
            if self.auto_apply and heal_result.get("safe_to_auto_apply"):
                patched_fn = self._load_patch(action, heal_result.get("patched_code", ""))
                if patched_fn:
                    retry = self._call_patched(patched_fn, **kwargs)
                    if retry.success:
                        return retry
                    result = retry  # feed updated failure back for next cycle
            else:
                # Surface the diagnosis back to the caller as structured data
                return OperationResult.fail(
                    error=result.error,
                    tb=result.raw_traceback,
                )

        return result

    def get_patch_log(self) -> list[dict]:
        """Return a history of all heal attempts and their patches."""
        return list(self._patch_log)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _heal_cycle(self, action: str, failed: OperationResult, kwargs: dict) -> dict | None:
        """Send failure to Gemini, parse and return the heal payload."""
        source = self._get_source(action)
        prompt = _HEAL_PROMPT_TEMPLATE.format(
            action=action,
            kwargs=kwargs,
            error=failed.error or "",
            traceback=failed.raw_traceback or "",
            source=source,
        )

        try:
            response = self.model.generate_content(prompt)
            raw = response.text.strip()
            # Strip accidental markdown fences
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)

            import json
            payload = json.loads(raw)
            self._patch_log.append({"action": action, "kwargs": kwargs, **payload})
            print(f"[SelfHealer] Diagnosis: {payload.get('diagnosis')}")
            return payload

        except Exception as e:
            print(f"[SelfHealer] Brain response parse failed: {e}")
            return None

    def _get_source(self, action: str) -> str:
        """Try to retrieve the source code of the failing handler."""
        import inspect
        from src.tools.system_ops import DISPATCH_TABLE
        fn = DISPATCH_TABLE.get(action)
        if fn:
            try:
                return inspect.getsource(fn)
            except Exception:
                pass
        return "(source unavailable)"

    def _load_patch(self, action: str, code: str) -> Callable | None:
        """
        Dynamically compile a patched function from a code string.
        Returns the callable or None on failure.
        """
        if not code:
            return None
        try:
            namespace: dict[str, Any] = {}
            exec(compile(code, "<patch>", "exec"), namespace)  # noqa: S102
            # Assume the patch defines a function with the same name as the action
            fn_name = action.split("_")[0]  # heuristic: first segment
            for name, obj in namespace.items():
                if callable(obj) and not name.startswith("_"):
                    return obj
        except Exception as e:
            print(f"[SelfHealer] Patch compile failed: {e}")
        return None

    def _call_patched(self, fn: Callable, **kwargs) -> OperationResult:
        """Call the dynamically-loaded patched function safely."""
        try:
            result = fn(**kwargs)
            if isinstance(result, OperationResult):
                return result
            return OperationResult.ok(data=result)
        except Exception as e:
            import traceback as tb_mod
            return OperationResult.fail(error=str(e), tb=tb_mod.format_exc())
