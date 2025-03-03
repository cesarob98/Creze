-- FUNCTION: main.compare_passwords(text, text)

-- DROP FUNCTION IF EXISTS main.compare_passwords(text, text);

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

ALTER FUNCTION main.compare_passwords(text, text)
    OWNER TO postgres;
