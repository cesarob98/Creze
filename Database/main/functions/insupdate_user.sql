-- FUNCTION: main.insupdate_user(character varying, character varying)

-- DROP FUNCTION IF EXISTS main.insupdate_user(character varying, character varying);

CREATE OR REPLACE FUNCTION main.insupdate_user(
	p_user_name character varying,
	p_password character varying)
    RETURNS boolean
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
	v_cyphered_password CHARACTER VARYING;
BEGIN
	BEGIN
		SELECT cypher_password INTO v_cyphered_password FROM main.cypher_password(p_password);
		INSERT INTO main.user (user_name, password) VALUES (p_user_name, v_cyphered_password);
		RETURN TRUE;
	EXCEPTION
		WHEN unique_violation THEN
			RETURN FALSE;
		WHEN OTHERS THEN
			RAISE NOTICE 'Error: %', SQLERRM;
			RETURN FALSE;
	END;
END;
$BODY$;

ALTER FUNCTION main.insupdate_user(character varying, character varying)
    OWNER TO postgres;
