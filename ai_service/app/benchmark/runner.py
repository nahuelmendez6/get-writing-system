"""Asynchronous Benchmark Runner for multimodal and digital Cambridge writing evaluations."""

import json
from pathlib import Path
from typing import Any

from app.benchmark.metrics import (
    compute_benchmark_summary,
    evaluate_single_sample_discrepancies,
)
from app.core.image_processing import encode_image_to_base64, strip_exif
from app.core.logging import logger
from app.graph.pipeline import run_evaluation_pipeline
from app.schemas.benchmark import (
    BenchmarkCriterionScores,
    BenchmarkEvaluationResult,
    BenchmarkReportSummary,
    BenchmarkSample,
)
from app.schemas.request import EvaluationRequest
from app.schemas.response import EvaluationResponse


class BenchmarkRunner:
    """Orchestrates loading benchmark samples and evaluating them through LangGraph."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.dataset_dir: Path = self.base_dir

    def load_dataset(
        self, source: str | Path | list[dict[str, Any]]
    ) -> list[BenchmarkSample]:
        """Loads and parses benchmark samples from a JSON file path or raw dictionary list."""
        if isinstance(source, (str, Path)):
            file_path = Path(source)
            if not file_path.is_absolute():
                if not file_path.exists() and (self.base_dir / file_path).exists():
                    file_path = self.base_dir / file_path
                elif not file_path.exists() and (self.base_dir.parent / file_path).exists():
                    file_path = self.base_dir.parent / file_path
            self.dataset_dir = file_path.parent
            logger.info("Loading benchmark dataset from %s", file_path)
            with open(file_path, encoding="utf-8") as f:
                raw_data = json.load(f)
        else:
            raw_data = source

        samples: list[BenchmarkSample] = []
        for item in raw_data:
            samples.append(BenchmarkSample.model_validate(item))

        logger.info("Loaded %d benchmark samples successfully", len(samples))
        return samples

    async def evaluate_sample(
        self, sample: BenchmarkSample
    ) -> BenchmarkEvaluationResult:
        """Executes the full evaluation pipeline for a single sample (image or text)."""
        image_b64: str | None = sample.image_base64

        # If sample specifies an image path on disk, load and encode it
        if not image_b64 and sample.image_path:
            candidate_paths = [
                self.dataset_dir / sample.image_path,
                self.base_dir / sample.image_path,
                Path(sample.image_path),
            ]
            img_file = next((p for p in candidate_paths if p.exists()), None)

            if img_file and img_file.exists():
                with open(img_file, "rb") as f:
                    raw_img_bytes = f.read()
                sanitized_bytes, _ = strip_exif(raw_img_bytes)
                image_b64 = encode_image_to_base64(sanitized_bytes)
            else:
                logger.warning(
                    "Image file %s not found. Falling back to student_text.",
                    sample.image_path,
                )

        req = EvaluationRequest(
            submission_id=sample.id,
            student_text=sample.student_text or "",
            image_base64=image_b64,
            task_prompt=sample.prompt,
            level=sample.cefr_level,
            text_type=sample.task_type,
            min_words=sample.min_words,
            max_words=sample.max_words,
        )

        response: EvaluationResponse = await run_evaluation_pipeline(req)

        # Extract criteria scores from rubric_evaluation
        crit_dict: dict[str, float] = {
            c.name.lower(): c.score for c in response.rubric_evaluation.criteria
        }

        ai_scores = BenchmarkCriterionScores(
            content=crit_dict.get("content", 3.0),
            communicative_achievement=crit_dict.get(
                "communicative achievement",
                crit_dict.get("communicative_achievement", 3.0),
            ),
            organisation=crit_dict.get("organisation", 3.0),
            language=crit_dict.get("language", 3.0),
            raw_score=response.rubric_evaluation.raw_score,
            institutional_score=response.rubric_evaluation.institutional_score,
        )

        extracted_text = response.extracted_text or sample.student_text or ""

        return evaluate_single_sample_discrepancies(
            sample_id=sample.id,
            cefr_level=sample.cefr_level,
            task_type=sample.task_type,
            ocr_applied=response.ocr_applied,
            extracted_text=extracted_text,
            ai_scores=ai_scores,
            human_scores=sample.human_scores,
            length_penalty_predicted=response.rubric_evaluation.length_penalty,
            length_penalty_expected=sample.expected_length_penalty,
            ai_generated_predicted=response.ai_detection.is_likely_ai,
            ai_generated_expected=sample.expected_ai_generated,
        )

    async def run_batch(
        self,
        samples: list[BenchmarkSample],
        level_filter: str | None = None,
        task_type_filter: str | None = None,
    ) -> BenchmarkReportSummary:
        """Executes the benchmark over a filtered list of writing samples."""
        filtered = samples
        if level_filter:
            filtered = [
                s for s in filtered if s.cefr_level.upper() == level_filter.upper()
            ]
        if task_type_filter:
            filtered = [
                s for s in filtered if s.task_type.lower() == task_type_filter.lower()
            ]

        logger.info(
            "Executing benchmark for %d samples (filter: level=%s)",
            len(filtered),
            level_filter,
        )

        results: list[BenchmarkEvaluationResult] = []
        for sample in filtered:
            res = await self.evaluate_sample(sample)
            results.append(res)

        return compute_benchmark_summary(results)


async def run_benchmark(
    source: str | Path | list[dict[str, Any]],
    level_filter: str | None = None,
    task_type_filter: str | None = None,
    base_dir: str | Path | None = None,
) -> BenchmarkReportSummary:
    """Convenience helper to load and execute benchmark in a single call."""
    runner = BenchmarkRunner(base_dir=base_dir)
    samples = runner.load_dataset(source)
    return await runner.run_batch(
        samples=samples, level_filter=level_filter, task_type_filter=task_type_filter
    )


def generate_markdown_report(summary: BenchmarkReportSummary) -> str:
    """Generates an executive GitHub-flavored markdown report from the summary."""
    verdict_badge = (
        "**PASSED (APPROVED)**" if summary.passed else "**FAILED (REJECTED)**"
    )

    md = [
        "# Benchmark Report: AI Writing Assessment Precision",
        "",
        "## 1. Executive Summary",
        f"- **Verdict**: {verdict_badge}",
        f"- **Total Samples Evaluated**: `{summary.total_samples}`",
        f"- **Samples with Human Ground Truth**: `{summary.evaluated_with_human_ground_truth}`",
        f"- **Multimodal / OCR Samples Processed**: `{summary.ocr_processed_count}`",
        f"- **Global Mean Absolute Error (MAE)**: `{summary.overall_mae:.3f}` bands (Target: $\\le 0.50$)",
        f"- **Accuracy within $\\pm 1$ Band**: `{summary.overall_within_one_band_pct:.1f}%` (Target: $\\ge 80.0\\%$)",
        f"- **Exact Match Rate**: `{summary.overall_exact_match_pct:.1f}%`",
        "",
        "## 2. Metrics by Cambridge Criterion",
        "",
        "| Criterion | MAE (Bands) | Within $\\pm 1$ Band % | Exact Match % | Max Error |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    for name, m in summary.criteria_metrics.items():
        md.append(
            f"| **{name}** | `{m.mae:.3f}` | `{m.within_one_band_pct:.1f}%` | `{m.exact_match_pct:.1f}%` | `{m.max_error:.1f}` |"
        )

    md.extend(
        [
            "",
            "## 3. Breakdown by CEFR Proficiency Level",
            "",
            "| Level | Samples | MAE (Bands) | Within $\\pm 1$ Band % |",
            "| :--- | :--- | :--- | :--- |",
        ]
    )

    for lvl, metrics in summary.level_breakdown.items():
        md.append(
            f"| **{lvl}** | `{int(metrics['sample_count'])}` | `{metrics['mae']:.3f}` | `{metrics['within_one_band_pct']:.1f}%` |"
        )

    md.extend(
        [
            "",
            "## 4. Acceptance Criteria Verification",
            f"- [{'x' if summary.overall_mae <= 0.5 else ' '}] **MAE $\\le 0.50$**: Achieved `{summary.overall_mae:.3f}`.",
            f"- [{'x' if summary.overall_within_one_band_pct >= 80.0 else ' '}] **$\\pm 1$ Band Concordance $\\ge 80\\%$**: Achieved `{summary.overall_within_one_band_pct:.1f}%`.",
            "",
        ]
    )

    return "\n".join(md)
