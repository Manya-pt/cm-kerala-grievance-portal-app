-- FICTIONAL SAMPLE GRIEVANCES for demonstration (recruitment prototype). Not real citizen data.
-- Run in Supabase -> SQL Editor AFTER reference_data.sql and demo_accounts.sql.
-- Creates 22 grievances in every status, each with history, plus assignments,
-- action-taken reports, feedback, one escalation, one duplicate pair and 2 contact enquiries.
-- Safe to run twice: it does nothing if the sample data is already there.

DO $$
DECLARE
    r          RECORD;
    cmo_id     INTEGER;
    cit_ids    INTEGER[];
    cit_id     INTEGER;
    dept_id    INTEGER;
    dept_name  TEXT;
    off_id     INTEGER;
    gid        INTEGER;
    rid        INTEGER;
    start_ts   TIMESTAMP;
    last_ts    TIMESTAMP;
    first_ref  TEXT;
    cur_ref    TEXT;
    cur_status TEXT;
    sla_days   INTEGER;
BEGIN
    IF EXISTS (SELECT 1 FROM grievances WHERE subject = 'Large potholes on Aluva-Perumbavoor road') THEN
        RAISE NOTICE 'Sample grievances already exist. Nothing to do.';
        RETURN;
    END IF;

    SELECT id INTO cmo_id FROM users WHERE email = 'cmo@demo.com';
    SELECT array_agg(id ORDER BY email) INTO cit_ids
      FROM users WHERE email IN ('citizen@demo.com', 'citizen2@demo.com');
    IF cmo_id IS NULL OR cit_ids IS NULL OR array_length(cit_ids, 1) < 2 THEN
        RAISE EXCEPTION 'Run demo_accounts.sql first (cmo@demo.com and the two demo citizens are needed).';
    END IF;

    -- stage: 0 submitted, 1 forwarded (Under Review), 2 In Progress, 3 report awaiting review,
    --        4 resolved, 5 reopened
    FOR r IN
        SELECT * FROM (VALUES
            (1,  'Ernakulam',          'Roads & Infrastructure', 'PWD',    'High',   'Large potholes on Aluva-Perumbavoor road',
                 'Several deep potholes near Thottumugham junction have caused two-wheeler accidents this week. Rain water fills them at night and they are not visible.', 2, 5),
            (2,  'Thiruvananthapuram', 'Water Supply',           'KWA',    'High',   'No drinking water supply for 6 days in Kazhakuttam ward',
                 'Our ward has not received pipe water for six days. Around 200 families depend on this supply and are buying water at high cost.', 4, 9),
            (3,  'Kozhikode',          'Electricity',            'KSEB',   'High',   'Low-hanging live wire near school',
                 'An electric line is hanging very low near the gate of the government LP school in Feroke. Children pass under it every day.', 4, 8),
            (4,  'Thrissur',           'Healthcare',             'HEALTH', 'Medium', 'Medicine shortage at taluk hospital pharmacy',
                 'Diabetes and blood pressure medicines have been unavailable at the Chalakudy taluk hospital pharmacy for three weeks.', 3, 7),
            (5,  'Kollam',             'Sanitation & Waste',     'LSGD',   'Medium', 'Garbage not collected for two weeks',
                 'Household waste has not been collected in Kadappakada area for two weeks. Stray dogs scatter it and there is a bad smell.', 1, 4),
            (6,  'Palakkad',           'Agriculture',            'AGRI',   'Medium', 'Crop loss compensation not received',
                 'My paddy crop was damaged in the August floods. I applied for compensation at the Krishi Bhavan but have not received any amount.', 2, 6),
            (7,  'Malappuram',         'Social Welfare',         'SJD',    'Medium', 'Widow pension stopped without notice',
                 'My mother has not received her widow pension for the last four months. No reason was given by the panchayat office.', 4, 10),
            (8,  'Kannur',             'Public Transport',       'TRANS',  'Low',    'Request for additional bus on Thalassery-Iritty route',
                 'Morning buses on the Thalassery to Iritty route are extremely crowded. Students and workers request one more service at 8 AM.', 0, 1),
            (9,  'Kottayam',           'Revenue & Land',         'REV',    'Medium', 'Delay in issuing possession certificate',
                 'I applied for a possession certificate at Ettumanoor village office two months ago. The application is still pending.', 5, 12),
            (10, 'Alappuzha',          'Roads & Infrastructure', 'PWD',    'Medium', 'Street lights not working on beach road',
                 'Most street lights on Alappuzha beach road have not worked for a month, making it unsafe for walkers at night.', 4, 11),
            (11, 'Idukki',             'Healthcare',             'HEALTH', 'High',   'No doctor at primary health centre at night',
                 'The PHC at Adimali has no doctor after 6 PM. Patients from tribal settlements have to travel 40 km during emergencies.', 1, 8),
            (12, 'Wayanad',            'Education',              'EDU',    'Medium', 'Damaged roof in government school classroom',
                 'The roof of two classrooms at the government UP school in Meppadi leaks badly during rain. Classes are being disrupted.', 2, 6),
            (13, 'Kasaragod',          'Water Supply',           'KWA',    'Medium', 'Pipeline leak wasting water on main road',
                 'A major pipeline is leaking near the new bus stand for ten days and water is flowing on the road.', 0, 2),
            (14, 'Pathanamthitta',     'Police & Safety',        'HOME',   'Medium', 'Frequent bike thefts near railway station',
                 'There have been at least five bike thefts at the Thiruvalla railway station parking area this month. We request police patrolling.', 1, 5),
            (15, 'Ernakulam',          'Sanitation & Waste',     'LSGD',   'High',   'Overflowing drainage causing mosquito breeding',
                 'The canal near Kaloor stadium is blocked with plastic waste. Stagnant water is causing mosquito breeding and fever cases.', 3, 6),
            (16, 'Thiruvananthapuram', 'Electricity',            'KSEB',   'Medium', 'Frequent power cuts in evening',
                 'Our area in Nemom faces 3-4 power cuts every evening for the past two weeks without any notice.', 0, 1),
            (17, 'Thrissur',           'Education',              'EDU',    'Low',    'Scholarship amount not credited',
                 'My pre-matric scholarship for last academic year has not been credited although the application was approved.', 4, 13),
            (18, 'Kozhikode',          'Roads & Infrastructure', 'PWD',    'Medium', 'Footpath broken near medical college',
                 'The footpath slabs near Kozhikode medical college main gate are broken. Elderly patients find it difficult to walk.', 0, 0),
            (19, 'Kollam',             'Water Supply',           'KWA',    'Medium', 'Muddy water from public tap',
                 'Water from the public tap in Karunagappally ward 12 is muddy and smells bad for the last week.', 2, 6),
            (20, 'Palakkad',           'Social Welfare',         'SJD',    'Low',    'Disability certificate camp request',
                 'Many differently-abled persons in Ottapalam need certificates. We request a medical board camp in the taluk.', 0, 2),
            (21, 'Malappuram',         'Public Transport',       'TRANS',  'Medium', 'KSRTC bus skipping stop',
                 'The KSRTC fast passenger buses do not stop at Kottakkal changuvetty stop even when passengers wait.', 4, 10),
            (22, 'Ernakulam',          'Roads & Infrastructure', 'PWD',    'High',   'Potholes on Aluva Perumbavoor road causing accidents',
                 'Big potholes near Thottumugham on the Aluva to Perumbavoor road. Many bike riders have fallen. Please repair urgently.', 0, 0)
        ) AS t(n, district, category, code, priority, subject, descr, stage, days_ago)
        ORDER BY n
    LOOP
        cit_id := cit_ids[1 + (r.n % 2)];
        SELECT d.id, d.name INTO dept_id, dept_name FROM departments d WHERE d.code = r.code;
        SELECT u.id INTO off_id FROM users u
          WHERE u.role = 'officer' AND u.department_id = dept_id ORDER BY u.id LIMIT 1;
        IF dept_id IS NULL THEN
            RAISE EXCEPTION 'Department % missing. Run reference_data.sql first.', r.code;
        END IF;

        sla_days := CASE r.priority WHEN 'High' THEN 3 WHEN 'Medium' THEN 7 ELSE 14 END;
        start_ts := (now() AT TIME ZONE 'utc')
                    - make_interval(days => r.days_ago, hours => (r.n * 7) % 20);
        last_ts  := start_ts;
        cur_status := 'Submitted';

        -- 1. Citizen submits
        INSERT INTO grievances (citizen_id, district, category, subject, description, priority,
                                status, due_at, created_at, updated_at,
                                ai_department, ai_category, ai_priority, ai_summary, ai_source)
        VALUES (cit_id, r.district, r.category, r.subject, r.descr, r.priority,
                'Submitted', start_ts + make_interval(days => sla_days), start_ts, start_ts,
                dept_name, r.category, r.priority,
                'Citizen reports: ' || lower(r.subject) || '. Requires review by ' || dept_name || '.',
                'sample data (not AI)')
        RETURNING id INTO gid;

        cur_ref := 'CMK-' || to_char(start_ts, 'YYYY') || '-' || lpad(gid::text, 6, '0');
        UPDATE grievances SET ref_id = cur_ref WHERE id = gid;
        IF r.n = 1 THEN first_ref := cur_ref; END IF;

        INSERT INTO grievance_history (grievance_id, from_status, to_status, action, remark, is_internal, user_id, created_at)
        VALUES (gid, 'Submitted', 'Submitted', 'Grievance submitted',
                'Reference number ' || cur_ref || ' generated.', FALSE, cit_id, start_ts);

        -- 2. CMO forwards to the department
        IF r.stage >= 1 THEN
            last_ts := start_ts + interval '2 hours';
            INSERT INTO assignments (grievance_id, department_id, officer_id, assigned_by_id, note, active, assigned_at)
            VALUES (gid, dept_id, off_id, cmo_id, 'Please inspect and act at the earliest.', TRUE, last_ts);
            INSERT INTO grievance_history (grievance_id, from_status, to_status, action, remark, is_internal, user_id, created_at)
            VALUES (gid, cur_status, 'Under Review', 'Forwarded to ' || dept_name,
                    'Please inspect and act at the earliest.', FALSE, cmo_id, last_ts);
            UPDATE grievances SET department_id = dept_id WHERE id = gid;
            cur_status := 'Under Review';
        END IF;

        -- 3. Officer starts investigation
        IF r.stage >= 2 THEN
            last_ts := start_ts + interval '6 hours';
            INSERT INTO grievance_history (grievance_id, from_status, to_status, action, remark, is_internal, user_id, created_at)
            VALUES (gid, cur_status, 'In Progress', 'Investigation started by department',
                    'Field team has been assigned to inspect the location.', FALSE, off_id, last_ts);
            cur_status := 'In Progress';
        END IF;

        -- 4. Officer submits an action-taken report
        IF r.stage >= 3 THEN
            last_ts := start_ts + interval '20 hours';
            INSERT INTO action_reports (grievance_id, officer_id, report, review_status, created_at)
            VALUES (gid, off_id,
                    'Issue inspected and corrective work completed by ' || dept_name || '. Site photos available on request.',
                    'Pending', last_ts)
            RETURNING id INTO rid;
            INSERT INTO grievance_history (grievance_id, from_status, to_status, action, remark, is_internal, user_id, created_at)
            VALUES (gid, 'In Progress', 'In Progress', 'Action-taken report submitted to CMO',
                    'Issue inspected and corrective work completed.', FALSE, off_id, last_ts);
        END IF;

        -- 5. CMO accepts the report: resolved
        IF r.stage >= 4 THEN
            last_ts := start_ts + interval '30 hours';
            UPDATE action_reports
               SET review_status = 'Accepted', cmo_remark = 'Verified with the department. Closing.', reviewed_at = last_ts
             WHERE id = rid;
            INSERT INTO grievance_history (grievance_id, from_status, to_status, action, remark, is_internal, user_id, created_at)
            VALUES (gid, 'In Progress', 'Resolved', 'Action-taken report accepted. Grievance resolved',
                    'Verified with the department. Closing.', FALSE, cmo_id, last_ts);
            cur_status := 'Resolved';
            UPDATE grievances SET resolved_at = last_ts WHERE id = gid;

            -- some citizens leave feedback
            IF r.stage = 4 AND r.n % 3 <> 0 THEN
                last_ts := last_ts + interval '4 hours';
                INSERT INTO feedback (grievance_id, citizen_id, rating, comment, created_at)
                VALUES (gid, cit_id, 3 + (r.n % 3), 'Thank you for the action.', last_ts);
                INSERT INTO grievance_history (grievance_id, from_status, to_status, action, remark, is_internal, user_id, created_at)
                VALUES (gid, 'Resolved', 'Resolved', 'Citizen feedback submitted',
                        'Rating ' || (3 + (r.n % 3)) || '/5. Thank you for the action.', FALSE, cit_id, last_ts);
            END IF;
        END IF;

        -- 6. Citizen reopens (stage 5 only)
        IF r.stage = 5 THEN
            last_ts := start_ts + interval '3 days';
            INSERT INTO grievance_history (grievance_id, from_status, to_status, action, remark, is_internal, user_id, created_at)
            VALUES (gid, 'Resolved', 'Reopened', 'Reopened by citizen',
                    'The problem has returned after a few days.', FALSE, cit_id, last_ts);
            cur_status := 'Reopened';
            UPDATE grievances
               SET resolved_at = NULL,
                   due_at = (now() AT TIME ZONE 'utc') + make_interval(days => sla_days)
             WHERE id = gid;
        END IF;

        UPDATE grievances SET status = cur_status, updated_at = last_ts WHERE id = gid;
    END LOOP;

    -- One escalated grievance (Idukki, still waiting on the department)
    UPDATE grievances SET escalated = TRUE, priority = 'High' WHERE subject = 'No doctor at primary health centre at night';
    INSERT INTO grievance_history (grievance_id, from_status, to_status, action, remark, is_internal, user_id, created_at)
    SELECT id, status, status, 'Escalated by CMO', 'Delayed grievance escalated for urgent action.', FALSE, cmo_id,
           (now() AT TIME ZONE 'utc')
    FROM grievances WHERE subject = 'No doctor at primary health centre at night';

    -- One duplicate pair: the last sample repeats the first one
    UPDATE grievances
       SET ai_duplicate_ref = first_ref,
           ai_duplicate_reason = 'Same potholes near Thottumugham on the Aluva-Perumbavoor road.'
     WHERE subject = 'Potholes on Aluva Perumbavoor road causing accidents';

    INSERT INTO contact_enquiries (name, email, subject, message) VALUES
        ('Anjali Menon', 'anjali@example.com', 'Can NRIs submit grievances?',
         'I live abroad. Can I submit a grievance for my parents in Kottayam?'),
        ('Rahul Nair', 'rahul@example.com', 'Mobile app', 'Is there a mobile app planned for this portal?');

    RAISE NOTICE 'Sample data created: 22 grievances and 2 contact enquiries.';
END $$;
