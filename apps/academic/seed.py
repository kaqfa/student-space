"""Idempotent seeding of academic reference data. Safe to call repeatedly."""

LEVELS = [
    {"code": "SD", "name": "Sekolah Dasar", "order": 1, "grades": [1, 2, 3, 4, 5, 6]},
    {"code": "SMP", "name": "Sekolah Menengah Pertama", "order": 2, "grades": [7, 8, 9]},
]

DEFAULT_YEAR = "2025/2026"


def seed_academic_reference(EducationLevel, Grade, AcademicYear):
    """Seed levels, grades, and a default active academic year.

    Models are passed in so this works from both a management command
    (real models) and a data migration (historical apps.get_model).
    Returns a dict summary.
    """
    summary = {"levels": 0, "grades": 0, "year": None}

    for lvl in LEVELS:
        level, lcreated = EducationLevel.objects.get_or_create(
            code=lvl["code"],
            defaults={"name": lvl["name"], "order": lvl["order"]},
        )
        if lcreated:
            summary["levels"] += 1
        for n in lvl["grades"]:
            _, gcreated = Grade.objects.get_or_create(
                level=level, number=n,
                defaults={"label": f"Kelas {n}", "order": n},
            )
            if gcreated:
                summary["grades"] += 1

    year, ycreated = AcademicYear.objects.get_or_create(
        name=DEFAULT_YEAR, defaults={"is_active": True},
    )
    # ensure exactly one active year exists
    if not AcademicYear.objects.filter(is_active=True).exists():
        year.is_active = True
        year.save()
    summary["year"] = year.name
    return summary
