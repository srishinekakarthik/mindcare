# MindCare Platform — Changes Summary

## What changed

### 1. Real data models (`base/models.py`)
Added: `CounselorProfile`, `Availability`, `Session`, `SessionFeedback`, `AssessmentResult`,
`Resource`, `PeerSupportPost`, `PeerSupportComment`. Extended `UserProfile` with a 4-way
`role` field (`student` / `staff` / `counselor` / `admin`) and `is_approved` for counselor
gating. `institution` is now nullable — only required for students and staff.

### 2. Roles & permissions
- **Student / Staff**: belong to an institution.
- **Counselor**: serves everyone, no institution. Self-signup creates a pending account
  (`is_approved=False`); cannot log in until an admin approves it from
  **Manage Counselors** (`/admin-panel/counselors/`).
- **Admin**: platform-wide, never created via signup — only via
  `python manage.py createsuperuser` or the Django admin panel.
- All nav/dashboard visibility is now driven server-side via a context processor
  (`base/context_processors.py`) instead of trusting `localStorage`.

### 3. Booking (`book_session.html` + new endpoints)
Lists real approved counselors and their real open `Availability` slots. Booking calls
`/api/book-session/` which atomically claims the slot (protected against double-booking),
creates a `Session`, and supports cancellation via `/api/cancel-session/<id>/`.

### 4. Analytics dashboard (`/dashboard/`)
Computed from real data. Admins see platform-wide metrics; staff see their own
institution only, in aggregate (no individual student identities exposed).

### 5. Counselor-facing pages (new)
- `/counselor/dashboard/` — upcoming/completed sessions, ratings.
- `/counselor/availability/` — add/remove open slots.

### 6. Resources & Peer Support
Both now read/write real DB rows instead of hardcoded JS arrays. A
`python manage.py seed_resources` command seeds 10 starter resources.

### 7. Signup/login
Signup offers Student / Staff / Counselor (no Admin option). Institution field hides
itself for counselors. Login looks up the real role server-side and redirects
accordingly — no role is ever self-asserted at login.

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_resources
python manage.py createsuperuser   # for an admin account
python manage.py runserver
```

To approve a counselor account manually instead of via the UI:
```bash
python manage.py shell -c "
from base.models import UserProfile
p = UserProfile.objects.get(user__username='SOME_USERNAME')
p.is_approved = True
p.save()
"
```

## Known follow-ups (not done in this pass)
- No email notifications (booking confirmations, approval emails) — currently silent.
- No counselor profile-editing UI (bio/specialties are set via Django admin or shell).
- Peer support has no moderation UI yet beyond the `is_flagged` field on the model.
- `database/`, `docs/`, `scripts/` folders (deployment/Supabase setup helpers) were left
  untouched — out of scope for this pass.
