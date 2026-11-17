"""Command-Line Interface (CLI) for multimodal writing assessment, OCR testing, and benchmark execution."""

import argparse
import asyncio
import sys
from pathlib import Path

from app.benchmark.runner import BenchmarkRunner, generate_markdown_report
from app.core.image_processing import encode_image_to_base64, strip_exif
from app.graph.pipeline import run_evaluation_pipeline
from app.schemas.request import EvaluationRequest
from app.schemas.response import EvaluationResponse


def format_header(title: str) -> str:
    line = "=" * 70
    return f"\n{line}\n  {title}\n{line}"


def format_subheader(title: str) -> str:
    line = "-" * 50
    return f"\n{title}\n{line}"


async def evaluate_single_file(
    image_path: str | None,
    text: str | None,
    level: str,
    text_type: str,
    prompt: str,
    min_words: int | None,
    max_words: int | None,
) -> None:
    """Evaluates a single writing sample (either handwritten photo or digital text) and displays rich results."""
    image_b64: str | None = None
    if image_path:
        img_p = Path(image_path)
        if not img_p.exists():
            print(f"Error: Image file '{image_path}' does not exist.")
            sys.exit(1)
        print(f"📸 Loading and sanitizing image: {img_p.resolve()}")
        with open(img_p, "rb") as f:
            raw_bytes = f.read()
        sanitized_bytes, meta = strip_exif(raw_bytes)
        image_b64 = encode_image_to_base64(sanitized_bytes)
        print(
            f"   Image format: {meta['sanitized_format']} | Dimensions: {meta['width']}x{meta['height']} | EXIF stripped: {meta['exif_stripped']}"
        )

    req = EvaluationRequest(
        submission_id="cli-eval-001",
        student_text=text or "",
        image_base64=image_b64,
        task_prompt=prompt,
        level=level.upper(),  # type: ignore[arg-type]
        text_type=text_type.lower(),  # type: ignore[arg-type]
        min_words=min_words,
        max_words=max_words,
    )

    print("\n⏳ Running LangGraph evaluation pipeline...")
    response: EvaluationResponse = await run_evaluation_pipeline(req)

    # 1. OCR Section
    if response.ocr_applied:
        print(format_header("1. MULTIMODAL OCR LITERAL TRANSCRIPTION"))
        print(
            "Fidelidad: Transcripción literal estricta (sin autocorregir faltas del alumno)"
        )
        print("-" * 70)
        print(response.extracted_text)
        print("-" * 70)
        print(f"Total palabras extraídas: {response.word_count}")

    # 2. Detected Errors
    print(format_header("2. DETECTED MISTAKES & LINGUISTIC ANALYSIS"))
    if not response.mistakes:
        print("  ✓ No grammar, spelling, or lexical mistakes found (Band 5 mastery).")
    else:
        for idx, m in enumerate(response.mistakes, 1):
            print(
                f"  [{idx}] '{m.quote}' ➔ '{m.correction}' ({m.category.upper()}) [Offset {m.start_index}:{m.end_index}]"
            )
            print(f"      Nota pedagógica: {m.explanation}")

    # 3. Cambridge Rubrics & Grades
    print(format_header("3. CAMBRIDGE 4-BAND RUBRICS & INSTITUTIONAL SCORE"))
    print(f"{'Criterio':<30} | {'Banda (0-5)':<12} | {'Descriptor'}")
    print("-" * 70)
    for c in response.rubric_evaluation.criteria:
        desc_preview = (
            (c.band_descriptor[:45] + "...")
            if len(c.band_descriptor) > 45
            else c.band_descriptor
        )
        print(f"{c.name:<30} | {c.score:<12.1f} | {desc_preview}")
    print("-" * 70)
    print(
        f"Puntuación Bruta (Raw Score): {response.rubric_evaluation.raw_score:.1f} / 20.0"
    )
    print(
        f"Calificación Institucional:   {response.rubric_evaluation.institutional_score:.1f} / 10.0"
    )
    if response.rubric_evaluation.length_penalty:
        print(
            f"⚠️  Penalización por longitud: ACTIVADA (Estado: {response.rubric_evaluation.word_count_status})"
        )

    # 4. Pedagogical Feedback
    print(format_header("4. PEDAGOGICAL FEEDBACK FOR STUDENT"))
    print(f"Resumen General:\n  {response.feedback.overall_feedback}\n")
    print("Fortalezas Clave:")
    for s in response.feedback.strengths:
        print(f"  + {s}")
    print("\nÁreas de Mejora:")
    for a in response.feedback.areas_for_improvement:
        print(f"  - {a}")
    print("\nConsejos Accionables (Tips):")
    for idx, tip in enumerate(response.feedback.actionable_tips, 1):
        print(f"  {idx}. {tip}")

    # 5. Exemplar Model
    print(format_header("5. BAND 5 EXEMPLARY REWRITE MODEL"))
    print(response.exemplar_model)
    print(
        f"\n⏱️  Tiempo de ejecución: {response.execution_time_seconds:.2f}s | Estado: {response.status}\n"
    )


async def evaluate_dataset(
    dataset_path: str,
    level_filter: str | None,
    task_type_filter: str | None,
    output_json: str | None,
    output_md: str | None,
) -> None:
    """Executes benchmark over a dataset and outputs summary statistics and reports."""
    print(format_header("CAMBRIDGE WRITING EVALUATION BENCHMARK"))
    print(f"Dataset path: {dataset_path}")
    if level_filter:
        print(f"Filter Level: {level_filter}")
    if task_type_filter:
        print(f"Filter Type:  {task_type_filter}")

    runner = BenchmarkRunner()
    samples = runner.load_dataset(dataset_path)

    print(f"Starting batch evaluation of {len(samples)} samples...")
    summary = await runner.run_batch(
        samples, level_filter=level_filter, task_type_filter=task_type_filter
    )

    # Display console summary table
    print(format_header("BENCHMARK EXECUTION RESULTS"))
    verdict_str = "PASSED (APPROVED)" if summary.passed else "FAILED (REJECTED)"
    print(f"VEREDICTO:                 {verdict_str}")
    print(f"Total redacciones:         {summary.total_samples}")
    print(
        f"Muestras contrastadas (Docente): {summary.evaluated_with_human_ground_truth}"
    )
    print(f"Muestras OCR Multimodal:   {summary.ocr_processed_count}")
    print(
        f"MAE Global (Desviación):   {summary.overall_mae:.3f} bandas (Meta: <= 0.50)"
    )
    print(
        f"Acierto en +-1 Banda:      {summary.overall_within_one_band_pct:.1f}% (Meta: >= 80.0%)"
    )
    print(f"Acierto Exacto de Banda:   {summary.overall_exact_match_pct:.1f}%")

    print(format_subheader("MÉTRICAS POR CRITERIO DE CAMBRIDGE"))
    print(f"{'Criterio':<28} | {'MAE':<8} | {'+-1 Banda %':<12} | {'Acierto Exacto %'}")
    print("-" * 65)
    for name, m in summary.criteria_metrics.items():
        print(
            f"{name:<28} | {m.mae:<8.3f} | {m.within_one_band_pct:<12.1f} | {m.exact_match_pct:.1f}%"
        )

    print(format_subheader("DESGLOSE POR NIVEL MCER"))
    print(f"{'Nivel':<10} | {'Muestras':<10} | {'MAE':<8} | {'+-1 Banda %'}")
    print("-" * 45)
    for lvl, metrics in summary.level_breakdown.items():
        print(
            f"{lvl:<10} | {int(metrics['sample_count']):<10} | {metrics['mae']:<8.3f} | {metrics['within_one_band_pct']:.1f}%"
        )

    # Export reports if requested
    if output_md:
        md_content = generate_markdown_report(summary)
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"\n📄 Markdown report written to: {output_md}")

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            f.write(summary.model_dump_json(indent=2))
        print(f"📊 JSON report written to: {output_json}")

    print("\n" + "=" * 70)
    if not summary.passed:
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Get Idiomas Cambridge Writing Assessment CLI & Benchmark Runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="Path to a student handwritten writing photo (JPEG/PNG)",
    )
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="Student writing text (for direct digital testing)",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="Path to benchmark dataset JSON file",
    )
    parser.add_argument(
        "--level",
        type=str,
        default="B2",
        choices=["B1", "B2", "C1", "C2"],
        help="Cambridge target level",
    )
    parser.add_argument(
        "--type",
        dest="text_type",
        type=str,
        default="essay",
        choices=[
            "essay",
            "article",
            "email",
            "review",
            "report",
            "story",
            "proposal",
        ],
        help="Text genre / assignment type",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="In your English class, you have been talking about advantages and disadvantages of remote working. Write an essay discussing whether remote working is positive for society.",
        help="Assignment prompt and instructions",
    )
    parser.add_argument(
        "--min-words",
        type=int,
        default=140,
        help="Minimum required words",
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=190,
        help="Maximum required words",
    )
    parser.add_argument(
        "--output-md",
        type=str,
        default=None,
        help="Path to export Markdown report",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default=None,
        help="Path to export JSON report",
    )

    args = parser.parse_args()

    if args.dataset:
        asyncio.run(
            evaluate_dataset(
                dataset_path=args.dataset,
                level_filter=args.level if "--level" in sys.argv else None,
                task_type_filter=args.text_type if "--type" in sys.argv else None,
                output_json=args.output_json,
                output_md=args.output_md,
            )
        )
    elif args.image or args.text:
        asyncio.run(
            evaluate_single_file(
                image_path=args.image,
                text=args.text,
                level=args.level,
                text_type=args.text_type,
                prompt=args.prompt,
                min_words=args.min_words,
                max_words=args.max_words,
            )
        )
    else:
        # Default behavior: run benchmark dataset in ai_service/data/benchmark/dataset.json
        default_dataset = Path("ai_service/data/benchmark/dataset.json")
        if not default_dataset.exists():
            default_dataset = Path("data/benchmark/dataset.json")

        if default_dataset.exists():
            asyncio.run(
                evaluate_dataset(
                    dataset_path=str(default_dataset),
                    level_filter=None,
                    task_type_filter=None,
                    output_json=args.output_json,
                    output_md=args.output_md,
                )
            )
        else:
            parser.print_help()
            print("\nPlease provide either --image, --text, or --dataset to execute.")


if __name__ == "__main__":
    main()
