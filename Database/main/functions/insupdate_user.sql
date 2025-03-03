-- FUNCTION: main.insupdate_user(character varying, character varying)

-- DROP FUNCTION IF EXISTS main.insupdate_user(character varying, character varying);

CREATE OR REPLACE FUNCTION main.insupdate_user(
	p_user_name character varying,
	p_password character varying)
    RETURNS TABLE(user_name character varying, password character varying, mfa_enabled boolean) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE
    v_cyphered_password CHARACTER VARYING;
    _user_name CHARACTER VARYING;
    _password CHARACTER VARYING;
    _mfa_enabled BOOLEAN;
BEGIN
    -- Log the inputs
    RAISE NOTICE 'p_user_name: %, p_password: %', p_user_name, p_password;

    IF p_user_name IS NULL THEN
        RAISE NOTICE 'Error: user_name is NULL';
        RETURN NEXT;
    END IF;

    -- Encrypt the password
    SELECT cypher_password INTO v_cyphered_password FROM main.cypher_password(p_password);
    RAISE NOTICE 'Encrypted password: %', v_cyphered_password;

    -- Insert or update the user
    INSERT INTO main."user" (user_name, password)
    VALUES (p_user_name, v_cyphered_password)
    RETURNING "user".user_id, "user".user_name, "user".mfa_enabled INTO _user_name, _password, _mfa_enabled;

    -- Return the inserted or updated row
    RETURN QUERY (SELECT _user_name, _password, _mfa_enabled);

END;
$BODY$;

ALTER FUNCTION main.insupdate_user(character varying, character varying)
    OWNER TO postgres;
