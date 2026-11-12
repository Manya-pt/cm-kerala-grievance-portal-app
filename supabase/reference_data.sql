-- Reference data: the government departments (fictional sample).
-- Safe to run more than once. No users or grievances are created here.
-- The first CMO account is created with:  python -m app.cli create-cmo

INSERT INTO departments (code, name, description) VALUES
    ('PWD',    'Public Works Department',   'Roads, bridges, public buildings and street infrastructure.'),
    ('KWA',    'Water Authority',           'Drinking water supply, pipelines and water quality.'),
    ('KSEB',   'Electricity Board',         'Power supply, transformers, outages and electrical safety.'),
    ('HEALTH', 'Health & Family Welfare',   'Government hospitals, PHCs, medicines and public health.'),
    ('EDU',    'General Education',         'Government schools, teachers, scholarships and facilities.'),
    ('REV',    'Revenue Department',        'Land records, certificates, village offices and land tax.'),
    ('HOME',   'Home Department (Police)',  'Law and order, police stations and public safety.'),
    ('SJD',    'Social Justice Department', 'Welfare pensions, disability support and social security.'),
    ('LSGD',   'Local Self Government',     'Panchayats, municipalities, sanitation and waste management.'),
    ('TRANS',  'Transport Department',      'Public bus services, routes and transport safety.'),
    ('AGRI',   'Agriculture Department',    'Farmer support, crop loss, subsidies and irrigation.')
ON CONFLICT (code) DO NOTHING;
