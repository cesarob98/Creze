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
BEGIN
    BEGIN
        -- Encrypt the password
        SELECT cypher_password INTO v_cyphered_password FROM main.cypher_password(p_password);
        
        -- Try to insert the user, update if exists
        INSERT INTO main.user (user_name, password)
        VALUES (p_user_name, v_cyphered_password)
        ON CONFLICT(user_name) 
        DO UPDATE 
        SET password = EXCLUDED.password
        RETURNING user_name, password, mfa_enabled INTO user_name, password, mfa_enabled;

        -- Return the inserted or updated row
        RETURN NEXT;
        
    EXCEPTION
        WHEN unique_violation THEN
            -- If a unique violation occurs, return the existing row
            RETURN QUERY
                SELECT user_name, password, mfa_enabled
                FROM main.user
                WHERE user_name = p_user_name;
        WHEN OTHERS THEN
            -- Handle other errors and raise a notice
            RAISE NOTICE 'Error: %', SQLERRM;
            RETURN NEXT;
    END;
END;
$BODY$;

ALTER FUNCTION main.insupdate_user(character varying, character varying)
    OWNER TO postgres;
