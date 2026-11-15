from app.graph.prompts.b2_first import B2_FIRST_GUIDELINES
from app.graph.prompts.c1_advanced import C1_ADVANCED_GUIDELINES
from app.graph.prompts.templates import (
    AI_DETECTION_PROMPT,
    EXEMPLAR_GENERATION_PROMPT,
    WRITING_ANALYSIS_PROMPT,
    get_level_guidelines,
)


def test_level_guidelines_selection() -> None:
    assert get_level_guidelines("B2") == B2_FIRST_GUIDELINES
    assert get_level_guidelines("b2") == B2_FIRST_GUIDELINES
    assert get_level_guidelines("C1") == C1_ADVANCED_GUIDELINES
    assert get_level_guidelines("c1") == C1_ADVANCED_GUIDELINES
    # Default fallback
    assert get_level_guidelines("B1") == B2_FIRST_GUIDELINES


def test_writing_analysis_prompt_formatting() -> None:
    prompt = WRITING_ANALYSIS_PROMPT.format(
        level_guidelines=B2_FIRST_GUIDELINES,
        task_prompt="Write an article about sports.",
        text_type="article",
        student_text="Sports are very important in daily life.",
    )
    assert "Sports are very important in daily life." in prompt
    assert "article" in prompt
    assert "start_index" in prompt


def test_exemplar_generation_prompt_formatting() -> None:
    prompt = EXEMPLAR_GENERATION_PROMPT.format(
        level_guidelines=C1_ADVANCED_GUIDELINES,
        task_prompt="Write a proposal for environmental sustainability.",
        text_type="proposal",
        level="C1",
        student_text="We need more solar panels.",
    )
    assert "proposal" in prompt
    assert "Band 5" in prompt
    assert "solar panels" in prompt


def test_ai_detection_prompt_formatting() -> None:
    prompt = AI_DETECTION_PROMPT.format(
        level="B2",
        student_text="Candidate text to inspect.",
    )
    assert "Candidate text to inspect." in prompt
    assert "probability" in prompt
