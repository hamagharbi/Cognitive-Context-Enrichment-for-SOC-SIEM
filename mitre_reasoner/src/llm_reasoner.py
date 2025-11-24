import os
import json
from typing import List
from dotenv import load_dotenv
from groq import Groq
from .models import MitreTechnique, MitreTechniqueResponse

load_dotenv()

class LLMReasoner:
    def __init__(self):
        # Initialize Groq client
        # Ensure GROQ_API_KEY is set in environment variables
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY not found in environment variables.")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)

    def select_best_technique(self, summary: str, features: List[str], intent: str, candidates: List[MitreTechnique]) -> MitreTechniqueResponse:
        """
        Uses Groq LLM to select the best MITRE technique from candidates.
        """
        if not self.client:
            # Fallback if no API key
            best = candidates[0] if candidates else None
            return MitreTechniqueResponse(
                attack_technique=best.name if best else "Unknown",
                technique_id=best.technique_id if best else "T0000",
                tactic="Unknown",
                kill_chain_phase="Unknown",
                confidence=0.0,
                explanation="Groq API key missing. Returning top candidate.",
                related_techniques=[c.name for c in candidates[1:]] if candidates else []
            )

        # Construct context from candidates
        candidates_context = ""
        for i, tech in enumerate(candidates):
            candidates_context += f"""
            Candidate {i+1}:
            Name: {tech.name}
            ID: {tech.technique_id}
            Description: {tech.description[:300]}...
            Score: {tech.score}
            """

        prompt = f"""
        You are a cybersecurity expert. Analyze the following semantic information about a security event and map it to the most accurate MITRE ATT&CK technique from the provided candidates.

        INPUT DATA:
        - Semantic Summary: "{summary}"
        - Semantic Features: {features}
        - Intent: "{intent}"

        CANDIDATE TECHNIQUES (Retrieved from Knowledge Base):
        {candidates_context}

        TASK:
        1. Evaluate which candidate best matches the input data.
        2. Determine the Tactic and Kill Chain Phase (infer if not explicitly provided).
        3. Assign a confidence score (0.0 to 1.0).
        4. Provide a clear explanation.
        5. List other relevant techniques from the candidates.

        OUTPUT FORMAT:
        Return ONLY a valid JSON object with the following structure:
        {{
          "attack_technique": "Name of the best technique",
          "technique_id": "Txxxx",
          "tactic": "Inferred tactic (e.g., Persistence, Discovery)",
          "kill_chain_phase": "Inferred phase",
          "confidence": 0.85,
          "explanation": "Reasoning...",
          "related_techniques": ["Name of candidate 2", "Name of candidate 3"]
        }}
        """

        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful cybersecurity assistant that outputs JSON."},
                    {"role": "user", "content": prompt}
                ],
                model="qwen/qwen3-32b",
                response_format={"type": "json_object"}
            )
            
            response_content = completion.choices[0].message.content
            data = json.loads(response_content)
            
            return MitreTechniqueResponse(**data)

        except Exception as e:
            print(f"LLM Error: {e}")
            # Fallback
            best = candidates[0] if candidates else None
            return MitreTechniqueResponse(
                attack_technique=best.name if best else "Error",
                technique_id=best.technique_id if best else "Error",
                tactic="Error",
                kill_chain_phase="Error",
                confidence=0.0,
                explanation=f"LLM processing failed: {str(e)}",
                related_techniques=[]
            )

