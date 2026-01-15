from core.llm_fast import OllamaLLM

llm = OllamaLLM()

def generate_mcqs(text: str, num_questions: int = 5):
    if not text.strip():
        return []

    prompt = f"""
Generate {num_questions} multiple-choice questions (MCQs).
Each question should have 4 options (A, B, C, D) and clearly mention the correct answer.

Text:
{text}

Format:
Q1. Question?
A) Option
B) Option
C) Option
D) Option
Answer: A
"""

    response = llm.generate(prompt, temperature=0.4, max_tokens=800)

    mcqs = []
    current = None

    for line in response.splitlines():
        line = line.strip()

        if line.lower().startswith("q"):
            if current:
                mcqs.append(current)
            current = {"question": line, "options": [], "answer": ""}
        elif current and line[:2] in ("A)", "B)", "C)", "D)"):
            current["options"].append(line)
        elif current and line.lower().startswith("answer"):
            current["answer"] = line.split(":")[-1].strip()

    if current:
        mcqs.append(current)

    return mcqs
