# Design — B2: Family & Roles

**Date:** 2026-06-26
**Refs:** [v2-upgrade-plan.md](../../v2-upgrade-plan.md) §2.1, §4 (B2) · [implementation-progress.md](../../implementation-progress.md)
**Builds on:** B1 (academic foundation) — same branch `feat/u1-b1-academic`.

Establish `Family` as the unit/tenancy root, add `tutor` role, thin parent/tutor profiles, and link the existing `ParentStudent` workflow to families. Entirely additive (🟢/🟡 expand+migrate); no contract; no UI (that is U2).

---

## Models (in `apps/accounts`)

### Family
```
name        CharField
owner       FK(User)            # the parent who owns/created the family
created_at  DateTimeField(auto_now_add)
```

### FamilyMembership (M2M through)
```
family          FK(Family, related_name="memberships")
user            FK(User, related_name="family_memberships")
role_in_family  CharField choices: parent / student / tutor
created_at      DateTimeField(auto_now_add)
unique (family, user)
```
M2M chosen over a single `User.family` FK so a student can belong to more than one family (e.g. separated parents) without a future migration.

### ParentProfile (thin)
```
user                OneToOne(User, related_name="parent_profile")
notification_prefs  JSONField(default=dict, blank=True)
phone               CharField(blank=True)   # fallback/secondary contact
```

### TutorProfile (thin)
```
user            OneToOne(User, related_name="tutor_profile")
bio             TextField(blank=True)
specialization  CharField(blank=True)
```

---

## Role: tutor

- Add `TUTOR = "tutor", _("Tutor")` to `User.Role`.
- Add `User.is_tutor` property.
- `is_parent_or_admin` unchanged (tutor is not parent/admin).

## Link ParentStudent → Family (expand + migrate)

- Expand: add `family = FK("accounts.Family", null=True, blank=True, on_delete=SET_NULL, related_name="parent_student_links")` to `ParentStudent`.
- Migrate (reversible data migration): for each distinct `parent` appearing in `ParentStudent`:
  1. `Family.objects.get_or_create(owner=parent, defaults={"name": f"Keluarga {parent.get_full_name() or parent.username}"})`.
  2. `FamilyMembership` for the parent (role=parent) and for each linked student (role=student), idempotent via get_or_create.
  3. Set `ParentStudent.family` on that parent's links.
- Reverse: delete created FamilyMemberships + Families, null out `ParentStudent.family`.

## Helper

- `User.family` property → first `Family` via membership (`self.family_memberships.first().family`) or None. (Multi-family selection UI is U2+; one is enough now.)

## Admin

- `FamilyAdmin`: list_display (name, owner, member count); `FamilyMembership` inline; search by name/owner.
- `FamilyMembershipAdmin`: list_display, list_filter (role_in_family), autocomplete user/family.
- `ParentProfileAdmin`, `TutorProfileAdmin`: simple, search by user.
- `ParentStudentAdmin`: add `family` to list_display/list_filter.

## Seed (permission groups)

Extend `seed_initial_data` `GROUP_PERMS["user_manager"]` with: `("accounts","family")`, `("accounts","familymembership")`, `("accounts","parentprofile")`, `("accounts","tutorprofile")`. content_manager/finance unchanged. (Defensive lookup already tolerates missing perms.)

## Tests (`apps/accounts/tests/`)

- Family + FamilyMembership creation; `unique (family, user)` enforced.
- `role_in_family` choices accepted.
- `User.is_tutor` true for tutor role.
- `User.family` returns the family for a member, None otherwise.
- Backfill: a parent with two linked students yields one Family, 3 memberships (1 parent + 2 students), and the links' `family` set. Reversible.
- ParentProfile / TutorProfile OneToOne round-trip.

Run via existing `.venv-test` venv (Django 5.0.14 + pytest-django, settings `config.settings.development`). All existing 120 tests must still pass.

## Out of scope
- UI for families / year switcher / dashboard → U2.
- Tutor custom UI → none (Django Admin only, per ui-improvement-plan).
- Subscription tie to Family → B7.
- Removing legacy `grade:int` → B8.

## Execution
Same-session inline (subagent dispatch unreliable under current session limits). TDD per task, frequent commits, on branch `feat/u1-b1-academic`.
