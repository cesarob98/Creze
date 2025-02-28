-- FUNCTION: main.login(character varying, character varying)

-- DROP FUNCTION IF EXISTS main.login(character varying, character varying);

CREATE OR REPLACE FUNCTION main.login(
	p_user_name character varying,
	p_password character varying)
    RETURNS TABLE(user_id integer, user_name character varying, mfa_enabled boolean) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE
    v_user_id INTEGER;
    v_user_name CHARACTER VARYING;
	v_cyphered_password VARCHAR;
	v_mfa_enabled BOOLEAN;
BEGIN
    SELECT u.user_id, u.user_name, u.mfa_enabled, u.password INTO v_user_id, v_user_name, v_mfa_enabled, v_cyphered_password
    FROM main.user u
    WHERE u.user_name = p_user_name;

    IF v_user_id IS NOT NULL AND main.compare_passwords(v_cyphered_password, p_password) THEN
        RETURN QUERY(SELECT v_user_id, v_user_name, v_mfa_enabled);
    END IF;
END;
$BODY$;

ALTER FUNCTION main.login(character varying, character varying)
    OWNER TO postgres;
