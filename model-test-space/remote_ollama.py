from __future__ import annotations

import json
from typing import Iterator, Optional

import requests


class RemoteOllamaClient:
    def __init__(
        self,
        base_url: str,
        model: str = "gemma4:e4b",
        timeout: int = 300,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.headers = {
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true",
        }

    def health(self) -> dict:
        r = requests.get(
            f"{self.base_url}/api/tags",
            headers={"ngrok-skip-browser-warning": "true"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        num_predict: int = 256,
        temperature: float = 0.7,
    ) -> str:
        payload = {
            "model": model or self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": num_predict,
                "temperature": temperature,
            },
        }

        if system:
            payload["system"] = system

        r = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            headers=self.headers,
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("response", "")

    def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        num_predict: int = 256,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        payload = {
            "model": model or self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_predict": num_predict,
                "temperature": temperature,
            },
        }

        if system:
            payload["system"] = system

        with requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            headers=self.headers,
            timeout=self.timeout,
            stream=True,
        ) as r:
            r.raise_for_status()

            for line in r.iter_lines():
                if not line:
                    continue

                data = json.loads(line.decode("utf-8"))
                piece = data.get("response", "")
                if piece:
                    yield piece

                if data.get("done"):
                    break