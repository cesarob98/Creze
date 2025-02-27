-- FUNCTION: main.cypher_password(text)

-- DROP FUNCTION IF EXISTS main.cypher_password(text);

CREATE OR REPLACE FUNCTION main.cypher_password(
	p_password text)
    RETURNS text
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
  v_cyphered_password text;
BEGIN
  v_cyphered_password := crypt(p_password, gen_salt('bf'));
  RETURN v_cyphered_password;
END;
$BODY$;

ALTER FUNCTION main.cypher_password(text)
    OWNER TO postgres;
