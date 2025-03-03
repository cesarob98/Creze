-- FUNCTION: main.cypher_password(text)

-- DROP FUNCTION IF EXISTS main.cypher_password(text);

CREATE OR REPLACE FUNCTION main.cypher_password(
	p_password text)
    RETURNS text
    LANGUAGE 'sql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
SELECT public.crypt(p_password, public.gen_salt('bf'));
$BODY$;

ALTER FUNCTION main.cypher_password(text)
    OWNER TO postgres;
