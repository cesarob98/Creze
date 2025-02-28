-- Table: main.user

-- DROP TABLE IF EXISTS main."user";

CREATE TABLE IF NOT EXISTS main."user"
(
    user_id integer NOT NULL DEFAULT nextval('main.user_user_id_seq'::regclass),
    user_name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    password character varying(255) COLLATE pg_catalog."default" NOT NULL,
    mfa_enabled boolean DEFAULT true,
    CONSTRAINT user_pkey PRIMARY KEY (user_id),
    CONSTRAINT user_user_name_key UNIQUE (user_name)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS main."user"
    OWNER to postgres;