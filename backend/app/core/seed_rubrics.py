from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rubric import Rubric, RubricCriterion

CAMBRIDGE_B2_RUBRIC_DATA: dict[str, Any] = {
    "name": "Cambridge B2 First General Rubric",
    "cefr_level": "B2",
    "description": (
        "Official Cambridge English scale for B2 First writing assessment "
        "covering Content, Communicative Achievement, Organisation and "
        "Language across Bands 0 to 5."
    ),
    "is_template": True,
    "is_active": True,
    "criteria": [
        {
            "name": "Content",
            "description": "Focuses on task fulfillment and relevance of ideas.",
            "weight": 1.0,
            "max_band": 5,
            "sort_order": 0,
            "descriptors": {
                "5": (
                    "All content is relevant to the task. "
                    "Target reader is fully informed."
                ),
                "4": "Performance shares features of Bands 3 and 5.",
                "3": (
                    "Minor irrelevances and/or omissions may be present. "
                    "Target reader is on the whole informed."
                ),
                "2": "Performance shares features of Bands 1 and 3.",
                "1": (
                    "Irrelevances and/or misinterpretation of task may be "
                    "present. Target reader is minimally informed."
                ),
                "0": "Content is totally irrelevant. Target reader is not informed.",
            },
        },
        {
            "name": "Communicative Achievement",
            "description": (
                "Focuses on register, tone, genre conventions and communicative "
                "purpose."
            ),
            "weight": 1.0,
            "max_band": 5,
            "sort_order": 1,
            "descriptors": {
                "5": (
                    "Uses the conventions of the communicative task effectively "
                    "to hold the target reader's attention and communicate "
                    "straightforward and complex ideas, as appropriate."
                ),
                "4": "Performance shares features of Bands 3 and 5.",
                "3": (
                    "Uses the conventions of the communicative task to hold "
                    "the target reader's attention and communicate straightforward "
                    "ideas."
                ),
                "2": "Performance shares features of Bands 1 and 3.",
                "1": "Produces text that communicates simple ideas in simple ways.",
                "0": "Performance below Band 1.",
            },
        },
        {
            "name": "Organisation",
            "description": (
                "Focuses on coherence, logical sequencing and cohesive devices."
            ),
            "weight": 1.0,
            "max_band": 5,
            "sort_order": 2,
            "descriptors": {
                "5": (
                    "Text is well-organised and coherent, using a variety of "
                    "cohesive devices and organisational patterns to generally "
                    "good effect."
                ),
                "4": "Performance shares features of Bands 3 and 5.",
                "3": (
                    "Text is generally well-organised and coherent, using a "
                    "variety of linking words and cohesive devices."
                ),
                "2": "Performance shares features of Bands 1 and 3.",
                "1": (
                    "Text is connected and coherent, using basic linking "
                    "words and a limited number of cohesive devices."
                ),
                "0": "Performance below Band 1.",
            },
        },
        {
            "name": "Language",
            "description": (
                "Focuses on vocabulary range/accuracy and grammatical "
                "complexity/control."
            ),
            "weight": 1.0,
            "max_band": 5,
            "sort_order": 3,
            "descriptors": {
                "5": (
                    "Uses a range of everyday vocabulary, including less common "
                    "lexis, appropriately. Uses a range of simple and complex "
                    "grammatical forms with control and flexibility. Occasional "
                    "errors may be present but do not impede communication."
                ),
                "4": "Performance shares features of Bands 3 and 5.",
                "3": (
                    "Uses everyday vocabulary appropriately, with occasional "
                    "inappropriate choice of less common lexis. Uses a range "
                    "of simple and some complex grammatical forms with a good "
                    "degree of control. Errors do not impede communication."
                ),
                "2": "Performance shares features of Bands 1 and 3.",
                "1": (
                    "Uses basic vocabulary appropriately of isolated words and "
                    "phrases. Uses simple grammatical forms with a degree of "
                    "control. Errors may impede meaning at times."
                ),
                "0": "Performance below Band 1.",
            },
        },
    ],
}

CAMBRIDGE_C1_RUBRIC_DATA: dict[str, Any] = {
    "name": "Cambridge C1 Advanced General Rubric",
    "cefr_level": "C1",
    "description": (
        "Official Cambridge English scale for C1 Advanced writing assessment "
        "covering Content, Communicative Achievement, Organisation and "
        "Language across Bands 0 to 5."
    ),
    "is_template": True,
    "is_active": True,
    "criteria": [
        {
            "name": "Content",
            "description": (
                "Focuses on complex task fulfillment, relevant depth and precision."
            ),
            "weight": 1.0,
            "max_band": 5,
            "sort_order": 0,
            "descriptors": {
                "5": (
                    "All content is relevant to the task. "
                    "Target reader is fully informed."
                ),
                "4": "Performance shares features of Bands 3 and 5.",
                "3": (
                    "Minor irrelevances and/or omissions may be present. "
                    "Target reader is on the whole informed."
                ),
                "2": "Performance shares features of Bands 1 and 3.",
                "1": (
                    "Irrelevances and/or misinterpretation of task may be "
                    "present. Target reader is minimally informed."
                ),
                "0": "Content is totally irrelevant. Target reader is not informed.",
            },
        },
        {
            "name": "Communicative Achievement",
            "description": (
                "Focuses on sophisticated tone, flexibility and rhetorical purpose."
            ),
            "weight": 1.0,
            "max_band": 5,
            "sort_order": 1,
            "descriptors": {
                "5": (
                    "Uses the conventions of the communicative task with "
                    "sufficient flexibility to communicate complex ideas in "
                    "an effective way, holding the target reader's attention "
                    "with ease, fulfilling all communicative purposes."
                ),
                "4": "Performance shares features of Bands 3 and 5.",
                "3": (
                    "Uses the conventions of the communicative task effectively "
                    "to hold the target reader's attention and communicate "
                    "straightforward and complex ideas, as appropriate."
                ),
                "2": "Performance shares features of Bands 1 and 3.",
                "1": (
                    "Uses the conventions of the communicative task to hold "
                    "the target reader's attention and communicate "
                    "straightforward ideas."
                ),
                "0": "Performance below Band 1.",
            },
        },
        {
            "name": "Organisation",
            "description": (
                "Focuses on sophisticated cohesive progression and structural "
                "complexity."
            ),
            "weight": 1.0,
            "max_band": 5,
            "sort_order": 2,
            "descriptors": {
                "5": (
                    "Text is a well-organised, coherent whole, using a variety "
                    "of cohesive devices and organisational patterns with "
                    "flexibility."
                ),
                "4": "Performance shares features of Bands 3 and 5.",
                "3": (
                    "Text is well-organised and coherent, using a variety of "
                    "cohesive devices and organisational patterns to generally "
                    "good effect."
                ),
                "2": "Performance shares features of Bands 1 and 3.",
                "1": (
                    "Text is generally well-organised and coherent, using a "
                    "variety of linking words and cohesive devices."
                ),
                "0": "Performance below Band 1.",
            },
        },
        {
            "name": "Language",
            "description": (
                "Focuses on advanced lexical nuance, idiomatic resource and "
                "syntactic control."
            ),
            "weight": 1.0,
            "max_band": 5,
            "sort_order": 3,
            "descriptors": {
                "5": (
                    "Uses a wide range of vocabulary, including less common "
                    "and sophisticated lexis, with style and nuance. Uses a "
                    "wide range of simple and complex grammatical forms with "
                    "full control, flexibility and sophistication. Errors are "
                    "rare and non-impeding."
                ),
                "4": "Performance shares features of Bands 3 and 5.",
                "3": (
                    "Uses a range of vocabulary, including less common lexis, "
                    "appropriately and effectively. Uses a range of simple "
                    "and complex grammatical forms with control and flexibility. "
                    "Occasional non-impeding errors."
                ),
                "2": "Performance shares features of Bands 1 and 3.",
                "1": (
                    "Uses everyday vocabulary appropriately, with occasional "
                    "inappropriate choice of less common lexis. Uses simple "
                    "and some complex grammatical forms with a good degree of "
                    "control. Errors do not impede communication."
                ),
                "0": "Performance below Band 1.",
            },
        },
    ],
}


def get_default_rubric_templates() -> list[dict[str, Any]]:
    """Return Cambridge default template definitions for B2 First and C1 Advanced."""
    return [CAMBRIDGE_B2_RUBRIC_DATA, CAMBRIDGE_C1_RUBRIC_DATA]


async def seed_default_rubrics(db: AsyncSession) -> list[Rubric]:
    """Idempotently seed Cambridge B2 and C1 rubrics into the database."""
    seeded: list[Rubric] = []
    templates = get_default_rubric_templates()

    for item in templates:
        query = select(Rubric).where(
            Rubric.name == item["name"],
            Rubric.cefr_level == item["cefr_level"],
            Rubric.is_template.is_(True),
        )
        result = await db.execute(query)
        existing = result.scalar_one_or_none()

        if existing is not None:
            seeded.append(existing)
            continue

        rubric = Rubric(
            name=item["name"],
            cefr_level=item["cefr_level"],
            description=item["description"],
            is_template=item["is_template"],
            is_active=item["is_active"],
        )

        for c_data in item["criteria"]:
            criterion = RubricCriterion(
                name=c_data["name"],
                description=c_data.get("description"),
                weight=c_data.get("weight", 1.0),
                max_band=c_data.get("max_band", 5),
                sort_order=c_data.get("sort_order", 0),
                descriptors=c_data.get("descriptors", {}),
            )
            rubric.criteria.append(criterion)

        db.add(rubric)
        await db.flush()
        await db.refresh(rubric)
        seeded.append(rubric)

    await db.commit()
    return seeded
