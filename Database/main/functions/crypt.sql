-- FUNCTION: main.crypt(text, text)

-- DROP FUNCTION IF EXISTS main.crypt(text, text);

CREATE OR REPLACE FUNCTION main.crypt(
	text,
	text)
    RETURNS text
    LANGUAGE 'c'
    COST 1
    IMMUTABLE STRICT PARALLEL SAFE 
AS '$libdir/pgcrypto', 'pg_crypt'
;

ALTER FUNCTION main.crypt(text, text)
    OWNER TO postgres;
