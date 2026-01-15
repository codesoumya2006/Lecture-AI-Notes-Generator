import logging
from typing import List
from core.llm_fast import OllamaLLM

logger = logging.getLogger(__name__)

class NotesGenerator:
    """Generate structured notes from transcribed text."""
    
    def __init__(self):
        """Initialize notes generator with LLM."""
        self.llm = OllamaLLM()
    
    def generate_structured_notes(self, text: str) -> str:
        """
        Generate structured notes from text.
        
        Returns:
            Formatted notes with sections
        """
        try:
            logger.info("Generating structured notes...")
            
            prompt = """Based on the following lecture content, create well-organized, concise study notes with clear sections and bullet points. Format should be:

## Key Topics
- Topic 1
- Topic 2
...

## Main Concepts
- Concept 1: Brief explanation
- Concept 2: Brief explanation
...

## Important Points to Remember
- Point 1
- Point 2
...

Lecture Content:
{text}

Study Notes:""".format(text=text[:2000])  # Limit context
            
            notes = self.llm.generate(prompt, temperature=0.3, max_tokens=1000)
            return notes
        
        except Exception as e:
            logger.error(f"Error generating notes: {e}")
            return "Error generating notes"
    
    def generate_summary(self, text: str, length: str = "medium") -> str:
        """
        Generate summary of different lengths.
        
        Args:
            text: Text to summarize
            length: 'short' (50 words), 'medium' (150 words), 'long' (300 words)
        
        Returns:
            Summarized text
        """
        try:
            length_map = {
                "short": 50,
                "medium": 150,
                "long": 300
            }
            
            max_tokens = length_map.get(length, 150)
            
            prompt = f"""Provide a {length} summary of the following text in approximately {max_tokens} words.

Text:
{text[:2000]}

Summary:"""
            
            summary = self.llm.generate(prompt, temperature=0.3, max_tokens=max_tokens + 50)
            return summary
        
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return ""
    
    def extract_definitions(self, text: str) -> dict:
        """
        Extract definitions and explanations of key terms.
        
        Returns:
            Dict of term -> definition
        """
        try:
            prompt = """Extract and define 5-10 key technical terms or concepts from the following text.
Format as:
Term: Definition

Text:
{text}

Definitions:""".format(text=text[:2000])
            
            response = self.llm.generate(prompt, temperature=0.2, max_tokens=500)
            
            definitions = {}
            for line in response.split('\n'):
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        term = parts[0].strip()
                        definition = parts[1].strip()
                        if term and definition:
                            definitions[term] = definition
            
            return definitions
        
        except Exception as e:
            logger.error(f"Error extracting definitions: {e}")
            return {}
    
    def generate_study_guide(self, text: str) -> str:
        """
        Generate comprehensive study guide.
        
        Returns:
            Formatted study guide
        """
        try:
            logger.info("Generating study guide...")
            
            prompt = """Create a comprehensive study guide for exam preparation based on this lecture content.
Include:
1. Overview
2. Key Concepts (with explanations)
3. Important Formulas/Rules
4. Common Mistakes to Avoid
5. Practice Topics

Lecture Content:
{text}

Study Guide:""".format(text=text[:2000])
            
            guide = self.llm.generate(prompt, temperature=0.3, max_tokens=1500)
            return guide
        
        except Exception as e:
            logger.error(f"Error generating study guide: {e}")
            return ""
    
    def extract_key_points(self, text: str, num_points: int = 10) -> List[str]:
        """
        Extract key points from text.
        
        Returns:
            List of key points
        """
        try:
            return self.llm.extract_key_points(text, num_points)
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return []
