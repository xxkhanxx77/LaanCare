import json
import os
import time


class OpenAIJsonClient:
    """Small OpenAI JSON client for symptom screening helper calls."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()
        self.disabled_by_env = os.environ.get("OPENAI_DISABLED", "0") == "1"
        self.enabled = bool(self.api_key) and not self.disabled_by_env

    def status(self):
        reason = ""
        if self.disabled_by_env:
            reason = "OPENAI_DISABLED=1"
        elif not self.api_key:
            reason = "OPENAI_API_KEY is missing"
        return {
            "enabled": self.enabled,
            "model": self.model,
            "api_key_present": bool(self.api_key),
            "disabled_by_env": self.disabled_by_env,
            "disabled_reason": reason,
        }

    def generate_json(self, system_prompt, user_prompt, purpose):
        if not self.enabled:
            return {
                "ok": False,
                "skipped": True,
                "purpose": purpose,
                "error": "OPENAI_API_KEY not set or OPENAI_DISABLED=1",
                "data": None,
                "raw_text": "",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "latency_ms": 0,
            }

        try:
            from openai import OpenAI
        except ImportError as exc:
            return {
                "ok": False,
                "skipped": False,
                "purpose": purpose,
                "error": f"openai is not installed: {exc}",
                "data": None,
                "raw_text": "",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "latency_ms": 0,
            }

        started = time.time()
        try:
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
            )
            latency_ms = int((time.time() - started) * 1000)
            raw_text = response.choices[0].message.content or "{}"
            data = json.loads(raw_text) if raw_text else {}
            usage = self._usage(response)
            return {
                "ok": True,
                "skipped": False,
                "purpose": purpose,
                "error": "",
                "data": data,
                "raw_text": raw_text,
                "usage": usage,
                "latency_ms": latency_ms,
            }
        except Exception as exc:
            latency_ms = int((time.time() - started) * 1000)
            return {
                "ok": False,
                "skipped": False,
                "purpose": purpose,
                "error": str(exc),
                "data": None,
                "raw_text": "",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "latency_ms": latency_ms,
            }

    def _usage(self, response):
        usage = getattr(response, "usage", None)
        if not usage:
            return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        prompt = getattr(usage, "prompt_tokens", 0) or 0
        completion = getattr(usage, "completion_tokens", 0) or 0
        total = getattr(usage, "total_tokens", prompt + completion) or 0
        return {
            "prompt_tokens": int(prompt),
            "completion_tokens": int(completion),
            "total_tokens": int(total),
        }
