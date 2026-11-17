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

RUBRIC_EVALUATION_PROMPT = """
{level_guidelines}

Task Prompt:
\"\"\"{task_prompt}\"\"\"

Text Type / Genre: {text_type}
Candidate Submission (Word Count: {word_count}, Target: {min_words}-{max_words}):
\"\"\"{student_text}\"\"\"

Instructions:
Evaluate the candidate's writing across the 4 Cambridge assessment criteria:
1. Content (0-5 band scale): Assess task completion, relevance, and development of prompt points.
2. Communicative Achievement (0-5 band scale): Assess genre conventions, register, tone, and holding reader attention.
3. Organisation (0-5 band scale): Assess paragraph structure, coherence, and cohesive devices.
4. Language (0-5 band scale): Assess vocabulary range/accuracy and grammatical control/complexity.

If word count deviates by >10% from required limits ({min_words}-{max_words}), apply a length penalty on Content.
Calculate raw_score (sum of 4 criteria, 0-20) and institutional_score ((raw_score / 20) * 10).

Output strictly valid JSON:
{{
  "criteria": [
    {{
      "name": "Content",
      "score": 4.0,
      "max_score": 5.0,
      "band_descriptor": "All content is relevant to the task.",
      "justification": "Justificación fundamentada en evidencias del texto."
    }}
  ],
  "raw_score": 16.0,
  "max_raw_score": 20.0,
  "institutional_score": 8.0,
  "length_penalty": false,
  "word_count_status": "NORMAL"
}}
"""

FEEDBACK_GENERATION_PROMPT = """
You are an expert Cambridge English writing tutor providing constructive pedagogical feedback in Spanish.
Target Level: {level}
Text Type: {text_type}
Institutional Score: {institutional_score}/10.0

Student Text:
\"\"\"{student_text}\"\"\"

Evaluation Summary:
- Content Band: {content_score}
- Communicative Achievement Band: {ca_score}
- Organisation Band: {org_score}
- Language Band: {lang_score}

Instructions:
Generate structured pedagogical feedback in Spanish:
1. overall_feedback: Constructive evaluation of competence and communicative efficacy.
2. strengths: 2 to 4 specific positive aspects observed in the writing.
3. areas_for_improvement: 2 to 4 priority development areas.
4. actionable_tips: Exactly 3 practical recommendations for future writings.

Output strictly valid JSON:
{{
  "overall_feedback": "Resumen cualitativo en español...",
  "strengths": ["Fortaleza 1", "Fortaleza 2"],
  "areas_for_improvement": ["Área 1", "Área 2"],
  "actionable_tips": ["Tip 1", "Tip 2", "Tip 3"]
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
