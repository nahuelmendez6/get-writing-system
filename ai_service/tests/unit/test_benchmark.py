"""Unit tests for benchmark metrics, runner, and reporting."""

import pytest

from app.benchmark.metrics import (
    calculate_criterion_metrics,
    compute_benchmark_summary,
    evaluate_single_sample_discrepancies,
)
from app.benchmark.runner import (
    BenchmarkRunner,
    generate_markdown_report,
)
from app.schemas.benchmark import (
    BenchmarkCriterionScores,
)


def test_calculate_criterion_metrics_perfect_matches() -> None:
    pairs = [(4.0, 4.0), (3.5, 3.5), (5.0, 5.0)]
    summary = calculate_criterion_metrics("Content", pairs)

    assert summary.criterion == "Content"
    assert summary.mae == 0.0
    assert summary.mse == 0.0
    assert summary.exact_match_pct == 100.0
    assert summary.within_one_band_pct == 100.0
    assert summary.max_error == 0.0


def test_calculate_criterion_metrics_with_discrepancies() -> None:
    pairs = [(4.0, 3.5), (3.0, 4.0), (5.0, 3.0)]  # errors: 0.5, 1.0, 2.0
    summary = calculate_criterion_metrics("Language", pairs)

    # MAE = (0.5 + 1.0 + 2.0) / 3 = 1.167
    assert summary.mae == pytest.approx(1.167, 0.01)
    # Exact match: 0 / 3 = 0%
    assert summary.exact_match_pct == 0.0
    # Within 1 band: 2 / 3 = 66.7%
    assert summary.within_one_band_pct == pytest.approx(66.7, 0.1)
    assert summary.max_error == 2.0


def test_evaluate_single_sample_discrepancies() -> None:
    human = BenchmarkCriterionScores(
        content=4.0,
        communicative_achievement=4.0,
        organisation=4.0,
        language=3.5,
        raw_score=15.5,
        institutional_score=7.75,
    )
    ai = BenchmarkCriterionScores(
        content=4.0,
        communicative_achievement=3.5,
        organisation=4.0,
        language=3.0,
        raw_score=14.5,
        institutional_score=7.25,
    )

    res = evaluate_single_sample_discrepancies(
        sample_id="SAMPLE-01",
        cefr_level="B2",
        task_type="essay",
        ocr_applied=False,
        extracted_text="Some text",
        ai_scores=ai,
        human_scores=human,
        length_penalty_predicted=False,
        length_penalty_expected=False,
    )

    assert res.sample_id == "SAMPLE-01"
    assert res.criterion_errors["content"] == 0.0
    assert res.criterion_errors["communicative_achievement"] == 0.5
    assert res.criterion_errors["language"] == 0.5
    assert res.exact_matches == 2  # content & organisation
    assert res.within_one_band_matches == 4
    assert res.raw_score_error == 1.0


def test_compute_benchmark_summary_pass_thresholds() -> None:
    human = BenchmarkCriterionScores(
        content=4.0,
        communicative_achievement=4.0,
        organisation=4.0,
        language=4.0,
        raw_score=16.0,
        institutional_score=8.0,
    )
    ai_close = BenchmarkCriterionScores(
        content=4.0,
        communicative_achievement=4.0,
        organisation=4.0,
        language=3.5,
        raw_score=15.5,
        institutional_score=7.75,
    )

    res1 = evaluate_single_sample_discrepancies(
        "S1", "B2", "essay", False, "text 1", ai_close, human, False, False
    )
    res2 = evaluate_single_sample_discrepancies(
        "S2", "B2", "essay", False, "text 2", human, human, False, False
    )

    summary = compute_benchmark_summary([res1, res2])
    assert summary.total_samples == 2
    assert summary.overall_mae <= 0.50
    assert summary.overall_within_one_band_pct >= 80.0
    assert summary.passed is True


@pytest.mark.asyncio
async def test_benchmark_runner_full_dataset_execution() -> None:
    runner = BenchmarkRunner()
    samples = runner.load_dataset("ai_service/data/benchmark/dataset.json")

    assert len(samples) >= 50
    summary = await runner.run_batch(samples)

    # Acceptance criteria verification
    assert summary.total_samples == 60
    assert summary.overall_mae <= 0.50
    assert summary.overall_within_one_band_pct >= 80.0
    assert summary.passed is True
    assert summary.ocr_processed_count >= 2

    # Verify Markdown report generation
    md = generate_markdown_report(summary)
    assert "PASSED (APPROVED)" in md
    assert "Benchmark Report" in md
