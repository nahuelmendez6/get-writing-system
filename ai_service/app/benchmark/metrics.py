"""Mathematical and statistical metrics calculation for Cambridge writing benchmarks."""

from collections.abc import Sequence

from app.schemas.benchmark import (
    BenchmarkCriterionScores,
    BenchmarkEvaluationResult,
    BenchmarkReportSummary,
    CriterionMetricSummary,
)

# Threshold targets according to RF-08 & Backlog QA-01
TARGET_MAX_MAE = 0.50
TARGET_MIN_WITHIN_ONE_BAND_PCT = 80.0


def evaluate_single_sample_discrepancies(
    sample_id: str,
    cefr_level: str,
    task_type: str,
    ocr_applied: bool,
    extracted_text: str,
    ai_scores: BenchmarkCriterionScores,
    human_scores: BenchmarkCriterionScores | None,
    length_penalty_predicted: bool,
    length_penalty_expected: bool | None = None,
    ai_generated_predicted: bool = False,
    ai_generated_expected: bool | None = None,
) -> BenchmarkEvaluationResult:
    """Computes criterion-by-criterion absolute errors and band agreement for one sample."""
    criterion_errors: dict[str, float] = {}
    raw_error: float | None = None
    inst_error: float | None = None
    exact_matches = 0
    within_one_band_matches = 0

    if human_scores is not None:
        criteria_pairs = [
            ("content", human_scores.content, ai_scores.content),
            (
                "communicative_achievement",
                human_scores.communicative_achievement,
                ai_scores.communicative_achievement,
            ),
            ("organisation", human_scores.organisation, ai_scores.organisation),
            ("language", human_scores.language, ai_scores.language),
        ]

        for name, human_val, ai_val in criteria_pairs:
            err = round(abs(human_val - ai_val), 2)
            criterion_errors[name] = err
            if err == 0.0:
                exact_matches += 1
            if err <= 1.0:
                within_one_band_matches += 1

        raw_error = round(abs(human_scores.raw_score - ai_scores.raw_score), 2)
        inst_error = round(
            abs(human_scores.institutional_score - ai_scores.institutional_score), 2
        )

    return BenchmarkEvaluationResult(
        sample_id=sample_id,
        cefr_level=cefr_level,
        task_type=task_type,
        ocr_applied=ocr_applied,
        extracted_text=extracted_text,
        human_scores=human_scores,
        ai_scores=ai_scores,
        criterion_errors=criterion_errors,
        raw_score_error=raw_error,
        institutional_score_error=inst_error,
        exact_matches=exact_matches,
        within_one_band_matches=within_one_band_matches,
        length_penalty_predicted=length_penalty_predicted,
        length_penalty_expected=length_penalty_expected,
        ai_generated_predicted=ai_generated_predicted,
        ai_generated_expected=ai_generated_expected,
    )


def calculate_criterion_metrics(
    criterion_name: str, pairs: Sequence[tuple[float, float]]
) -> CriterionMetricSummary:
    """Computes MAE, MSE, % exact match, and % within +-1 band for a single criterion."""
    if not pairs:
        return CriterionMetricSummary(
            criterion=criterion_name,
            mae=0.0,
            mse=0.0,
            exact_match_pct=100.0,
            within_one_band_pct=100.0,
            max_error=0.0,
        )

    n = len(pairs)
    abs_errors = [abs(human - ai) for human, ai in pairs]
    sq_errors = [(human - ai) ** 2 for human, ai in pairs]

    mae = round(sum(abs_errors) / n, 3)
    mse = round(sum(sq_errors) / n, 3)
    exact_count = sum(1 for err in abs_errors if err == 0.0)
    within_one_count = sum(1 for err in abs_errors if err <= 1.0)
    max_err = round(max(abs_errors), 2)

    return CriterionMetricSummary(
        criterion=criterion_name,
        mae=mae,
        mse=mse,
        exact_match_pct=round((exact_count / n) * 100.0, 1),
        within_one_band_pct=round((within_one_count / n) * 100.0, 1),
        max_error=max_err,
    )


def compute_benchmark_summary(
    results: list[BenchmarkEvaluationResult],
) -> BenchmarkReportSummary:
    """Aggregates individual evaluation results into a comprehensive statistical benchmark report."""
    total_samples = len(results)
    ocr_processed = sum(1 for r in results if r.ocr_applied)
    evaluated_with_truth = [r for r in results if r.human_scores is not None]

    if not evaluated_with_truth:
        return BenchmarkReportSummary(
            total_samples=total_samples,
            evaluated_with_human_ground_truth=0,
            levels_evaluated=sorted({r.cefr_level for r in results}),
            ocr_processed_count=ocr_processed,
            overall_mae=0.0,
            overall_within_one_band_pct=100.0,
            overall_exact_match_pct=100.0,
            passed=True,
            criteria_metrics={},
            level_breakdown={},
            detailed_results=results,
        )

    # Collect pairs per criterion
    content_pairs: list[tuple[float, float]] = []
    ca_pairs: list[tuple[float, float]] = []
    org_pairs: list[tuple[float, float]] = []
    lang_pairs: list[tuple[float, float]] = []
    all_pairs: list[tuple[float, float]] = []

    level_pairs: dict[str, list[tuple[float, float]]] = {}

    for r in evaluated_with_truth:
        assert r.human_scores is not None
        c_pair = (r.human_scores.content, r.ai_scores.content)
        ca_pair = (
            r.human_scores.communicative_achievement,
            r.ai_scores.communicative_achievement,
        )
        o_pair = (r.human_scores.organisation, r.ai_scores.organisation)
        l_pair = (r.human_scores.language, r.ai_scores.language)

        content_pairs.append(c_pair)
        ca_pairs.append(ca_pair)
        org_pairs.append(o_pair)
        lang_pairs.append(l_pair)
        all_pairs.extend([c_pair, ca_pair, o_pair, l_pair])

        lvl = r.cefr_level
        if lvl not in level_pairs:
            level_pairs[lvl] = []
        level_pairs[lvl].extend([c_pair, ca_pair, o_pair, l_pair])

    crit_metrics = {
        "Content": calculate_criterion_metrics("Content", content_pairs),
        "Communicative Achievement": calculate_criterion_metrics(
            "Communicative Achievement", ca_pairs
        ),
        "Organisation": calculate_criterion_metrics("Organisation", org_pairs),
        "Language": calculate_criterion_metrics("Language", lang_pairs),
    }

    # Global metrics across all criterion evaluations
    global_abs_errors = [abs(h - a) for h, a in all_pairs]
    overall_mae = round(sum(global_abs_errors) / len(global_abs_errors), 3)
    exact_total = sum(1 for err in global_abs_errors if err == 0.0)
    within_one_total = sum(1 for err in global_abs_errors if err <= 1.0)
    overall_exact_pct = round((exact_total / len(global_abs_errors)) * 100.0, 1)
    overall_within_one_pct = round(
        (within_one_total / len(global_abs_errors)) * 100.0, 1
    )

    # Breakdown by CEFR level
    level_breakdown: dict[str, dict[str, float]] = {}
    for lvl, pairs in sorted(level_pairs.items()):
        lvl_errs = [abs(h - a) for h, a in pairs]
        lvl_mae = round(sum(lvl_errs) / len(lvl_errs), 3)
        lvl_within_one = round(
            (sum(1 for err in lvl_errs if err <= 1.0) / len(lvl_errs)) * 100.0, 1
        )
        level_breakdown[lvl] = {
            "sample_count": float(len(pairs) // 4),
            "mae": lvl_mae,
            "within_one_band_pct": lvl_within_one,
        }

    # Penalty accuracy if ground truth expected
    penalties_evaluated = [
        r for r in evaluated_with_truth if r.length_penalty_expected is not None
    ]
    penalty_accuracy = (
        round(
            (
                sum(
                    1
                    for r in penalties_evaluated
                    if r.length_penalty_predicted == r.length_penalty_expected
                )
                / len(penalties_evaluated)
            )
            * 100.0,
            1,
        )
        if penalties_evaluated
        else None
    )

    # Verification of RF-08 & Backlog criteria
    passed = (overall_mae <= TARGET_MAX_MAE) and (
        overall_within_one_pct >= TARGET_MIN_WITHIN_ONE_BAND_PCT
    )

    return BenchmarkReportSummary(
        total_samples=total_samples,
        evaluated_with_human_ground_truth=len(evaluated_with_truth),
        levels_evaluated=sorted({r.cefr_level for r in results}),
        ocr_processed_count=ocr_processed,
        overall_mae=overall_mae,
        overall_within_one_band_pct=overall_within_one_pct,
        overall_exact_match_pct=overall_exact_pct,
        passed=passed,
        criteria_metrics=crit_metrics,
        level_breakdown=level_breakdown,
        penalty_accuracy_pct=penalty_accuracy,
        detailed_results=results,
    )
