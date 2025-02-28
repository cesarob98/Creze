-- FUNCTION: main.update_mfa_setup(integer, boolean)

-- DROP FUNCTION IF EXISTS main.update_mfa_setup(integer, boolean);

CREATE OR REPLACE FUNCTION main.update_mfa_setup(
	uid integer,
	p_mfa_setup boolean)
    RETURNS boolean
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
	BEGIN
	    UPDATE main.user 
	    SET mfa_enabled = p_mfa_setup 
	    WHERE user_id = uid;
	
	    RETURN TRUE;  -- Return TRUE on successful update
	END;
	
$BODY$;

ALTER FUNCTION main.update_mfa_setup(integer, boolean)
    OWNER TO postgres;
