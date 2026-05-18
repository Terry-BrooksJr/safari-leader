-- Safari Leader - PostgreSQL Seed Data
-- Run after Django migrations: python manage.py migrate
--
-- NOTE: EncryptedIntegerField columns (pickup_pin, personal_pin) are stored as
-- Fernet-encrypted text by django-fernet-fields. The placeholder values below
-- will NOT decrypt correctly. Re-set PINs via the Django shell after seeding:
--   profile.pickup_pin = 1234; profile.save()

BEGIN;

-- ============================================================================
-- 1. django-address tables (dependency for facilities_site)
-- ============================================================================

INSERT INTO address_country (id, name, code) VALUES
  (1, 'United States', 'US');

INSERT INTO address_state (id, name, code, country_id) VALUES
  (1, 'Maryland',      'MD', 1),
  (2, 'Virginia',      'VA', 1);

INSERT INTO address_locality (id, name, postal_code, state_id) VALUES
  (1, 'Baltimore',   '21201', 1),
  (2, 'Columbia',    '21044', 1),
  (3, 'Arlington',   '22201', 2);

INSERT INTO address_address (id, street_number, route, raw, formatted, latitude, longitude, locality_id) VALUES
  (1, '100',  'Sunshine Blvd',    '100 Sunshine Blvd, Baltimore, MD 21201',  '100 Sunshine Blvd, Baltimore, MD 21201',  39.2904, -76.6122, 1),
  (2, '250',  'Explorer Way',     '250 Explorer Way, Columbia, MD 21044',    '250 Explorer Way, Columbia, MD 21044',    39.2037, -76.8610, 2),
  (3, '400',  'Meadow Ln',        '400 Meadow Ln, Arlington, VA 22201',     '400 Meadow Ln, Arlington, VA 22201',      38.8816, -77.0910, 3);

SELECT setval('address_country_id_seq',  (SELECT MAX(id) FROM address_country));
SELECT setval('address_state_id_seq',    (SELECT MAX(id) FROM address_state));
SELECT setval('address_locality_id_seq', (SELECT MAX(id) FROM address_locality));
SELECT setval('address_address_id_seq',  (SELECT MAX(id) FROM address_address));

-- ============================================================================
-- 2. accounts_user  (AbstractBaseUser: id, password, last_login)
-- ============================================================================
-- Passwords are Argon2-hashed "changeme123". Reset via Django shell for real use.
INSERT INTO accounts_user (

    id,

    password,

    last_login,

    is_staff,

    is_superuser,

    is_active,

    username,

    first_name,

    last_name,

    email,

    date_joined

) VALUES

(

    1,

    'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQx$abcdefghijklmnop',

    NULL,

    TRUE,

    TRUE,

    TRUE,

    'admin_john',

    'John',

    'Anderson',

    'john.anderson@example.com',

    CURRENT_TIMESTAMP

),

(

    2,

    'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQy$qrstuvwxyzabcdef',

    NULL,

    TRUE,

    TRUE,

    TRUE,

    'admin_sarah',

    'Sarah',

    'Mitchell',

    'sarah.mitchell@example.com',

    CURRENT_TIMESTAMP

),

(

    3,

    'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQz$ghijklmnopqrstuv',

    NULL,

    TRUE,

    TRUE,

    TRUE,

    'admin_michael',

    'Michael',

    'Thompson',

    'michael.thompson@example.com',

    CURRENT_TIMESTAMP

),

(

    4,

    'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQ0$wxyzabcdefghijkl',

    NULL,

    TRUE,

    TRUE,

    TRUE,

    'admin_lisa',

    'Lisa',

    'Carter',

    'lisa.carter@example.com',

    CURRENT_TIMESTAMP

),

(

    5,

    'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQ1$mnopqrstuvabcdef',

    NULL,

    TRUE,

    TRUE,

    TRUE,

    'admin_david',

    'David',

    'Robinson',

    'david.robinson@example.com',

    CURRENT_TIMESTAMP

),

(

    6,

    'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQ2$ijklmnopqrstuvwx',

    NULL,

    TRUE,

    TRUE,

    TRUE,

    'admin_amy',

    'Amy',

    'Walker',

    'amy.walker@example.com',

    CURRENT_TIMESTAMP

),

(

    7,

    'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQ3$abcdefghijklqrst',

    NULL,

    FALSE,

    FALSE,

    TRUE,

    'user_chris',

    'Chris',

    'Evans',

    'chris.evans@example.com',

    CURRENT_TIMESTAMP

),

(

    8,

    'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQ4$uvwxyzabcdefghij',

    NULL,

    FALSE,

    FALSE,

    TRUE,

    'user_karen',

    'Karen',

    'Lewis',

    'karen.lewis@example.com',

    CURRENT_TIMESTAMP

),

(

    9,

    'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQ5$lmnopqrstuvwxyza',

    NULL,

    FALSE,

    FALSE,

    TRUE,

    'user_james',

    'James',

    'Hall',

    'james.hall@example.com',

    CURRENT_TIMESTAMP

),

(

    10,

    'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQxMA$bcdefghijklmnopq',

    NULL,

    FALSE,

    FALSE,

    TRUE,

    'user_emily',

    'Emily',

    'Young',

    'emily.young@example.com',

    CURRENT_TIMESTAMP

),

(

    11,

    'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQxMQ$rstuvwxyzabcdefg',

    NULL,

    FALSE,

    FALSE,

    TRUE,

    'user_robert',

    'Robert',

    'King',

    'robert.king@example.com',

    CURRENT_TIMESTAMP

),

(

    12,

    'argon2$argon2id$v=19$m=102400,t=2,p=8$c29tZXNhbHQxMg$hijklmnopqrstuvw',

    NULL,

    FALSE,

    FALSE,

    TRUE,

    'user_maria',

    'Maria',

    'Scott',

    'maria.scott@example.com',

    CURRENT_TIMESTAMP

);
SELECT setval('accounts_user_id_seq', (SELECT MAX(id) FROM accounts_user));

-- ============================================================================
-- 3. accounts_role
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
-- 4. facilities_site
-- ============================================================================

INSERT INTO facilities_site (id, name, address1_id, address2_id, is_active) VALUES
  (1, 'Sunshine Academy',        1, NULL, TRUE),
  (2, 'Little Explorers Center', 2, NULL, TRUE),
  (3, 'Meadow View Campus',     3, NULL, FALSE);

SELECT setval('facilities_site_id_seq', (SELECT MAX(id) FROM facilities_site));

-- ============================================================================
-- 5. facilities_room
-- ============================================================================

INSERT INTO facilities_room (id, site_id, name, capacity, age_group, is_active) VALUES
  -- Sunshine Academy
  (1, 1, 'Caterpillar Room',  8,  'INF', TRUE),
  (2, 1, 'Butterfly Room',    12, 'TOD', TRUE),
  (3, 1, 'Ladybug Room',      16, 'SA',  TRUE),
  (4, 1, 'Firefly Room',      20, 'SA',  TRUE),
  -- Little Explorers Center
  (5, 2, 'Duckling Room',     8,  'INF', TRUE),
  (6, 2, 'Penguin Room',      14, 'TOD', TRUE),
  (7, 2, 'Dolphin Room',      18, 'SA',  TRUE);

SELECT setval('facilities_room_id_seq', (SELECT MAX(id) FROM facilities_room));

-- ============================================================================
-- 6. facilities_program
-- ============================================================================

INSERT INTO facilities_program (id, site_id, name, program_type, is_active) VALUES
  (1, 1, 'Sunshine Preschool',            'PS',    TRUE),
  (2, 1, 'Sunshine Headstart',            'HD-ST', TRUE),
  (3, 1, 'Sunshine Afterschool Enrichment','AS',   TRUE),
  (4, 2, 'Explorers Preschool',           'PS',    TRUE),
  (5, 2, 'Explorers Precare',             'PC',    TRUE);

SELECT setval('facilities_program_id_seq', (SELECT MAX(id) FROM facilities_program));

-- ============================================================================
-- 7. children_child
-- ============================================================================

INSERT INTO children_child (id, first_name, last_name, date_of_birth, status, created_at) VALUES
  (1,  'Amara',    'Johnson',  '2022-03-15', 'A', CURRENT_DATE),
  (2,  'Elijah',   'Williams', '2021-08-22', 'A', CURRENT_DATE),
  (3,  'Sofia',    'Martinez', '2023-01-10', 'E', CURRENT_DATE),
  (4,  'Noah',     'Brown',    '2020-11-05', 'A', CURRENT_DATE),
  (5,  'Zara',     'Davis',    '2022-06-30', 'A', CURRENT_DATE),
  (6,  'Liam',     'Taylor',   '2019-04-18', 'A', CURRENT_DATE),
  (7,  'Nia',      'Anderson', '2023-09-02', 'E', CURRENT_DATE),
  (8,  'Marcus',   'Thomas',   '2021-12-25', 'S', CURRENT_DATE),
  (9,  'Chloe',    'Jackson',  '2020-07-14', 'X', CURRENT_DATE),
  (10, 'Jayden',   'Harris',   '2022-10-08', 'A', CURRENT_DATE),
  (11, 'Avery',    'Moore',    '2021-02-17', 'A', CURRENT_DATE),
  (12, 'Mason',    'Clark',    '2020-05-29', 'A', CURRENT_DATE),
  (13, 'Isabella', 'Rodriguez','2023-04-12', 'E', CURRENT_DATE),
  (14, 'Ethan',    'Lee',      '2019-09-21', 'S', CURRENT_DATE),
  (15, 'Maya',     'Green',    '2022-12-03', 'A', CURRENT_DATE),
  (16, 'Owen',     'Bennett',  '2021-07-19', 'A', CURRENT_DATE),
  (17, 'Layla',    'Brooks',   '2020-01-31', 'A', CURRENT_DATE),
  (18, 'Caleb',    'Morgan',   '2023-06-08', 'E', CURRENT_DATE),
  (19, 'Harper',   'Allen',    '2021-11-14', 'A', CURRENT_DATE),
  (20, 'Logan',    'Parker',   '2020-03-03', 'A', CURRENT_DATE),
  (21, 'Ella',     'Cook',     '2022-08-22', 'A', CURRENT_DATE),
  (22, 'Jackson',  'Rivera',   '2019-06-16', 'S', CURRENT_DATE),
  (23, 'Scarlett', 'Ward',     '2023-02-01', 'E', CURRENT_DATE),
  (24, 'Levi',     'Torres',   '2021-04-18', 'A', CURRENT_DATE),
  (25, 'Aria',     'Peterson', '2022-01-27', 'A', CURRENT_DATE),
  (26, 'Henry',    'Gray',     '2020-10-09', 'A', CURRENT_DATE),
  (27, 'Grace',    'Ramirez',  '2021-06-11', 'A', CURRENT_DATE),
  (28, 'Sebastian','Price',    '2019-12-05', 'S', CURRENT_DATE),
  (29, 'Luna',     'James',    '2023-07-30', 'E', CURRENT_DATE),
  (30, 'Daniel',   'Watson',   '2020-09-13', 'A', CURRENT_DATE),
(31, 'Aaliyah',   'Coleman',   '2021-01-14', 'A', CURRENT_DATE),
  (32, 'Bryson',    'Mitchell',  '2020-08-09', 'A', CURRENT_DATE),
  (33, 'Camila',    'Flores',    '2022-03-11', 'A', CURRENT_DATE),
  (34, 'Damien',    'Reed',      '2019-12-01', 'S', CURRENT_DATE),
  (35, 'Emerson',   'Bailey',    '2023-05-19', 'E', CURRENT_DATE),
  (36, 'Finley',    'Cooper',    '2021-06-22', 'A', CURRENT_DATE),
  (37, 'Gianna',    'Howard',    '2020-04-17', 'A', CURRENT_DATE),
  (38, 'Hudson',    'Ward',      '2022-11-30', 'A', CURRENT_DATE),
  (39, 'Ivy',       'Peterson',  '2021-02-08', 'A', CURRENT_DATE),
  (40, 'Jasper',    'Powell',    '2019-10-14', 'S', CURRENT_DATE),

  (41, 'Kennedy',   'Brooks',    '2023-01-05', 'E', CURRENT_DATE),
  (42, 'Lincoln',   'Bell',      '2020-09-28', 'A', CURRENT_DATE),
  (43, 'Madeline',  'Price',     '2021-07-12', 'A', CURRENT_DATE),
  (44, 'Nathan',    'Barnes',    '2022-02-20', 'A', CURRENT_DATE),
  (45, 'Olive',     'Murphy',    '2020-05-26', 'A', CURRENT_DATE),
  (46, 'Paisley',   'Hughes',    '2021-12-15', 'A', CURRENT_DATE),
  (47, 'Quentin',   'Simmons',   '2019-03-03', 'S', CURRENT_DATE),
  (48, 'Riley',     'Foster',    '2022-08-18', 'A', CURRENT_DATE),
  (49, 'Sawyer',    'Gonzalez',  '2023-06-09', 'E', CURRENT_DATE),
  (50, 'Talia',     'Bryant',    '2021-10-31', 'A', CURRENT_DATE),

  (51, 'Uriel',     'Diaz',      '2020-01-25', 'A', CURRENT_DATE),
  (52, 'Valentina', 'Russell',   '2022-04-13', 'A', CURRENT_DATE),
  (53, 'Weston',    'Griffin',   '2021-09-07', 'A', CURRENT_DATE),
  (54, 'Xavier',    'Hayes',     '2019-11-21', 'S', CURRENT_DATE),
  (55, 'Yasmin',    'Washington','2023-03-29', 'E', CURRENT_DATE),
  (56, 'Zayne',     'Butler',    '2020-07-04', 'A', CURRENT_DATE),
  (57, 'Alina',     'Perry',     '2022-12-24', 'A', CURRENT_DATE),
  (58, 'Bennett',   'Long',      '2021-05-10', 'A', CURRENT_DATE),
  (59, 'Celeste',   'Patterson', '2020-06-16', 'A', CURRENT_DATE),
  (60, 'Declan',    'Henderson', '2019-08-27', 'S', CURRENT_DATE),

  (61, 'Evelyn',    'Cole',      '2023-02-02', 'E', CURRENT_DATE),
  (62, 'Felix',     'Jenkins',   '2021-11-19', 'A', CURRENT_DATE),
  (63, 'Genevieve', 'Parker',    '2020-10-05', 'A', CURRENT_DATE),
  (64, 'Holden',    'Perry',     '2022-01-08', 'A', CURRENT_DATE),
  (65, 'Isla',      'Stewart',   '2021-03-23', 'A', CURRENT_DATE),
  (66, 'Jonah',     'Ross',      '2019-04-30', 'S', CURRENT_DATE),
  (67, 'Kaia',      'Morris',    '2023-07-17', 'E', CURRENT_DATE),
  (68, 'Lennox',    'Nguyen',    '2020-02-12', 'A', CURRENT_DATE),
  (69, 'Mila',      'Cook',      '2022-09-01', 'A', CURRENT_DATE),
  (70, 'Nolan',     'Kelly',     '2021-08-03', 'A', CURRENT_DATE);
SELECT setval('children_child_id_seq', (SELECT MAX(id) FROM children_child));

-- ============================================================================
-- 8. staffing_staffprofile
-- ============================================================================
-- personal_pin values are placeholders; re-set via Django ORM for encryption.

INSERT INTO staffing_staffprofile (id, user_id, hire_date, termination_date, personal_pin, role_title, is_active) VALUES
  (1, 1, '2020-01-15', NULL,         '1342', 'System Administrator',  TRUE),
  (2, 2, '2019-06-01', NULL,         '1342', 'Site Director',          TRUE),
  (3, 3, '2021-08-20', NULL,         '1342', 'Lead Instructor',        TRUE),
  (4, 4, '2022-01-10', NULL,         '1342', 'Instructor',             TRUE),
  (5, 5, '2023-03-01', NULL,         '1342', 'Teacher''s Aide',        TRUE),
  (6, 6, '2022-09-15', '2025-12-31', '1342', 'Instructor',             FALSE);

SELECT setval('staffing_staffprofile_id_seq', (SELECT MAX(id) FROM staffing_staffprofile));

-- ============================================================================
-- 9. children_guardianprofile
-- ============================================================================

INSERT INTO children_guardianprofile (id, user_id, contact_number, is_primary_contact, created_at) VALUES
  (1, 7,  '410-555-0101', TRUE,  CURRENT_DATE),
  (2, 8,  '410-555-0202', TRUE,  CURRENT_DATE),
  (3, 9,  '703-555-0303', TRUE,  CURRENT_DATE),
  (4, 10, '410-555-0404', FALSE, CURRENT_DATE),
  (5, 11, '410-555-0505', TRUE,  CURRENT_DATE),
  (6, 12, '703-555-0606', FALSE, CURRENT_DATE);

SELECT setval('children_guardianprofile_id_seq', (SELECT MAX(id) FROM children_guardianprofile));

-- ============================================================================
-- 10. children_childguardianrelationship
-- ============================================================================

INSERT INTO children_childguardianrelationship (id, child_id, guardian_id, relationship, is_primary, has_custody_rights, can_pickup, is_active) VALUES
  (1,  1,  1, 'P',  TRUE,  TRUE,  TRUE,  TRUE),
  (2,  2,  2, 'P',  TRUE,  TRUE,  TRUE,  TRUE),
  (3,  3,  3, 'P',  TRUE,  TRUE,  TRUE,  TRUE),
  (4,  4,  1, 'P',  FALSE, TRUE,  TRUE,  TRUE),   -- sibling of child 1, same guardian
  (5,  5,  4, 'GP', FALSE, FALSE, TRUE,  TRUE),
  (6,  6,  5, 'P',  TRUE,  TRUE,  TRUE,  TRUE),
  (7,  7,  2, 'P',  TRUE,  TRUE,  TRUE,  TRUE),   -- sibling of child 2, same guardian
  (8,  8,  3, 'G',  TRUE,  TRUE,  TRUE,  TRUE),
  (9,  10, 6, 'AV', FALSE, FALSE, TRUE,  TRUE),
  (10, 10, 5, 'P',  TRUE,  TRUE,  TRUE,  TRUE);

SELECT setval('children_childguardianrelationship_id_seq', (SELECT MAX(id) FROM children_childguardianrelationship));

-- ============================================================================
-- 11. children_authorizedpickupprofile
-- ============================================================================
-- pickup_pin values are placeholders; re-set via Django ORM for encryption.

INSERT INTO children_authorizedpickupprofile (id, child_id, user_id, relationship, is_authorized, is_active, pickup_pin, verification_notes) VALUES
  (1, 1,  7,  'P',  TRUE, TRUE, '1234', NULL),
  (2, 2,  8,  'P',  TRUE, TRUE, '5321', NULL),
  (3, 3,  9,  'P',  TRUE, TRUE, '5321', NULL),
  (4, 4,  7,  'P',  TRUE, TRUE, '5321', NULL),
  (5, 5,  10, 'GP', TRUE, TRUE, '5321', 'Grandmother — verified via photo ID 2025-01-10'),
  (6, 6,  11, 'P',  TRUE, TRUE, '5321', NULL),
  (7, 10, 12, 'AV', TRUE, TRUE, '5321', 'Uncle — added per guardian request 2025-03-20');

SELECT setval('children_authorizedpickupprofile_id_seq', (SELECT MAX(id) FROM children_authorizedpickupprofile));

-- ============================================================================
-- 12. children_allergy
-- ============================================================================

INSERT INTO children_allergy (id, child_id, allergen, severity, instructions, is_active) VALUES
  (1, 1, 'Peanuts',      'LT', 'Administer EpiPen immediately. Call 911. Notify guardian.',                       TRUE),
  (2, 1, 'Tree Nuts',    'S',  'Avoid all tree nut products. Antihistamine in emergency kit.',                     TRUE),
  (3, 2, 'Dairy',        'MD', 'Substitute with oat milk. Monitor for hives after meals.',                         TRUE),
  (4, 5, 'Bee Stings',   'LT', 'EpiPen in classroom bag. Keep indoors during high-pollen days.',                   TRUE),
  (5, 6, 'Strawberries', 'M',  'Mild rash may develop. Apply calamine lotion. No emergency action needed.',        TRUE),
  (6, 8, 'Eggs',         'S',  'Avoid egg-containing foods. Benadryl in med kit for accidental exposure.',         FALSE);

SELECT setval('children_allergy_id_seq', (SELECT MAX(id) FROM children_allergy));

-- ============================================================================
-- 13. children_medicalnote
-- ============================================================================

INSERT INTO children_medicalnote (id, child_id, note, is_active, date_created) VALUES
  (1, 1, 'Child has asthma. Rescue inhaler stored in main office. Use as needed during physical activity.', TRUE, CURRENT_TIMESTAMP),
  (2, 2, 'Child wears corrective lenses. Glasses should remain on during all activities except nap time.',  TRUE, CURRENT_TIMESTAMP),
  (3, 6, 'Child is on daily medication administered by guardian before drop-off. No on-site dosing.',       TRUE, CURRENT_TIMESTAMP),
  (4, 8, 'Recurring ear infections. Monitor for tugging at ears or complaints of pain.',                    FALSE, CURRENT_TIMESTAMP);

SELECT setval('children_medicalnote_id_seq', (SELECT MAX(id) FROM children_medicalnote));

-- ============================================================================
-- 14. children_custodyrestriction
-- ============================================================================

INSERT INTO children_custodyrestriction (id, child_id, notes, is_active) VALUES
  (1, 8,  'Court order on file dated 2024-11-15. Biological father (John Thomas) is NOT permitted to pick up or visit.', TRUE),
  (2, 4,  'Only individuals on the authorized pickup list may collect this child. No exceptions without director approval.', TRUE),
  (3, 9, 'Temporary suspension of pickup rights for user ID 12 pending investigation. Effective 2025-04-01.', FALSE);

SELECT setval('children_custodyrestriction_id_seq', (SELECT MAX(id) FROM children_custodyrestriction));

-- ============================================================================
-- 15. children_emergencycontact
-- ============================================================================

INSERT INTO children_emergencycontact (id, child_id, first_name, last_name, contact_number, relationship, is_authorized, is_active, verification_notes) VALUES
  (1,  1,  'Denise',  'Johnson',   '410-555-1111', 'GP', TRUE,  TRUE, NULL),
  (2,  1,  'Robert',  'Johnson',   '410-555-1112', 'GP', TRUE,  TRUE, NULL),
  (3,  2,  'Angela',  'Williams',  '410-555-2222', 'AV', TRUE,  TRUE, 'Aunt — lives 5 min from facility'),
  (4,  3,  'Carlos',  'Martinez',  '703-555-3333', 'P',  TRUE,  TRUE, NULL),
  (5,  4,  'Denise',  'Johnson',   '410-555-1111', 'GP', TRUE,  TRUE, NULL),
  (6,  5,  'Frank',   'Davis',     '410-555-5555', 'P',  TRUE,  TRUE, NULL),
  (7,  6,  'Grace',   'Taylor',    '410-555-6666', 'S',  FALSE, TRUE, 'Older sibling — 17 years old, backup only'),
  (8,  8,  'Helen',   'Thomas',    '410-555-8888', 'GP', TRUE,  TRUE, 'Paternal grandmother'),
  (9,  10, 'James',   'Harris',    '410-555-1010', 'P',  TRUE,  TRUE, NULL);

SELECT setval('children_emergencycontact_id_seq', (SELECT MAX(id) FROM children_emergencycontact));

-- ============================================================================
-- 16. staffing_staffassignment
-- ============================================================================

INSERT INTO staffing_staffassignment (id, staff_id, site_id, room_id, program_id, start_date, end_date, is_active) VALUES
  (1, 2, 1, 3, 1, '2019-06-01', NULL,         TRUE),   -- Director -> Ladybug Room / Preschool
  (2, 3, 1, 1, 2, '2021-08-20', NULL,         TRUE),   -- Lead Instructor -> Caterpillar / Headstart
  (3, 4, 1, 2, 1, '2022-01-10', NULL,         TRUE),   -- Instructor -> Butterfly / Preschool
  (4, 5, 2, 5, 4, '2023-03-01', NULL,         TRUE),   -- Aide -> Duckling / Explorers Preschool
  (5, 6, 2, 7, 4, '2022-09-15', '2025-12-31', FALSE);  -- Former Instructor -> Dolphin

SELECT setval('staffing_staffassignment_id_seq', (SELECT MAX(id) FROM staffing_staffassignment));

-- ============================================================================
-- 17. staffing_shift
-- ============================================================================

INSERT INTO staffing_shift (id, staff_id, site_id, start_time, end_time, is_active) VALUES
  (1, 2, 1, '07:00', '16:00', TRUE),
  (2, 3, 1, '07:30', '15:30', TRUE),
  (3, 4, 1, '08:00', '16:30', TRUE),
  (4, 5, 2, '06:30', '14:30', TRUE),
  (5, 6, 2, '12:00', '18:00', FALSE);

SELECT setval('staffing_shift_id_seq', (SELECT MAX(id) FROM staffing_shift));

-- ============================================================================
-- 18. staffing_ratiorequirement
-- ============================================================================

INSERT INTO staffing_ratiorequirement (id, program_id, room_id, min_age, max_age, staff_to_child_ratio, is_active) VALUES
  (1, 1, 2, 1, 3,  '1:4',  TRUE),   -- Preschool toddlers
  (2, 1, 3, 3, 5,  '1:8',  TRUE),   -- Preschool school-age
  (3, 2, 1, 0, 1,  '1:3',  TRUE),   -- Headstart infants
  (4, 3, 4, 5, 12, '1:10', TRUE),   -- Afterschool
  (5, 4, 6, 1, 3,  '1:4',  TRUE),   -- Explorers toddlers
  (6, 4, 7, 3, 5,  '1:8',  TRUE);   -- Explorers school-age

SELECT setval('staffing_ratiorequirement_id_seq', (SELECT MAX(id) FROM staffing_ratiorequirement));

-- ============================================================================
-- 19. accounts_roleassignment
-- ============================================================================

INSERT INTO accounts_roleassignment (id, user_id, role_id, child_id, room_id, is_active, created) VALUES
  (1,  1,  1, NULL, NULL, TRUE,  CURRENT_DATE),  -- user 1 = Admin
  (2,  2,  2, NULL, NULL, TRUE,  CURRENT_DATE),  -- user 2 = Director
  (3,  3,  3, NULL, 1,   TRUE,  CURRENT_DATE),  -- user 3 = Instructor, Caterpillar Room
  (4,  4,  3, NULL, 2,   TRUE,  CURRENT_DATE),  -- user 4 = Instructor, Butterfly Room
  (5,  5,  4, NULL, 5,   TRUE,  CURRENT_DATE),  -- user 5 = Aide, Duckling Room
  (6,  6,  3, NULL, 7,   FALSE, CURRENT_DATE),  -- user 6 = Instructor (terminated)
  (7,  7,  5, 1,   NULL, TRUE,  CURRENT_DATE),  -- user 7 = Guardian of child 1
  (8,  7,  5, 4,   NULL, TRUE,  CURRENT_DATE),  -- user 7 = Guardian of child 4
  (9,  8,  5, 2,   NULL, TRUE,  CURRENT_DATE),  -- user 8 = Guardian of child 2
  (10, 9,  5, 3,   NULL, TRUE,  CURRENT_DATE),  -- user 9 = Guardian of child 3
  (11, 10, 6, 5,   NULL, TRUE,  CURRENT_DATE),  -- user 10 = Authorized Pickup for child 5
  (12, 11, 5, 6,   NULL, TRUE,  CURRENT_DATE),  -- user 11 = Guardian of child 6
  (13, 12, 6, 10,  NULL, TRUE,  CURRENT_DATE);  -- user 12 = Authorized Pickup for child 10

SELECT setval('accounts_roleassignment_id_seq', (SELECT MAX(id) FROM accounts_roleassignment));

-- ============================================================================
-- 20. enrollment_enrollment
-- ============================================================================

INSERT INTO enrollment_enrollment (id, child_id, program_id, site_id, start_date, end_date, status) VALUES
  (1,  1,  1, 1, '2025-01-06', NULL,         'A'),
  (2,  2,  2, 1, '2024-09-03', NULL,         'A'),
  (3,  3,  1, 1, '2025-08-01', NULL,         'P'),
  (4,  4,  3, 1, '2024-09-03', NULL,         'A'),
  (5,  5,  4, 2, '2025-01-06', NULL,         'A'),
  (6,  6,  4, 2, '2023-09-05', NULL,         'A'),
  (7,  7,  4, 2, '2025-09-01', NULL,         'P'),
  (8,  8,  1, 1, '2024-06-01', '2025-02-28', 'W'),
  (9,  9,  4, 2, '2023-09-05', '2025-01-15', 'PS'),
  (10, 10, 1, 1, '2025-02-01', NULL,         'A');

SELECT setval('enrollment_enrollment_id_seq', (SELECT MAX(id) FROM enrollment_enrollment));

-- ============================================================================
-- 21. enrollment_childschedule
-- ============================================================================

INSERT INTO enrollment_childschedule (id, child_id, program_id, enrollment_id, days_of_week, is_active, start_time, end_time) VALUES
  (1, 1,  1, 1,  '{"sunday":false,"monday":true,"tuesday":true,"wednesday":true,"thursday":true,"friday":true,"saturday":false}',  TRUE,  '07:30', '17:00'),
  (2, 2,  2, 2,  '{"sunday":false,"monday":true,"tuesday":true,"wednesday":true,"thursday":true,"friday":true,"saturday":false}',  TRUE,  '08:00', '15:00'),
  (3, 4,  3, 4,  '{"sunday":false,"monday":true,"tuesday":false,"wednesday":true,"thursday":false,"friday":true,"saturday":false}', TRUE,  '15:00', '18:00'),
  (4, 5,  4, 5,  '{"sunday":false,"monday":true,"tuesday":true,"wednesday":true,"thursday":true,"friday":true,"saturday":false}',  TRUE,  '07:00', '17:30'),
  (5, 6,  4, 6,  '{"sunday":false,"monday":true,"tuesday":true,"wednesday":true,"thursday":true,"friday":false,"saturday":false}', TRUE,  '08:00', '16:00'),
  (6, 10, 1, 10, '{"sunday":false,"monday":true,"tuesday":true,"wednesday":true,"thursday":true,"friday":true,"saturday":false}',  TRUE,  '07:30', '17:00');

SELECT setval('enrollment_childschedule_id_seq', (SELECT MAX(id) FROM enrollment_childschedule));

-- ============================================================================
-- 22. attendance_attendancerecord
-- ============================================================================

INSERT INTO attendance_attendancerecord (id, child_id, date, status, created) VALUES
  (1,  1,  '2025-05-09', 'F', '2025-05-09'),
  (2,  2,  '2025-05-09', 'F', '2025-05-09'),
  (3,  4,  '2025-05-09', 'F', '2025-05-09'),
  (4,  5,  '2025-05-09', 'F', '2025-05-09'),
  (5,  6,  '2025-05-09', 'F', '2025-05-09'),
  (6,  10, '2025-05-09', 'F', '2025-05-09'),
  (7,  1,  '2025-05-10', 'D', '2025-05-10'),
  (8,  2,  '2025-05-10', 'D', '2025-05-10'),
  (9,  5,  '2025-05-10', 'D', '2025-05-10'),
  (10, 10, '2025-05-10', 'D', '2025-05-10');

SELECT setval('attendance_attendancerecord_id_seq', (SELECT MAX(id) FROM attendance_attendancerecord));

-- ============================================================================
-- 23. attendance_checkinoutevent
-- ============================================================================

INSERT INTO attendance_checkinoutevent (id, child_id, event_type, timestamp, performed_by_id, recorded_by_id, notes) VALUES
  (1,  1,  'CI-AM', '2025-05-09 07:45:00-04', 1, 3, NULL),
  (2,  2,  'CI-AM', '2025-05-09 08:10:00-04', 2, 3, NULL),
  (3,  1,  'CO-PM', '2025-05-09 17:05:00-04', 1, 4, NULL),
  (4,  2,  'CO-PM', '2025-05-09 15:00:00-04', 2, 3, NULL),
  (5,  5,  'CI-AM', '2025-05-09 07:15:00-04', 5, 5, NULL),
  (6,  5,  'CO-PM', '2025-05-09 17:30:00-04', 5, 5, 'Late pickup — guardian called ahead'),
  (7,  10, 'CI-AM', '2025-05-09 07:50:00-04', 7, 4, NULL),
  (8,  10, 'CO-PM', '2025-05-09 16:45:00-04', 7, 4, NULL);

SELECT setval('attendance_checkinoutevent_id_seq', (SELECT MAX(id) FROM attendance_checkinoutevent));

-- ============================================================================
-- 24. handoff_handoffevent
-- ============================================================================

INSERT INTO handoff_handoffevent (id, child_id, event_type, pickup_person_id, checked_by_id, timestamp) VALUES
  (1, 1,  'DO-AM', 1, 3, '2025-05-09 07:45:00-04'),
  (2, 2,  'DO-AM', 2, 3, '2025-05-09 08:10:00-04'),
  (3, 1,  'PU-PM', 1, 4, '2025-05-09 17:05:00-04'),
  (4, 2,  'PU-PM', 2, 3, '2025-05-09 15:00:00-04'),
  (5, 5,  'DO-AM', 5, 5, '2025-05-09 07:15:00-04'),
  (6, 5,  'PU-PM', 5, 5, '2025-05-09 17:30:00-04'),
  (7, 10, 'DO-AM', 7, 4, '2025-05-09 07:50:00-04'),
  (8, 10, 'PU-PM', 7, 4, '2025-05-09 16:45:00-04');

SELECT setval('handoff_handoffevent_id_seq', (SELECT MAX(id) FROM handoff_handoffevent));

-- ============================================================================
-- 25. documents_document
-- ============================================================================

INSERT INTO documents_document (id, child_id, uploaded_by_id, document_type, file, date_created) VALUES
  (1, 1, 7,  'M', 'restricted/compliance/child_1_immunization_record.pdf', '2025-01-05 10:00:00-05'),
  (2, 1, 7,  'G', 'restricted/compliance/child_1_birth_certificate.pdf',   '2025-01-05 10:05:00-05'),
  (3, 2, 8,  'M', 'restricted/compliance/child_2_immunization_record.pdf', '2024-09-01 14:30:00-04'),
  (4, 3, 9,  'L', 'restricted/compliance/child_3_custody_agreement.pdf',   '2025-07-20 09:00:00-04'),
  (5, 5, 10, 'F', 'restricted/compliance/child_5_subsidy_approval.pdf',    '2025-01-04 11:15:00-05'),
  (6, 8, 9,  'L', 'restricted/compliance/child_8_court_order.pdf',         '2024-11-15 08:30:00-05');

SELECT setval('documents_document_id_seq', (SELECT MAX(id) FROM documents_document));

-- ============================================================================
-- 26. communication_announcement
-- ============================================================================

INSERT INTO communication_announcement (id, title, message, created_by_id, created_at, updated_at) VALUES
  (1, 'Summer Hours Begin June 2',
      'Starting Monday June 2, all sites will operate on summer hours: 6:30 AM – 6:00 PM. Please update your schedules accordingly.',
      2, '2025-05-01 09:00:00-04', '2025-05-01 09:00:00-04'),
  (2, 'Staff Development Day — May 23',
      'All sites will be CLOSED on Friday May 23 for staff professional development. No childcare services will be available.',
      2, '2025-05-05 08:00:00-04', '2025-05-05 08:00:00-04'),
  (3, 'New Allergy Policy Effective Immediately',
      'Per updated health department guidelines, all nut products are now prohibited in all classrooms. Please review the updated food policy in your welcome packet.',
      2, '2025-04-15 10:30:00-04', '2025-04-16 14:00:00-04'),
  (4, 'Picture Day Schedule',
      'Picture day will take place on Wednesday May 28. Please send children in their preferred photo outfit and include a change of clothes if needed.',
      2, '2025-05-12 08:30:00-04', '2025-05-12 08:30:00-04'),
  (5, 'Field Trip Permission Forms Due',
      'Permission forms for the June nature center field trip are due by Friday May 30.',
      2, '2025-05-13 09:15:00-04', '2025-05-13 09:15:00-04'),
  (6, 'Water Play Days Begin',
      'Water play activities begin the week of June 9. Please send labeled swimwear and towels.',
      3, '2025-05-19 11:00:00-04', '2025-05-19 11:00:00-04'),
  (7, 'Family Breakfast Morning',
      'Families are invited to join us for breakfast on Friday June 6 from 8:00 AM to 9:00 AM.',
      2, '2025-05-20 07:45:00-04', '2025-05-20 07:45:00-04'),
  (8, 'Updated Pickup Procedure Reminder',
      'All pickup persons must present photo identification and know the pickup PIN.',
      2, '2025-05-21 13:30:00-04', '2025-05-21 13:30:00-04'),
  (9, 'Summer Camp Registration Open',
      'Registration for summer camp programs is now available through the parent portal.',
      2, '2025-05-22 10:00:00-04', '2025-05-22 10:00:00-04'),
  (10, 'New Playground Safety Rules',
      'Updated playground supervision and safety rules are now in effect at all sites.',
      3, '2025-05-23 09:00:00-04', '2025-05-23 09:00:00-04'),
  (11, 'Parent Teacher Conferences',
      'Conference signups are available online beginning Monday.',
      2, '2025-05-24 08:15:00-04', '2025-05-24 08:15:00-04'),
  (12, 'Library Story Week',
      'Children are encouraged to bring their favorite books during story week activities.',
      3, '2025-05-25 12:00:00-04', '2025-05-25 12:00:00-04'),
  (13, 'Emergency Contact Audit',
      'Please review and confirm all emergency contact information by the end of the month.',
      2, '2025-05-26 11:20:00-04', '2025-05-26 11:20:00-04'),
  (14, 'Outdoor Activity Advisory',
      'Due to warmer temperatures, outdoor play schedules may shift earlier in the day.',
      2, '2025-05-27 07:00:00-04', '2025-05-27 07:00:00-04'),
  (15, 'Nutrition Program Update',
      'The summer meal program menu has been updated and is available online.',
      3, '2025-05-28 09:45:00-04', '2025-05-28 09:45:00-04'),
  (16, 'Technology Maintenance Notice',
      'Parent portal access may be intermittent during scheduled maintenance this Saturday.',
      1, '2025-05-29 18:00:00-04', '2025-05-29 18:00:00-04'),
  (17, 'Volunteer Opportunities Available',
      'Families interested in volunteering for summer events may contact the front office.',
      2, '2025-05-30 10:10:00-04', '2025-05-30 10:10:00-04'),
  (18, 'Classroom Supply Donations',
      'We are accepting classroom supply donations for art and sensory activities.',
      3, '2025-05-31 14:15:00-04', '2025-05-31 14:15:00-04'),
  (19, 'Parking Lot Safety Reminder',
      'Please use designated crosswalks and hold children''s hands in the parking lot.',
      2, '2025-06-01 08:00:00-04', '2025-06-01 08:00:00-04'),
  (20, 'Juneteenth Closure Notice',
      'All facilities will be closed on June 19 in observance of Juneteenth.',
      2, '2025-06-02 09:30:00-04', '2025-06-02 09:30:00-04'),
  (21, 'Staff Appreciation Week',
      'Families are welcome to leave thank-you notes for teachers during appreciation week.',
      2, '2025-06-03 08:45:00-04', '2025-06-03 08:45:00-04'),
  (22, 'Medication Policy Reminder',
      'All medications must be in original packaging with current authorization forms.',
      3, '2025-06-04 13:00:00-04', '2025-06-04 13:00:00-04'),
  (23, 'Lost and Found Cleanout',
      'Unclaimed lost and found items will be donated at the end of the month.',
      2, '2025-06-05 15:20:00-04', '2025-06-05 15:20:00-04');

SELECT setval('communication_announcement_id_seq', (SELECT MAX(id) FROM communication_announcement));

-- M2M: announcement <-> sites
INSERT INTO communication_announcement_sites (id, announcement_id, site_id) VALUES
  (1, 1, 1),
  (2, 1, 2),
  (3, 2, 1),
  (4, 2, 2),
  (5, 3, 1),
  (6, 3, 2),
  (7, 4, 1),
  (8, 4, 2),
  (9, 5, 1),
  (10, 5, 2),
  (11, 6, 1),
  (12, 6, 2),
  (13, 7, 1),
  (14, 7, 2),
  (15, 8, 1),
  (16, 8, 2),
  (17, 9, 1),
  (18, 9, 2),
  (19, 10, 1),
  (20, 10, 2),
  (21, 11, 1),
  (22, 11, 2),
  (23, 12, 1),
  (24, 12, 2),
  (25, 13, 1),
  (26, 13, 2),
  (27, 14, 1),
  (28, 14, 2),
  (29, 15, 1),
  (30, 15, 2),
  (31, 16, 1),
  (32, 16, 2),
  (33, 17, 1),
  (34, 17, 2),
  (35, 18, 1),
  (36, 18, 2),
  (37, 19, 1),
  (38, 19, 2),
  (39, 20, 1),
  (40, 20, 2),
  (41, 21, 1),
  (42, 21, 2),
  (43, 22, 1),
  (44, 22, 2),
  (45, 23, 1),
  (46, 23, 2);

SELECT setval('communication_announcement_sites_id_seq', (SELECT MAX(id) FROM communication_announcement_sites));

-- ============================================================================
-- 27. communication_notification
-- ============================================================================

INSERT INTO communication_notification (id, user_id, type, message, is_read, created_at) VALUES
  (1,  7,  'R',  'Amara''s attendance record for May 9 has been finalized.',           TRUE,  '2025-05-09 18:00:00-04'),
  (2,  7,  'U',  'Reminder: immunization records for Amara are due for annual update.', FALSE, '2025-05-08 09:00:00-04'),
  (3,  8,  'R',  'Elijah''s attendance record for May 9 has been finalized.',           TRUE,  '2025-05-09 18:00:00-04'),
  (4,  11, 'C',  'Subsidy renewal documentation is required by June 1.',               FALSE, '2025-05-01 10:00:00-04'),
  (5,  2,  'HR', 'Staff assignment for user 6 has been deactivated.',                   TRUE,  '2025-12-31 17:00:00-05'),
  (6,  1,  'T',  'Database backup completed successfully at 2025-05-10 02:00 UTC.',    TRUE,  '2025-05-10 02:00:00+00'),
  (7, 7, 'U', 'Picture day is scheduled for May 28.', FALSE, '2025-05-12 09:00:00-04'),
  (8, 8, 'R', 'Elijah has a completed daily report available for review.', FALSE, '2025-05-12 16:45:00-04'),
  (9, 9, 'C', 'Custody documentation for Sofia requires director review.', FALSE, '2025-05-13 10:30:00-04'),
  (10, 10, 'U', 'Please confirm Zara''s authorized pickup list.', FALSE, '2025-05-14 08:15:00-04'),
  (11, 11, 'R', 'Liam''s attendance record has been finalized.', TRUE, '2025-05-12 18:00:00-04'),
  (12, 12, 'U', 'Jayden has an upcoming document update due.', FALSE, '2025-05-15 09:20:00-04'),
  (13, 2, 'HR', 'Staffing ratio review is due for Sunshine Academy by Friday.', FALSE, '2025-05-15 11:10:00-04'),
  (14, 3, 'T', 'New attendance exception report is ready for review.', FALSE, '2025-05-16 07:55:00-04'),
  (15, 4, 'R', 'Incident report follow-up reminder pending.', FALSE, '2025-05-16 12:30:00-04'),
  (16, 5, 'U', 'Water play schedule has been posted.', FALSE, '2025-05-19 12:00:00-04'),
  (17, 7, 'C', 'Emergency contact information was successfully updated.', TRUE, '2025-05-20 09:00:00-04'),
  (18, 8, 'U', 'Summer camp registration is now open.', FALSE, '2025-05-20 14:00:00-04'),
  (19, 9, 'R', 'Sofia''s enrollment packet has been received.', TRUE, '2025-05-21 10:25:00-04'),
  (20, 10, 'U', 'Please upload updated immunization forms.', FALSE, '2025-05-22 08:40:00-04'),
  (21, 11, 'C', 'Pickup authorization has been approved.', TRUE, '2025-05-22 15:45:00-04'),
  (22, 12, 'R', 'Attendance records are available in the portal.', TRUE, '2025-05-23 18:00:00-04'),
  (23, 1, 'T', 'Nightly audit completed successfully.', TRUE, '2025-05-24 01:00:00+00'),
  (24, 2, 'HR', 'Background check renewal due next month.', FALSE, '2025-05-24 11:15:00-04'),
  (25, 3, 'T', 'New classroom assignment report generated.', FALSE, '2025-05-25 07:20:00-04'),
  (26, 4, 'R', 'Daily attendance submission confirmed.', TRUE, '2025-05-25 17:00:00-04');

SELECT setval('communication_notification_id_seq', (SELECT MAX(id) FROM communication_notification));

-- ============================================================================
-- 28. incidents_incidentreport
-- ============================================================================

INSERT INTO incidents_incidentreport (id, child_id, reported_by_id, incident_type, description, occurred_on, occured_at, severity, is_resolved, created_at) VALUES
  (1, 2, 3, 'S',
     'Child tripped on playground equipment and scraped left knee. Area cleaned and bandaged. Ice pack applied. Guardian notified at pickup.',
     '2025-04-28', '10:30', 'M', TRUE, '2025-04-28 10:45:00-04'),
  (2, 5, 5, 'M',
     'Child exhibited allergic reaction (hives on arms) after outdoor play. Antihistamine administered per care plan. Guardian called immediately. Symptoms resolved within 30 minutes.',
     '2025-05-02', '14:15', 'MD', TRUE, '2025-05-02 14:20:00-04'),
  (3, 6, 4, 'E',
     'Child reported feeling dizzy during circle time. Moved to rest area, given water. Temperature normal. Monitored for remainder of day with no further symptoms.',
     '2025-05-09', '09:45', 'M', TRUE, '2025-05-09 09:50:00-04');

SELECT setval('incidents_incidentreport_id_seq', (SELECT MAX(id) FROM incidents_incidentreport));

COMMIT;
