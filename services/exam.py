import logging
from typing import List, Dict
from core.llm_fast import OllamaLLM

logger = logging.getLogger(__name__)

class ExamGenerator:
    """Generate exam questions and MCQs from lecture content."""
    
    def __init__(self):
        """Initialize exam generator with LLM."""
        self.llm = OllamaLLM()
    
    def generate_short_answer_questions(self, text: str, num_questions: int = 5) -> List[str]:
        """
        Generate short answer exam questions.
        
        Args:
            text: Lecture content
            num_questions: Number of questions to generate
        
        Returns:
            List of questions
        """
        try:
            logger.info(f"Generating {num_questions} short answer questions...")
            
            prompt = f"""Generate {num_questions} short answer exam questions based on the following lecture content.
Questions should be clear, specific, and answerable in 2-3 sentences.
Return only the questions, one per line.

Lecture Content:
{text[:2000]}

Questions:"""
            
            response = self.llm.generate(prompt, temperature=0.5, max_tokens=500)
            
            questions = []
            for line in response.split('\n'):
                line = line.strip()
                if line and len(line) > 10 and (line.endswith('?') or line[0].isdigit()):
                    # Remove numbering
                    question = line.lstrip('0123456789.-) ').strip()
                    if question not in questions:
                        questions.append(question)
            
            return questions[:num_questions]
        
        except Exception as e:
            logger.error(f"Error generating short answer questions: {e}")
            return []
    
    def generate_multiple_choice(self, text: str, num_questions: int = 5) -> List[Dict]:
        """
        Generate multiple choice questions with 4 options.

        Args:
            text: Lecture content
            num_questions: Number of MCQs

        Returns:
            List of MCQ dicts
        """
        try:
            logger.info(f"Generating {num_questions} multiple choice questions...")

            prompt = f"""Generate {num_questions} multiple choice questions based on the lecture content.
Each question should have 4 options (A, B, C, D) and indicate the correct answer.
Follow these guidelines:
- ONE and ONLY ONE correct answer
- Plausible but incorrect distractors (wrong answers)
- All options similar in length and complexity
- Avoid "all of the above" and "none of the above"
- No double negatives
- Clear, concise question stem
- Options in logical order (usually A=best answer)
- Test understanding, not just memorization
- Difficulty: 40% Easy, 40% Medium, 20% Hard

Format each MCQ as:
Q: [question text]
A) [option A]
B) [option B]
C) [option C]
D) [option D]
Answer: [correct letter]

Lecture Content:
{text[:2000]}

MCQs:"""

            response = self.llm.generate(prompt, temperature=0.5, max_tokens=800)

            mcqs = []
            current_q = None

            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('Q:'):
                    if current_q:
                        mcqs.append(current_q)
                    current_q = {
                        "question": line[2:].strip(),
                        "options": [],
                        "answer": None
                    }
                elif current_q and line.startswith(('A)', 'B)', 'C)', 'D)')):
                    current_q["options"].append(line[2:].strip())
                elif current_q and line.startswith('Answer:'):
                    current_q["answer"] = line.split(':')[1].strip().upper()

            if current_q:
                mcqs.append(current_q)

            # Validate MCQs
            valid_mcqs = []
            for mcq in mcqs:
                if (mcq.get("question") and len(mcq.get("options", [])) == 4 and mcq.get("answer") in ['A', 'B', 'C', 'D']):
                    valid_mcqs.append(mcq)

            return valid_mcqs[:num_questions]

        except Exception as e:
            logger.error(f"Error generating MCQs: {e}")
            return []
    
    def generate_true_false(self, text: str, num_questions: int = 5) -> List[Dict]:
        """
        Generate true/false questions.
        
        Args:
            text: Lecture content
            num_questions: Number of questions
        
        Returns:
            List of T/F questions with answers
        """
        try:
            logger.info(f"Generating {num_questions} true/false questions...")
            
            prompt = f"""Generate {num_questions} True/False exam questions based on the lecture content.
Format each as:
T/F: [statement]
Answer: [True/False]

Some statements should be true, others false.

Lecture Content:
{text[:2000]}

Questions:"""
            
            response = self.llm.generate(prompt, temperature=0.5, max_tokens=600)
            
            questions = []
            current_q = None
            
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('T/F:'):
                    if current_q:
                        questions.append(current_q)
                    current_q = {
                        "statement": line[4:].strip(),
                        "answer": None
                    }
                elif current_q and line.startswith('Answer:'):
                    answer_text = line.split(':')[1].strip().upper()
                    current_q["answer"] = "True" if "TRUE" in answer_text else "False"
            
            if current_q:
                questions.append(current_q)
            
            return questions[:num_questions]
        
        except Exception as e:
            logger.error(f"Error generating T/F questions: {e}")
            return []
    
    def generate_essay_prompts(self, text: str, num_prompts: int = 3) -> List[str]:
        """
        Generate essay question prompts.
        
        Args:
            text: Lecture content
            num_prompts: Number of prompts
        
        Returns:
            List of essay prompts
        """
        try:
            logger.info(f"Generating {num_prompts} essay prompts...")
            
            prompt = f"""Generate {num_prompts} thought-provoking essay question prompts based on the lecture content.
Questions should require critical thinking and understanding of concepts.
Return only the prompts, one per line.

Lecture Content:
{text[:2000]}

Essay Prompts:"""
            
            response = self.llm.generate(prompt, temperature=0.6, max_tokens=500)
            
            prompts = []
            for line in response.split('\n'):
                line = line.strip()
                if line and len(line) > 15:
                    prompt_text = line.lstrip('0123456789.-) ').strip()
                    if prompt_text not in prompts:
                        prompts.append(prompt_text)
            
            return prompts[:num_prompts]
        
        except Exception as e:
            logger.error(f"Error generating essay prompts: {e}")
            return []
    

    
    def generate_practice_test(self, text: str) -> Dict:
        """
        Generate complete practice test with mixed question types.
        
        Returns:
            Dict with all question types
        """
        try:
            logger.info("Generating complete practice test...")
            
            return {
                "short_answer": self.generate_short_answer_questions(text, 5),
                "multiple_choice": self.generate_multiple_choice(text, 5),
                "true_false": self.generate_true_false(text, 5),
                "essay": self.generate_essay_prompts(text, 3)
            }
        
        except Exception as e:
            logger.error(f"Error generating practice test: {e}")
            return {}
