import requests
import json
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaLLM:
    """
    Stable & production-safe Ollama LLM wrapper
    """

    def __init__(
        self,
        model: str = "mistral:latest",
        base_url: str = "http://localhost:11434",
        timeout: int = 300
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_endpoint = f"{self.base_url}/api/generate"
        self.available = False

        self._check_connection_and_model()

    def _check_connection_and_model(self):
        """Check Ollama server + model availability."""
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            r.raise_for_status()

            models = [m["name"] for m in r.json().get("models", [])]

            if self.model not in models:
                raise RuntimeError(
                    f"Model '{self.model}' not found. Available models: {models}"
                )

            self.available = True
            logger.info(f"✓ Ollama connected | Model loaded: {self.model}")

        except Exception as e:
            logger.error(f"✗ Ollama not ready: {e}")
            self.available = False

    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 500) -> str:
        """Generate text safely."""
        if not self.available:
            return "[Ollama not available]"

        if not prompt or not prompt.strip():
            return "[Empty prompt]"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": False
        }

        try:
            r = requests.post(self.api_endpoint, json=payload, timeout=self.timeout)
            r.raise_for_status()

            text = r.json().get("response", "").strip()
            return text if text else "[Empty response from model]"

        except requests.exceptions.Timeout:
            return "[Ollama timeout]"
        except Exception as e:
            logger.exception("Generation error")
            return f"[Generation error: {e}]"
            
    def stream_generate(self, prompt: str, temperature: float = 0.3):
        """Stream tokens from Ollama."""
        if not self.available or not prompt.strip():
            yield "[Streaming unavailable]"
            return

        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": True
        }

        try:
            with requests.post(
                self.api_endpoint,
                json=payload,
                timeout=self.timeout,
                stream=True
            ) as r:
                r.raise_for_status()

                for line in r.iter_lines():
                    if line:
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        if chunk:
                            yield chunk

        except Exception as e:
            yield f"[Stream error: {e}]"

    # -------------------------------------------------
    def summarize(self, text: str, max_length: int = 200) -> str:
        if not text.strip():
            return "[No text to summarize]"

        prompt = f"""
Summarize the following text in {max_length} tokens or less:

{text}

Summary:
"""
        return self.generate(prompt, temperature=0.3, max_tokens=max_length)

    def extract_key_points(self, text: str, num_points: int = 5) -> List[str]:
        if not text.strip():
            return ["[No text provided]"]

        prompt = f"""
Extract {num_points} clear key points as bullet points:

{text}
"""

        response = self.generate(prompt, temperature=0.2, max_tokens=400)

        points = [
            line.strip("-•0123456789. ").strip()
            for line in response.splitlines()
            if line.strip()
        ]

        return points[:num_points]

    def generate_questions(self, text: str, num_questions: int = 3) -> List[str]:
        if not text.strip():
            return ["[No text provided]"]

        prompt = f"""
Generate {num_questions} exam questions:

{text}
"""

        response = self.generate(prompt, temperature=0.5, max_tokens=400)

        return [
            q.strip("-•0123456789. ").strip()
            for q in response.splitlines()
            if len(q.strip()) > 10
        ][:num_questions]

    def generate_mcq(self, text: str, num_questions: int = 3) -> List[dict]:
        if not text.strip():
            return []

        prompt = f"""
Generate {num_questions} MCQs with answers:

{text}
"""

        response = self.generate(prompt, temperature=0.5, max_tokens=800)

        mcqs = []
        current = None

        for line in response.splitlines():
            line = line.strip()

            if line.startswith("Q"):
                if current:
                    mcqs.append(current)
                current = {"question": line[2:].strip(), "options": [], "answer": None}

            elif current and line[:2] in ("A)", "B)", "C)", "D)"):
                current["options"].append(line[2:].strip())

            elif current and line.lower().startswith("answer"):
                current["answer"] = line.split(":")[-1].strip()

        if current:
            mcqs.append(current)

        return mcqs[:num_questions]
