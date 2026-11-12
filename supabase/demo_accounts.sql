-- TEST ACCOUNTS ONLY, for evaluators of this recruitment prototype.
-- Every account below uses the password  Demo@1234  (stored as a scrypt hash, never in plain text).
-- Run after reference_data.sql. Safe to run more than once.
-- Do NOT run this on a real deployment: create the CMO with  python -m app.cli create-cmo  instead.

INSERT INTO users (name, email, mobile, password_hash, role) VALUES
    ('CMO Administrator', 'cmo@demo.com', '9000000001', 'scrypt:32768:8:1$Kl4QOca5CZIq6jy4$335350c6596fb08c7b75c0a8c39354de72cf2d9a712800cfd2477aef82c8d43c8b568cd11f20b040a00413070df67d6db5f336c5957fa3f2335d5e6b35e80b1f', 'cmo'),
    ('Arun Kumar (Demo Citizen)', 'citizen@demo.com', '9847000001', 'scrypt:32768:8:1$Kl4QOca5CZIq6jy4$335350c6596fb08c7b75c0a8c39354de72cf2d9a712800cfd2477aef82c8d43c8b568cd11f20b040a00413070df67d6db5f336c5957fa3f2335d5e6b35e80b1f', 'citizen'),
    ('Fathima Rahman (Demo Citizen)', 'citizen2@demo.com', '9847000002', 'scrypt:32768:8:1$Kl4QOca5CZIq6jy4$335350c6596fb08c7b75c0a8c39354de72cf2d9a712800cfd2477aef82c8d43c8b568cd11f20b040a00413070df67d6db5f336c5957fa3f2335d5e6b35e80b1f', 'citizen')
ON CONFLICT (email) DO NOTHING;

-- One officer per department
INSERT INTO users (name, email, mobile, password_hash, role, department_id)
SELECT d.name || ' Officer', 'officer.pwd@demo.com', '9000000100', 'scrypt:32768:8:1$Kl4QOca5CZIq6jy4$335350c6596fb08c7b75c0a8c39354de72cf2d9a712800cfd2477aef82c8d43c8b568cd11f20b040a00413070df67d6db5f336c5957fa3f2335d5e6b35e80b1f', 'officer', d.id
FROM departments d WHERE d.code = 'PWD'
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (name, email, mobile, password_hash, role, department_id)
SELECT d.name || ' Officer', 'officer.kwa@demo.com', '9000000101', 'scrypt:32768:8:1$Kl4QOca5CZIq6jy4$335350c6596fb08c7b75c0a8c39354de72cf2d9a712800cfd2477aef82c8d43c8b568cd11f20b040a00413070df67d6db5f336c5957fa3f2335d5e6b35e80b1f', 'officer', d.id
FROM departments d WHERE d.code = 'KWA'
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (name, email, mobile, password_hash, role, department_id)
SELECT d.name || ' Officer', 'officer.kseb@demo.com', '9000000102', 'scrypt:32768:8:1$Kl4QOca5CZIq6jy4$335350c6596fb08c7b75c0a8c39354de72cf2d9a712800cfd2477aef82c8d43c8b568cd11f20b040a00413070df67d6db5f336c5957fa3f2335d5e6b35e80b1f', 'officer', d.id
FROM departments d WHERE d.code = 'KSEB'
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (name, email, mobile, password_hash, role, department_id)
SELECT d.name || ' Officer', 'officer.health@demo.com', '9000000103', 'scrypt:32768:8:1$Kl4QOca5CZIq6jy4$335350c6596fb08c7b75c0a8c39354de72cf2d9a712800cfd2477aef82c8d43c8b568cd11f20b040a00413070df67d6db5f336c5957fa3f2335d5e6b35e80b1f', 'officer', d.id
FROM departments d WHERE d.code = 'HEALTH'
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (name, email, mobile, password_hash, role, department_id)
SELECT d.name || ' Officer', 'officer.edu@demo.com', '9000000104', 'scrypt:32768:8:1$Kl4QOca5CZIq6jy4$335350c6596fb08c7b75c0a8c39354de72cf2d9a712800cfd2477aef82c8d43c8b568cd11f20b040a00413070df67d6db5f336c5957fa3f2335d5e6b35e80b1f', 'officer', d.id
FROM departments d WHERE d.code = 'EDU'
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (name, email, mobile, password_hash, role, department_id)
SELECT d.name || ' Officer', 'officer.rev@demo.com', '9000000105', 'scrypt:32768:8:1$Kl4QOca5CZIq6jy4$335350c6596fb08c7b75c0a8c39354de72cf2d9a712800cfd2477aef82c8d43c8b568cd11f20b040a00413070df67d6db5f336c5957fa3f2335d5e6b35e80b1f', 'officer', d.id
FROM departments d WHERE d.code = 'REV'
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (name, email, mobile, password_hash, role, department_id)
SELECT d.name || ' Officer', 'officer.home@demo.com', '9000000106', 'scrypt:32768:8:1$Kl4QOca5CZIq6jy4$335350c6596fb08c7b75c0a8c39354de72cf2d9a712800cfd2477aef82c8d43c8b568cd11f20b040a00413070df67d6db5f336c5957fa3f2335d5e6b35e80b1f', 'officer', d.id
FROM departments d WHERE d.code = 'HOME'
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (name, email, mobile, password_hash, role, department_id)
SELECT d.name || ' Officer', 'officer.sjd@demo.com', '9000000107', 'scrypt:32768:8:1$Kl4QOca5CZIq6jy4$335350c6596fb08c7b75c0a8c39354de72cf2d9a712800cfd2477aef82c8d43c8b568cd11f20b040a00413070df67d6db5f336c5957fa3f2335d5e6b35e80b1f', 'officer', d.id
FROM departments d WHERE d.code = 'SJD'
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (name, email, mobile, password_hash, role, department_id)
SELECT d.name || ' Officer', 'officer.lsgd@demo.com', '9000000108', 'scrypt:32768:8:1$Kl4QOca5CZIq6jy4$335350c6596fb08c7b75c0a8c39354de72cf2d9a712800cfd2477aef82c8d43c8b568cd11f20b040a00413070df67d6db5f336c5957fa3f2335d5e6b35e80b1f', 'officer', d.id
FROM departments d WHERE d.code = 'LSGD'
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (name, email, mobile, password_hash, role, department_id)
SELECT d.name || ' Officer', 'officer.trans@demo.com', '9000000109', 'scrypt:32768:8:1$Kl4QOca5CZIq6jy4$335350c6596fb08c7b75c0a8c39354de72cf2d9a712800cfd2477aef82c8d43c8b568cd11f20b040a00413070df67d6db5f336c5957fa3f2335d5e6b35e80b1f', 'officer', d.id
FROM departments d WHERE d.code = 'TRANS'
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (name, email, mobile, password_hash, role, department_id)
SELECT d.name || ' Officer', 'officer.agri@demo.com', '9000000110', 'scrypt:32768:8:1$Kl4QOca5CZIq6jy4$335350c6596fb08c7b75c0a8c39354de72cf2d9a712800cfd2477aef82c8d43c8b568cd11f20b040a00413070df67d6db5f336c5957fa3f2335d5e6b35e80b1f', 'officer', d.id
FROM departments d WHERE d.code = 'AGRI'
ON CONFLICT (email) DO NOTHING;

