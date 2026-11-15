from app.graph.prompts.b2_first import B2_FIRST_GUIDELINES
from app.graph.prompts.c1_advanced import C1_ADVANCED_GUIDELINES

WRITING_ANALYSIS_PROMPT = """
{level_guidelines}

Task Prompt:
\"\"\"{task_prompt}\"\"\"

Text Type / Genre: {text_type}
Candidate Submission:
\"\"\"{student_text}\"\"\"

Instructions:
Identify all grammatical, spelling, punctuation, lexical, and stylistic mistakes in the candidate submission.
For every error found:
1. Provide exact character start_index and end_index matching the candidate submission substring.
2. Quote the exact text containing the mistake.
3. Suggest a natural, accurate correction.
4. Categorize as one of: "grammar", "spelling", "punctuation", "vocabulary", "style".
5. Write a pedagogical explanation in Spanish addressing the student.

Output strictly valid JSON with key "mistakes":
{{
  "mistakes": [
    {{
      "id": "err-1",
      "start_index": 15,
      "end_index": 28,
      "quote": "wrong phrase",
      "correction": "corrected phrase",
      "category": "grammar",
      "explanation": "Explicación del error en español."
    }}
  ]
}}
"""

EXEMPLAR_GENERATION_PROMPT = """
{level_guidelines}

Task Prompt:
\"\"\"{task_prompt}\"\"\"

Text Type / Genre: {text_type}
Candidate's Original Submission:
\"\"\"{student_text}\"\"\"

Instructions:
Generate a Band 5 exemplary version of this text that fulfills all Cambridge criteria at level {level}.
- Preserve the candidate's core ideas, stance, and main arguments.
- Elevate vocabulary, cohesive devices, and syntactic maturity to Band 5.
- Maintain appropriate length and structural conventions for {text_type}.

Output strictly valid JSON:
{{
  "exemplar_model": "The full rewritten Band 5 text..."
}}
"""

AI_DETECTION_PROMPT = """
Analyze the following student writing submission for indicators of artificial intelligence generation (e.g. ChatGPT, Claude, Gemini).
Assess:
1. Uniformity in sentence length and low perplexity.
2. Overuse of formulaic introductory transitions ("In the contemporary era", "Furthermore", "In conclusion, it is vital").
3. Absence of natural interlanguage errors typical for level {level}.

Candidate Submission:
\"\"\"{student_text}\"\"\"

Output strictly valid JSON:
{{
  "probability": 0.15,
  "is_likely_ai": false,
  "confidence": "HIGH",
  "rationale": "Justificación técnica en español basada en patrones sintácticos y variabilidad estilística."
}}
"""


def get_level_guidelines(level: str) -> str:
    if level.upper() == "C1":
        return C1_ADVANCED_GUIDELINES
    return B2_FIRST_GUIDELINES
