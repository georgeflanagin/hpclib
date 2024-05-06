drop view if exists export;
drop table if exists facts;

CREATE TABLE facts (
    user VARCHAR(20), 
    systolic INTEGER,
    diastolic INTEGER,
    pulse INTEGER,
    arm CHAR(1),
    t DATETIME DEFAULT CURRENT_TIMESTAMP,
    narrative VARCHAR(100));

CREATE VIEW export AS 
    SELECT 
        DATETIME(t, 'localtime') AS time, 
        systolic, 
        diastolic, 
        pulse, 
        narrative 
    FROM facts ORDER BY time;

