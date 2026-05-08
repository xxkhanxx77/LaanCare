import json
import os
import time

import requests


class GeminiClient:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.disabled_by_env = os.environ.get("GEMINI_DISABLED", "0") == "1"
        self.enabled = bool(self.api_key) and not self.disabled_by_env
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def status(self):
        reason = ""
        if self.disabled_by_env:
            reason = "GEMINI_DISABLED=1"
        elif not self.api_key:
            reason = "GEMINI_API_KEY is missing"
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
                "error": "GEMINI_API_KEY not set or GEMINI_DISABLED=1",
                "data": None,
                "raw_text": "",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "latency_ms": 0,
            }
        body = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        }
        url = self.endpoint.format(model=self.model)
        started = time.time()
        try:
            response = requests.post(
                url,
                headers={"x-goog-api-key": self.api_key},
                json=body,
                timeout=30,
            )
            latency_ms = int((time.time() - started) * 1000)
            if response.status_code >= 400:
                return {
                    "ok": False,
                    "skipped": False,
                    "purpose": purpose,
                    "error": "Gemini HTTP {0}: {1}".format(response.status_code, response.text[:500]),
                    "data": None,
                    "raw_text": response.text[:2000],
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                    "latency_ms": latency_ms,
                }
            payload = response.json()
            raw_text = self._extract_text(payload)
            data = json.loads(raw_text) if raw_text else {}
            usage = self._usage(payload)
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

    def _extract_text(self, payload):
        candidates = payload.get("candidates") or []
        if not candidates:
            return ""
        parts = (((candidates[0] or {}).get("content") or {}).get("parts")) or []
        return "".join(part.get("text", "") for part in parts if isinstance(part, dict)).strip()

    def _usage(self, payload):
        meta = payload.get("usageMetadata") or payload.get("usage_metadata") or {}
        prompt = meta.get("promptTokenCount", meta.get("prompt_token_count", 0)) or 0
        completion = meta.get("candidatesTokenCount", meta.get("candidates_token_count", 0)) or 0
        total = meta.get("totalTokenCount", meta.get("total_token_count", prompt + completion)) or 0
        return {
            "prompt_tokens": int(prompt),
            "completion_tokens": int(completion),
            "total_tokens": int(total),
        }
