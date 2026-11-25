CREATE TABLE occupations(
    id VARCHAR(20) PRIMARY KEY,
    esco_id VARCHAR(20),
    onet_id VARCHAR(20),
    title TEXT,
    occ_description TEXT,
    source TEXT,
    source_version VARCHAR(20),
    validation TEXT
);


CREATE SEQUENCE occupations_id_seq OWNED BY occupations.id;

ALTER TABLE occupations ALTER COLUMN id
  SET DEFAULT 'OCC_' || LPAD(nextval('occupations_id_seq')::TEXT, 6, '0');

CREATE TEMP TABLE temporary1 (
    occupation_id VARCHAR(20),
    canonical_title TEXT,
    occupation_description TEXT
);


\copy temporary FROM 'C:/Users/Laura/OneDrive/Desktop/Data_science_2/cleaning_data/occupations.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
INSERT INTO occupations(esco_id, title, occ_description) SELECT occupation_id, canonical_title, occupation_description FROM temporary;

CREATE TEMP TABLE temporary2 (
    iscoGroup VARCHAR(20),
    occupation_code VARCHAR (20),
    preferredLabel TEXT,
    occupation_id_onet VARCHAR (20)
);

\copy temporary2 FROM 'C:/Users/Laura/OneDrive/Desktop/Data_science_2/datasets/esco_onet_crosswalk.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

UPDATE occupations
SET onet_id = occupation_id_onet
FROM temporary2
WHERE esco_id = occupation_code;

UPDATE occupations
SET source = 'ESCO',
    source_version = '1.2.1';

UPDATE occupations
SET validation = 'imported & preprocessed';