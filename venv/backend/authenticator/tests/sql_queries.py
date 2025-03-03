SQL_CREATE_SCHEMA = "CREATE SCHEMA IF NOT EXISTS main;"
SQL_PG_CRYPTO = "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
SQL_USER = """
    CREATE TABLE IF NOT EXISTS main."user"
    (
        user_id serial primary key not null,
        user_name character varying(255) COLLATE pg_catalog."default" NOT NULL,
        password character varying(255) COLLATE pg_catalog."default" NOT NULL,
        mfa_enabled boolean DEFAULT false,
        CONSTRAINT user_user_name_key UNIQUE (user_name)
    )

    TABLESPACE pg_default;
"""
SQL_COPMPARE_PW = """
        CREATE OR REPLACE FUNCTION main.compare_passwords(
            p_cyphered_passsword text,
            p_input_password text)
            RETURNS boolean
            LANGUAGE 'sql'
            COST 100
            VOLATILE PARALLEL UNSAFE
        AS $BODY$
        SELECT public.crypt(p_input_password, p_cyphered_passsword) = p_cyphered_passsword;
        $BODY$;
"""
SQL_CYPHER = """
    CREATE OR REPLACE FUNCTION main.cypher_password(
        p_password text)
        RETURNS text
        LANGUAGE 'sql'
        COST 100
        VOLATILE PARALLEL UNSAFE
    AS $BODY$
    SELECT public.crypt(p_password, public.gen_salt('bf'));
    $BODY$;
"""
SQL_INSUPDATE = """
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
"""
SQL_LOGIN = """
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
"""