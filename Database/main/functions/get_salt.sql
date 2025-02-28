
-- FUNCTION: main.gen_salt(text)

-- DROP FUNCTION IF EXISTS main.gen_salt(text);

CREATE OR REPLACE FUNCTION main.gen_salt(
	text)
    RETURNS text
    LANGUAGE 'c'
    COST 1
    VOLATILE STRICT PARALLEL SAFE 
AS '$libdir/pgcrypto', 'pg_gen_salt'
;

ALTER FUNCTION main.gen_salt(text)
    OWNER TO postgres;
