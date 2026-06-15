#!/usr/bin/env python3
"""
Deterministic generator for Safari Leader's PostgreSQL seed data (seed.sql).

Every child (ids 1-70, preserved from the original seed) is given a complete,
realistic set of related records: guardian(s), authorized pickup(s), emergency
contacts, an enrollment + weekly schedule, attendance records, check-in/out
events, handoff events, documents, role assignments, and -- for a realistic
subset -- allergies, medical notes, custody restrictions and incident reports.

All foreign keys are resolved from in-memory counters, so the output is
guaranteed referentially consistent. Run:

    python scripts/generate_seed.py        # writes ../seed.sql

The output is plain SQL wrapped in a single transaction and is meant to be run
after `python manage.py migrate` against an empty (flushed) database.
"""

from __future__ import annotations

import os
import random
from datetime import date, datetime, timedelta

SEED = 42
TODAY = date(2026, 6, 14)  # matches the project's "current date"
TZ = "-04"  # US Eastern, DST

rng = random.Random(SEED)

# ---------------------------------------------------------------------------
# Static reference data (preserved from the original seed)
# ---------------------------------------------------------------------------

# (id, first, last, dob, student_status)  -- STUDENT_STATUS: A/E/S/X
CHILDREN = [
    (1, "Amara", "Johnson", "2022-03-15", "A"),
    (2, "Elijah", "Williams", "2021-08-22", "A"),
    (3, "Sofia", "Martinez", "2023-01-10", "E"),
    (4, "Noah", "Brown", "2020-11-05", "A"),
    (5, "Zara", "Davis", "2022-06-30", "A"),
    (6, "Liam", "Taylor", "2019-04-18", "A"),
    (7, "Nia", "Anderson", "2023-09-02", "E"),
    (8, "Marcus", "Thomas", "2021-12-25", "S"),
    (9, "Chloe", "Jackson", "2020-07-14", "X"),
    (10, "Jayden", "Harris", "2022-10-08", "A"),
    (11, "Avery", "Moore", "2021-02-17", "A"),
    (12, "Mason", "Clark", "2020-05-29", "A"),
    (13, "Isabella", "Rodriguez", "2023-04-12", "E"),
    (14, "Ethan", "Lee", "2019-09-21", "S"),
    (15, "Maya", "Green", "2022-12-03", "A"),
    (16, "Owen", "Bennett", "2021-07-19", "A"),
    (17, "Layla", "Brooks", "2020-01-31", "A"),
    (18, "Caleb", "Morgan", "2023-06-08", "E"),
    (19, "Harper", "Allen", "2021-11-14", "A"),
    (20, "Logan", "Parker", "2020-03-03", "A"),
    (21, "Ella", "Cook", "2022-08-22", "A"),
    (22, "Jackson", "Rivera", "2019-06-16", "S"),
    (23, "Scarlett", "Ward", "2023-02-01", "E"),
    (24, "Levi", "Torres", "2021-04-18", "A"),
    (25, "Aria", "Peterson", "2022-01-27", "A"),
    (26, "Henry", "Gray", "2020-10-09", "A"),
    (27, "Grace", "Ramirez", "2021-06-11", "A"),
    (28, "Sebastian", "Price", "2019-12-05", "S"),
    (29, "Luna", "James", "2023-07-30", "E"),
    (30, "Daniel", "Watson", "2020-09-13", "A"),
    (31, "Aaliyah", "Coleman", "2021-01-14", "A"),
    (32, "Bryson", "Mitchell", "2020-08-09", "A"),
    (33, "Camila", "Flores", "2022-03-11", "A"),
    (34, "Damien", "Reed", "2019-12-01", "S"),
    (35, "Emerson", "Bailey", "2023-05-19", "E"),
    (36, "Finley", "Cooper", "2021-06-22", "A"),
    (37, "Gianna", "Howard", "2020-04-17", "A"),
    (38, "Hudson", "Ward", "2022-11-30", "A"),
    (39, "Ivy", "Peterson", "2021-02-08", "A"),
    (40, "Jasper", "Powell", "2019-10-14", "S"),
    (41, "Kennedy", "Brooks", "2023-01-05", "E"),
    (42, "Lincoln", "Bell", "2020-09-28", "A"),
    (43, "Madeline", "Price", "2021-07-12", "A"),
    (44, "Nathan", "Barnes", "2022-02-20", "A"),
    (45, "Olive", "Murphy", "2020-05-26", "A"),
    (46, "Paisley", "Hughes", "2021-12-15", "A"),
    (47, "Quentin", "Simmons", "2019-03-03", "S"),
    (48, "Riley", "Foster", "2022-08-18", "A"),
    (49, "Sawyer", "Gonzalez", "2023-06-09", "E"),
    (50, "Talia", "Bryant", "2021-10-31", "A"),
    (51, "Uriel", "Diaz", "2020-01-25", "A"),
    (52, "Valentina", "Russell", "2022-04-13", "A"),
    (53, "Weston", "Griffin", "2021-09-07", "A"),
    (54, "Xavier", "Hayes", "2019-11-21", "S"),
    (55, "Yasmin", "Washington", "2023-03-29", "E"),
    (56, "Zayne", "Butler", "2020-07-04", "A"),
    (57, "Alina", "Perry", "2022-12-24", "A"),
    (58, "Bennett", "Long", "2021-05-10", "A"),
    (59, "Celeste", "Patterson", "2020-06-16", "A"),
    (60, "Declan", "Henderson", "2019-08-27", "S"),
    (61, "Evelyn", "Cole", "2023-02-02", "E"),
    (62, "Felix", "Jenkins", "2021-11-19", "A"),
    (63, "Genevieve", "Parker", "2020-10-05", "A"),
    (64, "Holden", "Perry", "2022-01-08", "A"),
    (65, "Isla", "Stewart", "2021-03-23", "A"),
    (66, "Jonah", "Ross", "2019-04-30", "S"),
    (67, "Kaia", "Morris", "2023-07-17", "E"),
    (68, "Lennox", "Nguyen", "2020-02-12", "A"),
    (69, "Mila", "Cook", "2022-09-01", "A"),
    (70, "Nolan", "Kelly", "2021-08-03", "A"),
]

# Programs: id -> (site_id, program_type). PS=Preschool, HD-ST=Headstart,
# PC=Precare, AS=Afterschool. (Same as facilities seed below.)
PROGRAMS = {
    1: (1, "PS"),
    2: (1, "HD-ST"),
    3: (1, "AS"),
    4: (2, "PS"),
    5: (2, "PC"),
}
# Active (non-admin) staff profile ids available to record events, per site.
SITE_STAFF = {1: [2, 3, 4], 2: [5]}

ADULT_FIRST = [
    "Denise", "Robert", "Angela", "Carlos", "Frank", "Grace", "Helen", "James",
    "Monica", "Derek", "Patricia", "Andre", "Yolanda", "Marcus", "Tanya",
    "Vincent", "Renee", "Gregory", "Sandra", "Terrence", "Lydia", "Maurice",
    "Janet", "Curtis", "Brenda", "Dwayne", "Sheila", "Reginald", "Camille",
    "Lamar", "Naomi", "Darnell", "Felicia", "Roland", "Cynthia", "Wesley",
    "Gloria", "Malik", "Rosa", "Hector", "Diana", "Omar", "Priya", "Raj",
    "Mei", "Kenji", "Sofia", "Linh", "Anh", "Ibrahim",
]
PICKUP_FIRST = [
    "Eleanor", "Walter", "Beatrice", "Harold", "Mabel", "Clifford", "Ruth",
    "Otis", "Vera", "Leon", "Esther", "Clarence", "Gladys", "Floyd", "Marie",
    "Ernest", "Pearl", "Hank", "Dolores", "Sylvester",
]

NOTIF_TYPES = ["R", "U", "C", "HR", "T"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def esc(value: str) -> str:
    """Escape a string for a single-quoted SQL literal."""
    return value.replace("'", "''")


def age_on(dob_str: str, ref: date) -> int:
    dob = date.fromisoformat(dob_str)
    years = ref.year - dob.year
    if (ref.month, ref.day) < (dob.month, dob.day):
        years -= 1
    return years


def weekdays_back(end: date, count: int):
    """Return `count` weekdays at or before `end`, oldest first."""
    days, cur = [], end
    while len(days) < count:
        if cur.weekday() < 5:  # Mon-Fri
            days.append(cur)
        cur -= timedelta(days=1)
    return list(reversed(days))


# ---------------------------------------------------------------------------
# Insert-block accumulator
# ---------------------------------------------------------------------------

class Table:
    def __init__(self, name: str, columns: list[str]):
        self.name = name
        self.columns = columns
        self.rows: list[tuple] = []

    def add(self, *values) -> int:
        self.rows.append(values)
        return values[0]  # id is always first

    def render(self) -> str:
        if not self.rows:
            return f"-- (no rows for {self.name})\n"
        cols = ", ".join(self.columns)
        lines = [f"INSERT INTO {self.name} ({cols}) VALUES"]
        rendered = []
        for row in self.rows:
            cells = []
            for val in row:
                if val is None:
                    cells.append("NULL")
                elif isinstance(val, bool):
                    cells.append("TRUE" if val else "FALSE")
                elif isinstance(val, (int, float)):
                    cells.append(str(val))
                elif isinstance(val, _Raw):
                    cells.append(val.sql)
                else:
                    cells.append("'" + esc(str(val)) + "'")
            rendered.append("  (" + ", ".join(cells) + ")")
        lines.append(",\n".join(rendered) + ";")
        seq = f"{self.name}_id_seq"
        lines.append(
            f"SELECT setval('{seq}', (SELECT MAX(id) FROM {self.name}));"
        )
        return "\n".join(lines) + "\n"


class _Raw:
    """Wrap a raw SQL expression (e.g. CURRENT_DATE) so it is not quoted."""

    def __init__(self, sql: str):
        self.sql = sql


CURRENT_DATE = _Raw("CURRENT_DATE")
CURRENT_TS = _Raw("CURRENT_TIMESTAMP")


def ts(d: date, hh: int, mm: int) -> str:
    return f"{d.isoformat()} {hh:02d}:{mm:02d}:00{TZ}"


# ---------------------------------------------------------------------------
# Counters / id allocation
# ---------------------------------------------------------------------------

USER_ID = 6           # 1-6 reserved for staff
GUARDIAN_PROFILE_ID = 0
CGR_ID = 0            # child-guardian relationship
PICKUP_ID = 0
EMERGENCY_ID = 0
ALLERGY_ID = 0
MEDNOTE_ID = 0
CUSTODY_ID = 0
ENROLLMENT_ID = 0
SCHEDULE_ID = 0
ATT_ID = 0
CIO_ID = 0
HANDOFF_ID = 0
DOC_ID = 0
ROLE_ASSIGN_ID = 13  # 1-13 used by static staff/role rows below
NOTIF_ID = 0
INCIDENT_ID = 0


def next_user():
    global USER_ID
    USER_ID += 1
    return USER_ID


# Tables that we generate dynamically
users = Table(
    "accounts_user",
    ["id", "password", "last_login", "is_staff", "is_superuser", "is_active",
     "username", "first_name", "last_name", "email", "date_joined"],
)
guardian_profiles = Table(
    "children_guardianprofile",
    ["id", "user_id", "contact_number", "is_primary_contact", "created_at"],
)
cgr = Table(
    "children_childguardianrelationship",
    ["id", "child_id", "guardian_id", "relationship", "is_primary",
     "has_custody_rights", "can_pickup", "is_active"],
)
pickups = Table(
    "children_authorizedpickupprofile",
    ["id", "child_id", "user_id", "relationship", "is_authorized", "is_active",
     "pickup_pin", "verification_notes"],
)
allergies = Table(
    "children_allergy",
    ["id", "child_id", "allergen", "severity", "instructions", "is_active"],
)
mednotes = Table(
    "children_medicalnote",
    ["id", "child_id", "note", "is_active", "date_created"],
)
custody = Table(
    "children_custodyrestriction",
    ["id", "child_id", "notes", "is_active"],
)
emergency = Table(
    "children_emergencycontact",
    ["id", "child_id", "first_name", "last_name", "contact_number",
     "relationship", "is_authorized", "is_active", "verification_notes"],
)
role_assign = Table(
    "accounts_roleassignment",
    ["id", "user_id", "role_id", "child_id", "room_id", "is_active", "created"],
)
enrollments = Table(
    "enrollment_enrollment",
    ["id", "child_id", "program_id", "start_date", "end_date", "status"],
)
schedules = Table(
    "enrollment_childschedule",
    ["id", "child_id", "program_id", "enrollment_id", "days_of_week",
     "is_active", "start_time", "end_time"],
)
attendance = Table(
    "attendance_attendancerecord",
    ["id", "child_id", "date", "status", "created"],
)
checkinout = Table(
    "attendance_checkinoutevent",
    ["id", "attendance_record_id", "event_type", "timestamp", "performed_by_id",
     "recorded_by_id", "notes"],
)
handoff = Table(
    "handoff_handoffevent",
    ["id", "attendance_record_id", "event_type", "pickup_person_id",
     "checked_by_id", "timestamp"],
)
documents = Table(
    "documents_document",
    ["id", "child_id", "uploaded_by_id", "document_type", "file",
     "date_created"],
)
notifications = Table(
    "communication_notification",
    ["id", "user_id", "type", "message", "is_read", "created_at"],
)
incidents = Table(
    "incidents_incidentreport",
    ["id", "child_id", "reported_by_id", "incident_type", "description",
     "occurred_on", "occured_at", "severity", "is_resolved", "created_at"],
)

ALLERGENS = [
    ("Peanuts", "LT", "Administer EpiPen immediately. Call 911. Notify guardian."),
    ("Tree Nuts", "S", "Avoid all tree nut products. Antihistamine in emergency kit."),
    ("Dairy", "MD", "Substitute with oat milk. Monitor for hives after meals."),
    ("Eggs", "S", "Avoid egg-containing foods. Benadryl in med kit for exposure."),
    ("Bee Stings", "LT", "EpiPen in classroom bag. Keep indoors on high-pollen days."),
    ("Strawberries", "M", "Mild rash may develop. Apply calamine lotion."),
    ("Shellfish", "S", "Strict avoidance. Notify kitchen of cross-contamination risk."),
    ("Gluten", "MD", "Celiac diet. Dedicated prep surface required."),
    ("Soy", "M", "Read labels; substitute with sunflower butter."),
    ("Latex", "MD", "Use non-latex gloves and supplies around this child."),
]
MED_NOTES = [
    "Child has asthma. Rescue inhaler stored in main office. Use as needed during physical activity.",
    "Child wears corrective lenses. Glasses should remain on during all activities except nap time.",
    "Child is on daily medication administered by guardian before drop-off. No on-site dosing.",
    "Recurring ear infections. Monitor for tugging at ears or complaints of pain.",
    "Mild eczema. Apply prescribed cream to affected areas after water play.",
    "Type 1 diabetes. Blood glucose checks before lunch per care plan on file.",
    "History of febrile seizures. Notify guardian and call 911 if temperature spikes.",
    "Seasonal allergies. May receive antihistamine per signed authorization.",
]
INCIDENT_DESCS = [
    ("S", "M", "Child tripped on playground equipment and scraped a knee. Area cleaned and bandaged. Ice pack applied. Guardian notified at pickup."),
    ("M", "MD", "Child exhibited an allergic reaction (hives) after outdoor play. Antihistamine administered per care plan. Guardian called immediately. Symptoms resolved within 30 minutes."),
    ("M", "M", "Child reported feeling dizzy during circle time. Moved to rest area, given water. Temperature normal. Monitored with no further symptoms."),
    ("S", "M", "Minor collision with another child during free play. No injury. Both children consoled and redirected."),
    ("E", "M", "Child became frustrated during a group activity and left the circle. De-escalated with a quiet-corner break. Guardian informed."),
    ("S", "MD", "Child fell from the bottom rung of the climber. Bumped forehead; small bruise. Ice applied, monitored for 1 hour. Guardian notified by phone."),
]


def pick_program(child_age: int) -> int:
    """Assign a program by rough age-appropriateness (deterministic-ish)."""
    if child_age <= 2:
        return rng.choice([5])           # Precare (site 2)
    if child_age <= 4:
        return rng.choice([1, 4])        # Preschool (site 1/2)
    if child_age <= 5:
        return rng.choice([1, 2, 4])     # Preschool / Headstart
    return rng.choice([3, 2])            # Afterschool / Headstart


DOW_FULL = '{"sunday":false,"monday":true,"tuesday":true,"wednesday":true,"thursday":true,"friday":true,"saturday":false}'
DOW_MWF = '{"sunday":false,"monday":true,"tuesday":false,"wednesday":true,"thursday":false,"friday":true,"saturday":false}'
DOW_TTH = '{"sunday":false,"monday":false,"tuesday":true,"wednesday":false,"thursday":true,"friday":false,"saturday":false}'


# ---------------------------------------------------------------------------
# Build per-child records
# ---------------------------------------------------------------------------

# Group some children into shared-guardian families (consecutive same last name
# already cluster a few; we also randomly pair a handful as siblings).
child_primary_guardian: dict[int, int] = {}   # child_id -> guardian_profile_id
child_primary_pickup: dict[int, int] = {}      # child_id -> pickup_profile_id
child_site: dict[int, int] = {}                # child_id -> site_id

for cid, first, last, dob, status in CHILDREN:
    age = age_on(dob, TODAY)
    program_id = pick_program(age)
    site_id = PROGRAMS[program_id][0]
    child_site[cid] = site_id

    # ---- Guardian (parent) -------------------------------------------------
    g_user = next_user()
    g_first = rng.choice(ADULT_FIRST)
    g_uname = f"guardian_{g_first.lower()}_{last.lower()}_{g_user}"
    users.add(
        g_user,
        "argon2$argon2id$v=19$m=102400,t=2,p=8$c2VlZHNhbHQ$cGxhY2Vob2xkZXI",
        None, False, False, True, g_uname, g_first, last,
        f"{g_first.lower()}.{last.lower()}{g_user}@example.com", CURRENT_TS,
    )
    GUARDIAN_PROFILE_ID += 1
    gp_id = GUARDIAN_PROFILE_ID
    area = rng.choice(["410", "443", "703", "240"])
    contact = f"{area}-555-{rng.randint(1000, 9999)}"
    guardian_profiles.add(gp_id, g_user, contact, True, CURRENT_DATE)
    child_primary_guardian[cid] = gp_id

    g_rel = "P" if rng.random() < 0.8 else rng.choice(["G", "GP"])
    CGR_ID += 1
    cgr.add(CGR_ID, cid, gp_id, g_rel, True, True, True, True)
    ROLE_ASSIGN_ID += 1
    role_assign.add(ROLE_ASSIGN_ID, g_user, 5, cid, None, True, CURRENT_DATE)

    # Optional second guardian (two-parent household) ~45%
    if rng.random() < 0.45:
        g2_user = next_user()
        g2_first = rng.choice(ADULT_FIRST)
        g2_uname = f"guardian_{g2_first.lower()}_{last.lower()}_{g2_user}"
        users.add(
            g2_user,
            "argon2$argon2id$v=19$m=102400,t=2,p=8$c2VlZHNhbHQ$cGxhY2Vob2xkZXI",
            None, False, False, True, g2_uname, g2_first, last,
            f"{g2_first.lower()}.{last.lower()}{g2_user}@example.com", CURRENT_TS,
        )
        GUARDIAN_PROFILE_ID += 1
        gp2_id = GUARDIAN_PROFILE_ID
        guardian_profiles.add(
            gp2_id, g2_user, f"{area}-555-{rng.randint(1000, 9999)}", False,
            CURRENT_DATE,
        )
        CGR_ID += 1
        cgr.add(CGR_ID, cid, gp2_id, "P", False, True, True, True)
        ROLE_ASSIGN_ID += 1
        role_assign.add(ROLE_ASSIGN_ID, g2_user, 5, cid, None, True, CURRENT_DATE)

    # ---- Authorized pickup(s) ---------------------------------------------
    # The primary guardian is always an authorized pickup.
    PICKUP_ID += 1
    pin = rng.randint(1000, 9999)
    pickups.add(
        PICKUP_ID, cid, g_user, g_rel, True, True, pin, None,
    )
    child_primary_pickup[cid] = PICKUP_ID
    ROLE_ASSIGN_ID += 1
    role_assign.add(ROLE_ASSIGN_ID, g_user, 6, cid, None, True, CURRENT_DATE)

    # A secondary pickup (grandparent / aunt-uncle) ~55%
    if rng.random() < 0.55:
        p_user = next_user()
        p_first = rng.choice(PICKUP_FIRST)
        p_last = last if rng.random() < 0.6 else rng.choice(
            [c[2] for c in CHILDREN]
        )
        p_uname = f"pickup_{p_first.lower()}_{p_last.lower()}_{p_user}"
        users.add(
            p_user,
            "argon2$argon2id$v=19$m=102400,t=2,p=8$c2VlZHNhbHQ$cGxhY2Vob2xkZXI",
            None, False, False, True, p_uname, p_first, p_last,
            f"{p_first.lower()}.{p_last.lower()}{p_user}@example.com", CURRENT_TS,
        )
        rel = rng.choice(["GP", "AV", "S"])
        PICKUP_ID += 1
        note = {
            "GP": "Grandparent — verified via photo ID.",
            "AV": "Aunt/uncle — added per guardian request.",
            "S": "Adult sibling — backup pickup only.",
        }[rel]
        pickups.add(
            PICKUP_ID, cid, p_user, rel, True, True, rng.randint(1000, 9999),
            note,
        )
        ROLE_ASSIGN_ID += 1
        role_assign.add(ROLE_ASSIGN_ID, p_user, 6, cid, None, True, CURRENT_DATE)

    # ---- Emergency contacts (1-2, non-user) -------------------------------
    for _ in range(rng.randint(1, 2)):
        EMERGENCY_ID += 1
        ec_first = rng.choice(ADULT_FIRST + PICKUP_FIRST)
        ec_rel = rng.choice(["GP", "AV", "S", "P", "G"])
        emergency.add(
            EMERGENCY_ID, cid, ec_first, last,
            f"{rng.choice(['410', '443', '703'])}-555-{rng.randint(1000, 9999)}",
            ec_rel, True, True, None,
        )

    # ---- Allergies (~30%) --------------------------------------------------
    if rng.random() < 0.30:
        for allergen, sev, instr in rng.sample(ALLERGENS, rng.randint(1, 2)):
            ALLERGY_ID += 1
            allergies.add(ALLERGY_ID, cid, allergen, sev, instr, True)

    # ---- Medical notes (~25%) ---------------------------------------------
    if rng.random() < 0.25:
        MEDNOTE_ID += 1
        mednotes.add(MEDNOTE_ID, cid, rng.choice(MED_NOTES), True, CURRENT_TS)

    # ---- Custody restrictions (court orders etc.) for some at-risk statuses
    if status in ("S", "X") and rng.random() < 0.5:
        CUSTODY_ID += 1
        custody.add(
            CUSTODY_ID, cid,
            "Court order on file. Only individuals on the authorized pickup "
            "list may collect this child without director approval.",
            True,
        )
    elif rng.random() < 0.06:
        CUSTODY_ID += 1
        custody.add(
            CUSTODY_ID, cid,
            "Authorized pickup list strictly enforced per guardian request.",
            True,
        )

    # ---- Enrollment (exactly one current; partial-unique allows one 'A') ---
    if status == "X":
        enr_status = "W"
        start = "2023-09-05"
        end = "2025-01-15"
    elif status == "E":
        enr_status = "A"
        start = (TODAY - timedelta(days=rng.randint(20, 45))).isoformat()
        end = None
    elif status == "S":
        enr_status = "A"
        start = (TODAY - timedelta(days=rng.randint(200, 500))).isoformat()
        end = None
    else:  # A
        enr_status = "A"
        start = (TODAY - timedelta(days=rng.randint(120, 700))).isoformat()
        end = None
    ENROLLMENT_ID += 1
    current_enr = ENROLLMENT_ID
    enrollments.add(current_enr, cid, program_id, start, end, enr_status)

    # Some children have a prior (withdrawn) enrollment in another program.
    if rng.random() < 0.18:
        prior_program = rng.choice([p for p in PROGRAMS if p != program_id])
        ENROLLMENT_ID += 1
        prior_start = (date.fromisoformat(start) - timedelta(days=400)).isoformat()
        prior_end = (date.fromisoformat(start) - timedelta(days=30)).isoformat()
        enrollments.add(
            ENROLLMENT_ID, cid, prior_program, prior_start, prior_end, "PS",
        )

    # ---- Weekly schedule tied to the current enrollment -------------------
    SCHEDULE_ID += 1
    dow = rng.choice([DOW_FULL, DOW_FULL, DOW_MWF, DOW_TTH])
    sched_active = status not in ("X",)
    start_t = rng.choice(["07:00", "07:30", "08:00"])
    end_t = rng.choice(["15:00", "16:00", "17:00", "17:30"])
    schedules.add(
        SCHEDULE_ID, cid, program_id, current_enr, dow, sched_active,
        start_t, end_t,
    )

    # ---- Documents (immunization + birth cert, plus occasional extra) -----
    DOC_ID += 1
    documents.add(
        DOC_ID, cid, g_user, "M",
        f"restricted/compliance/child_{cid}_immunization_record.pdf",
        CURRENT_TS,
    )
    DOC_ID += 1
    documents.add(
        DOC_ID, cid, g_user, "G",
        f"restricted/compliance/child_{cid}_birth_certificate.pdf",
        CURRENT_TS,
    )
    if status in ("S", "X") and rng.random() < 0.7:
        DOC_ID += 1
        documents.add(
            DOC_ID, cid, g_user, "L",
            f"restricted/compliance/child_{cid}_custody_agreement.pdf",
            CURRENT_TS,
        )
    if site_id == 2 and rng.random() < 0.4:
        DOC_ID += 1
        documents.add(
            DOC_ID, cid, g_user, "F",
            f"restricted/compliance/child_{cid}_subsidy_approval.pdf",
            CURRENT_TS,
        )

    # ---- Incident report (~12%) -------------------------------------------
    if rng.random() < 0.12:
        itype, sev, desc = rng.choice(INCIDENT_DESCS)
        occ = TODAY - timedelta(days=rng.randint(7, 90))
        staff = rng.choice(SITE_STAFF[site_id])
        INCIDENT_ID += 1
        incidents.add(
            INCIDENT_ID, cid, staff, itype, desc, occ.isoformat(),
            f"{rng.randint(8, 15):02d}:{rng.choice(['00', '15', '30', '45'])}",
            sev, rng.random() < 0.8, CURRENT_TS,
        )


# ---------------------------------------------------------------------------
# Attendance, check-in/out and handoff events
# ---------------------------------------------------------------------------


for cid, first, last, dob, status in CHILDREN:
    site_id = child_site[cid]
    pickup_id = child_primary_pickup[cid]
    staff_pool = SITE_STAFF[site_id]

    if status in ("A", "E", "S"):
        # Current/recent attendance week.
        if status == "E":
            sch_days = weekdays_back(TODAY - timedelta(days=1), 3)
        elif status == "S":
            # Suspended: attendance is historical (pre-suspension).
            sch_days = weekdays_back(TODAY - timedelta(days=21), 4)
        else:
            sch_days = weekdays_back(TODAY - timedelta(days=1), 5)
    else:  # X transferred -> past attendance before withdrawal
        sch_days = weekdays_back(date(2025, 1, 14), 3)

    event_days = sch_days[-2:]  # detailed CI/CO + handoff for the last 2 days

    att_by_day = {}  # day -> attendance_record id, so events can link to it
    for d in sch_days:
        ATT_ID += 1
        # Most days finalized; the most recent active day may still be a draft.
        rec_status = "F"
        if status == "A" and d == sch_days[-1] and d >= TODAY - timedelta(days=2):
            rec_status = "D"
        attendance.add(ATT_ID, cid, d.isoformat(), rec_status, d.isoformat())
        att_by_day[d] = ATT_ID

    for d in event_days:
        att_id = att_by_day[d]  # events belong to that day's attendance record
        recorder_am = rng.choice(staff_pool)
        recorder_pm = rng.choice(staff_pool)
        in_h, in_m = 7, rng.choice([15, 30, 45, 50])
        out_h, out_m = rng.choice([15, 16, 17]), rng.choice([0, 15, 30, 45])

        CIO_ID += 1
        checkinout.add(
            CIO_ID, att_id, "CI-AM", ts(d, in_h, in_m), pickup_id, recorder_am,
            None,
        )
        CIO_ID += 1
        late = out_h >= 17
        checkinout.add(
            CIO_ID, att_id, "CO-PM", ts(d, out_h, out_m), pickup_id, recorder_pm,
            "Late pickup — guardian called ahead." if late else None,
        )

        HANDOFF_ID += 1
        handoff.add(
            HANDOFF_ID, att_id, "DO-AM", pickup_id, recorder_am, ts(d, in_h, in_m),
        )
        HANDOFF_ID += 1
        handoff.add(
            HANDOFF_ID, att_id, "PU-PM", pickup_id, recorder_pm, ts(d, out_h, out_m),
        )


# ---------------------------------------------------------------------------
# Notifications (a couple per guardian + a few staff/system notices)
# ---------------------------------------------------------------------------

NOTIF_MSGS = {
    "R": "{name}'s attendance record has been finalized.",
    "U": "Action needed: please review updated documents for {name}.",
    "C": "Compliance: immunization records for {name} are due for annual update.",
    "HR": "Staffing reminder posted for your site.",
    "T": "Parent portal maintenance is scheduled for this weekend.",
}
for cid, first, last, dob, status in CHILDREN:
    gp_id = child_primary_guardian[cid]
    g_user = guardian_profiles.rows[gp_id - 1][1]  # user_id of that profile
    for _ in range(rng.randint(1, 2)):
        ntype = rng.choice(["R", "U", "C"])
        NOTIF_ID += 1
        msg = NOTIF_MSGS[ntype].format(name=first)
        created = ts(TODAY - timedelta(days=rng.randint(1, 30)), 9, 0)
        notifications.add(
            NOTIF_ID, g_user, ntype, msg, rng.random() < 0.5, created,
        )

# A few staff/system notifications.
for staff_user in (1, 2, 3):
    NOTIF_ID += 1
    notifications.add(
        NOTIF_ID, staff_user, "T", "Nightly database backup completed successfully.",
        True, ts(TODAY - timedelta(days=1), 2, 0),
    )


# ---------------------------------------------------------------------------
# Static sections (facilities, staff, roles, announcements) preserved verbatim
# ---------------------------------------------------------------------------

STATIC_HEADER = """-- Safari Leader - PostgreSQL Seed Data  (generated by scripts/generate_seed.py)
-- Run after Django migrations: python manage.py migrate
--
-- NOTE: EncryptedIntegerField columns (pickup_pin, personal_pin) are TEXT
-- columns holding Fernet-encrypted ciphertext (encrypted_fields). The plain
-- placeholder integers below will NOT decrypt correctly. Re-set PINs via the
-- Django shell after seeding:  profile.pickup_pin = 1234; profile.save()
--
-- Passwords are placeholder Argon2 hashes. Reset via the Django shell for real use.

BEGIN;

-- ============================================================================
-- 1. django-address tables (dependency for facilities_site)
-- ============================================================================

INSERT INTO address_country (id, name, code) VALUES
  (1, 'United States', 'US');

INSERT INTO address_state (id, name, code, country_id) VALUES
  (1, 'Maryland', 'MD', 1),
  (2, 'Virginia', 'VA', 1);

INSERT INTO address_locality (id, name, postal_code, state_id) VALUES
  (1, 'Baltimore', '21201', 1),
  (2, 'Columbia',  '21044', 1),
  (3, 'Arlington', '22201', 2);

INSERT INTO address_address (id, street_number, route, raw, formatted, latitude, longitude, locality_id) VALUES
  (1, '100', 'Sunshine Blvd', '100 Sunshine Blvd, Baltimore, MD 21201', '100 Sunshine Blvd, Baltimore, MD 21201', 39.2904, -76.6122, 1),
  (2, '250', 'Explorer Way',  '250 Explorer Way, Columbia, MD 21044',   '250 Explorer Way, Columbia, MD 21044',   39.2037, -76.8610, 2),
  (3, '400', 'Meadow Ln',     '400 Meadow Ln, Arlington, VA 22201',     '400 Meadow Ln, Arlington, VA 22201',     38.8816, -77.0910, 3);

SELECT setval('address_country_id_seq',  (SELECT MAX(id) FROM address_country));
SELECT setval('address_state_id_seq',    (SELECT MAX(id) FROM address_state));
SELECT setval('address_locality_id_seq', (SELECT MAX(id) FROM address_locality));
SELECT setval('address_address_id_seq',  (SELECT MAX(id) FROM address_address));

-- ============================================================================
-- 2. accounts_role
-- ============================================================================

INSERT INTO accounts_role (id, name, description, created, deleted) VALUES
  (1, 'ADMIN',      'Full system administrator with unrestricted access',          CURRENT_DATE, NULL),
  (2, 'DIRECTOR',   'Site director responsible for day-to-day operations',         CURRENT_DATE, NULL),
  (3, 'INSTRUCTOR', 'Lead classroom instructor',                                   CURRENT_DATE, NULL),
  (4, 'AIDE',       'Teaching assistant supporting the lead instructor',           CURRENT_DATE, NULL),
  (5, 'GUARDIAN',   'Parent or legal guardian of an enrolled child',               CURRENT_DATE, NULL),
  (6, 'PICKUP',     'Person authorized to pick up a child',                        CURRENT_DATE, NULL),
  (7, 'CLERICAL',   'Administrative support handling auditing and clerical tasks', CURRENT_DATE, NULL);
SELECT setval('accounts_role_id_seq', (SELECT MAX(id) FROM accounts_role));

-- ============================================================================
-- 3. facilities_site
-- ============================================================================

INSERT INTO facilities_site (id, name, address1_id, address2_id, is_active) VALUES
  (1, 'Sunshine Academy',        1, NULL, TRUE),
  (2, 'Little Explorers Center', 2, NULL, TRUE),
  (3, 'Meadow View Campus',      3, NULL, FALSE);
SELECT setval('facilities_site_id_seq', (SELECT MAX(id) FROM facilities_site));

-- ============================================================================
-- 4. facilities_room
-- ============================================================================

INSERT INTO facilities_room (id, site_id, name, capacity, age_group, is_active) VALUES
  (1, 1, 'Caterpillar Room', 8,  'INF', TRUE),
  (2, 1, 'Butterfly Room',   12, 'TOD', TRUE),
  (3, 1, 'Ladybug Room',     16, 'SA',  TRUE),
  (4, 1, 'Firefly Room',     20, 'SA',  TRUE),
  (5, 2, 'Duckling Room',    8,  'INF', TRUE),
  (6, 2, 'Penguin Room',     14, 'TOD', TRUE),
  (7, 2, 'Dolphin Room',     18, 'SA',  TRUE);
SELECT setval('facilities_room_id_seq', (SELECT MAX(id) FROM facilities_room));

-- ============================================================================
-- 5. facilities_program
-- ============================================================================

INSERT INTO facilities_program (id, site_id, name, program_type, is_active) VALUES
  (1, 1, 'Sunshine Preschool',             'PS',    TRUE),
  (2, 1, 'Sunshine Headstart',             'HD-ST', TRUE),
  (3, 1, 'Sunshine Afterschool Enrichment','AS',    TRUE),
  (4, 2, 'Explorers Preschool',            'PS',    TRUE),
  (5, 2, 'Explorers Precare',              'PC',    TRUE);
SELECT setval('facilities_program_id_seq', (SELECT MAX(id) FROM facilities_program));

-- ============================================================================
-- 6. accounts_user  (staff 1-6; guardians/pickups appended below)
-- ============================================================================

INSERT INTO accounts_user (id, password, last_login, is_staff, is_superuser, is_active, username, first_name, last_name, email, date_joined) VALUES
  (1, 'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQx$abcdefghijklmnop', NULL, TRUE,  TRUE,  TRUE, 'admin_john',    'John',    'Anderson', 'john.anderson@example.com',     CURRENT_TIMESTAMP),
  (2, 'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQy$qrstuvwxyzabcdef', NULL, TRUE,  TRUE,  TRUE, 'admin_sarah',   'Sarah',   'Mitchell', 'sarah.mitchell@example.com',    CURRENT_TIMESTAMP),
  (3, 'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQz$ghijklmnopqrstuv', NULL, TRUE,  TRUE,  TRUE, 'admin_michael', 'Michael', 'Thompson', 'michael.thompson@example.com',  CURRENT_TIMESTAMP),
  (4, 'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQ0$wxyzabcdefghijkl', NULL, TRUE,  TRUE,  TRUE, 'admin_lisa',    'Lisa',    'Carter',   'lisa.carter@example.com',       CURRENT_TIMESTAMP),
  (5, 'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQ1$mnopqrstuvabcdef', NULL, TRUE,  TRUE,  TRUE, 'admin_david',   'David',   'Robinson', 'david.robinson@example.com',    CURRENT_TIMESTAMP),
  (6, 'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQ2$ijklmnopqrstuvwx', NULL, FALSE, FALSE, TRUE, 'inst_amy',      'Amy',     'Walker',   'amy.walker@example.com',        CURRENT_TIMESTAMP);
"""

STATIC_STAFF = """-- ============================================================================
-- 8. staffing_staffprofile
-- ============================================================================

INSERT INTO staffing_staffprofile (id, user_id, hire_date, termination_date, personal_pin, role_title, is_active) VALUES
  (1, 1, '2020-01-15', NULL,         1342, 'System Administrator', TRUE),
  (2, 2, '2019-06-01', NULL,         1342, 'Site Director',         TRUE),
  (3, 3, '2021-08-20', NULL,         1342, 'Lead Instructor',       TRUE),
  (4, 4, '2022-01-10', NULL,         1342, 'Instructor',            TRUE),
  (5, 5, '2023-03-01', NULL,         1342, 'Teacher''s Aide',       TRUE),
  (6, 6, '2022-09-15', '2025-12-31', 1342, 'Instructor',            FALSE);
SELECT setval('staffing_staffprofile_id_seq', (SELECT MAX(id) FROM staffing_staffprofile));

-- ============================================================================
-- staffing_staffassignment / shift / ratiorequirement
-- ============================================================================

INSERT INTO staffing_staffassignment (id, staff_id, site_id, room_id, program_id, start_date, end_date, is_active) VALUES
  (1, 2, 1, 3, 1, '2019-06-01', NULL,         TRUE),
  (2, 3, 1, 1, 2, '2021-08-20', NULL,         TRUE),
  (3, 4, 1, 2, 1, '2022-01-10', NULL,         TRUE),
  (4, 5, 2, 5, 4, '2023-03-01', NULL,         TRUE),
  (5, 6, 2, 7, 4, '2022-09-15', '2025-12-31', FALSE);
SELECT setval('staffing_staffassignment_id_seq', (SELECT MAX(id) FROM staffing_staffassignment));

INSERT INTO staffing_shift (id, staff_id, site_id, start_time, end_time, is_active) VALUES
  (1, 2, 1, '07:00', '16:00', TRUE),
  (2, 3, 1, '07:30', '15:30', TRUE),
  (3, 4, 1, '08:00', '16:30', TRUE),
  (4, 5, 2, '06:30', '14:30', TRUE),
  (5, 6, 2, '12:00', '18:00', FALSE);
SELECT setval('staffing_shift_id_seq', (SELECT MAX(id) FROM staffing_shift));

INSERT INTO staffing_ratiorequirement (id, program_id, room_id, min_age, max_age, staff_to_child_ratio, is_active) VALUES
  (1, 1, 2, 1, 3,  '1:4',  TRUE),
  (2, 1, 3, 3, 5,  '1:8',  TRUE),
  (3, 2, 1, 0, 1,  '1:3',  TRUE),
  (4, 3, 4, 5, 12, '1:10', TRUE),
  (5, 4, 6, 1, 3,  '1:4',  TRUE),
  (6, 4, 7, 3, 5,  '1:8',  TRUE);
SELECT setval('staffing_ratiorequirement_id_seq', (SELECT MAX(id) FROM staffing_ratiorequirement));

-- Static staff/role assignments (guardian & pickup assignments are generated).
INSERT INTO accounts_roleassignment (id, user_id, role_id, child_id, room_id, is_active, created) VALUES
  (1,  1, 1, NULL, NULL, TRUE,  CURRENT_DATE),
  (2,  2, 2, NULL, NULL, TRUE,  CURRENT_DATE),
  (3,  3, 3, NULL, 1,    TRUE,  CURRENT_DATE),
  (4,  4, 3, NULL, 2,    TRUE,  CURRENT_DATE),
  (5,  5, 4, NULL, 5,    TRUE,  CURRENT_DATE),
  (6,  6, 3, NULL, 7,    FALSE, CURRENT_DATE);
"""

STATIC_ANNOUNCEMENTS = """-- ============================================================================
-- communication_announcement  (facility-wide; created_by -> staff profile)
-- ============================================================================

INSERT INTO communication_announcement (id, title, message, created_by_id, created_at, updated_at) VALUES
  (1, 'Summer Hours Begin June 2', 'Starting Monday June 2, all sites operate on summer hours: 6:30 AM - 6:00 PM. Please update your schedules.', 2, '2026-05-01 09:00:00-04', '2026-05-01 09:00:00-04'),
  (2, 'Staff Development Day - May 23', 'All sites will be CLOSED Friday May 23 for professional development. No childcare services available.', 2, '2026-05-05 08:00:00-04', '2026-05-05 08:00:00-04'),
  (3, 'New Allergy Policy', 'Per updated health-department guidance, all nut products are prohibited in classrooms. Review the food policy in your packet.', 2, '2026-04-15 10:30:00-04', '2026-04-16 14:00:00-04'),
  (4, 'Picture Day', 'Picture day is Wednesday May 28. Send children in their preferred outfit and a change of clothes.', 2, '2026-05-12 08:30:00-04', '2026-05-12 08:30:00-04'),
  (5, 'Field Trip Permission Forms Due', 'Permission forms for the June nature-center trip are due Friday May 30.', 2, '2026-05-13 09:15:00-04', '2026-05-13 09:15:00-04'),
  (6, 'Water Play Days Begin', 'Water play begins the week of June 9. Send labeled swimwear and towels.', 3, '2026-05-19 11:00:00-04', '2026-05-19 11:00:00-04'),
  (7, 'Updated Pickup Procedure', 'All pickup persons must present photo ID and know the pickup PIN.', 2, '2026-05-21 13:30:00-04', '2026-05-21 13:30:00-04'),
  (8, 'Juneteenth Closure', 'All facilities will be closed June 19 in observance of Juneteenth.', 2, '2026-06-02 09:30:00-04', '2026-06-02 09:30:00-04');
SELECT setval('communication_announcement_id_seq', (SELECT MAX(id) FROM communication_announcement));

INSERT INTO communication_announcement_sites (id, announcement_id, site_id) VALUES
  (1, 1, 1), (2, 1, 2), (3, 2, 1), (4, 2, 2), (5, 3, 1), (6, 3, 2),
  (7, 4, 1), (8, 4, 2), (9, 5, 1), (10, 5, 2), (11, 6, 1), (12, 6, 2),
  (13, 7, 1), (14, 7, 2), (15, 8, 1), (16, 8, 2);
SELECT setval('communication_announcement_sites_id_seq', (SELECT MAX(id) FROM communication_announcement_sites));
"""

CHILDREN_TABLE = Table(
    "children_child",
    ["id", "first_name", "last_name", "date_of_birth", "status", "created_at"],
)
for cid, first, last, dob, status in CHILDREN:
    CHILDREN_TABLE.add(cid, first, last, dob, status, CURRENT_DATE)


# ---------------------------------------------------------------------------
# Assemble the file
# ---------------------------------------------------------------------------

def section(title: str, table: Table) -> str:
    bar = "=" * 76
    return f"-- {bar}\n-- {title}\n-- {bar}\n\n{table.render()}\n"


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.normpath(os.path.join(here, "..", "seed.sql"))

    parts = [STATIC_HEADER]
    parts.append("\n-- guardians & authorized-pickup user accounts\n")
    parts.append(users.render())
    parts.append("\n" + section("children_child", CHILDREN_TABLE))
    parts.append(STATIC_STAFF)
    parts.append("\n" + section("children_guardianprofile", guardian_profiles))
    parts.append(section("children_childguardianrelationship", cgr))
    parts.append(section("children_authorizedpickupprofile", pickups))
    parts.append(section("children_emergencycontact", emergency))
    parts.append(section("children_allergy", allergies))
    parts.append(section("children_medicalnote", mednotes))
    parts.append(section("children_custodyrestriction", custody))
    parts.append(section("accounts_roleassignment (guardians & pickups)", role_assign))
    parts.append(section("enrollment_enrollment", enrollments))
    parts.append(section("enrollment_childschedule", schedules))
    parts.append(section("attendance_attendancerecord", attendance))
    parts.append(section("attendance_checkinoutevent", checkinout))
    parts.append(section("handoff_handoffevent", handoff))
    parts.append(section("documents_document", documents))
    parts.append(section("incidents_incidentreport", incidents))
    parts.append(STATIC_ANNOUNCEMENTS)
    parts.append("\n" + section("communication_notification", notifications))
    parts.append("COMMIT;\n")

    with open(out_path, "w") as fh:
        fh.write("\n".join(parts))

    # Console summary
    counts = {
        "users": len(users.rows),
        "children": len(CHILDREN_TABLE.rows),
        "guardian_profiles": len(guardian_profiles.rows),
        "guardian_links": len(cgr.rows),
        "pickups": len(pickups.rows),
        "emergency_contacts": len(emergency.rows),
        "allergies": len(allergies.rows),
        "medical_notes": len(mednotes.rows),
        "custody_restrictions": len(custody.rows),
        "role_assignments(gen)": len(role_assign.rows),
        "enrollments": len(enrollments.rows),
        "schedules": len(schedules.rows),
        "attendance": len(attendance.rows),
        "checkinout": len(checkinout.rows),
        "handoff": len(handoff.rows),
        "documents": len(documents.rows),
        "incidents": len(incidents.rows),
        "notifications": len(notifications.rows),
    }
    print(f"Wrote {out_path}")
    for k, v in counts.items():
        print(f"  {k:24s} {v}")
    # Sanity: exactly one active enrollment per child.
    active = {}
    for row in enrollments.rows:
        if row[5] == "A":
            active[row[1]] = active.get(row[1], 0) + 1
    dupes = {c: n for c, n in active.items() if n > 1}
    assert not dupes, f"children with >1 active enrollment: {dupes}"
    no_active = [c[0] for c in CHILDREN if c[0] not in active and c[4] != "X"]
    print(f"  active-enrollment children: {len(active)} "
          f"(non-X children without one: {no_active})")


if __name__ == "__main__":
    main()
