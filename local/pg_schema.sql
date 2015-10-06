--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: bags_of_words; Type: TABLE; Schema: public; Owner: the_owner; Tablespace: 
--

CREATE TABLE bags_of_words (
    id integer NOT NULL,
    generated_on timestamp with time zone,
    bag_of_words character varying[],
    method character varying,
    response_id integer
);


ALTER TABLE bags_of_words OWNER TO the_owner;

--
-- Name: bags_of_words_id_seq; Type: SEQUENCE; Schema: public; Owner: the_owner
--

CREATE SEQUENCE bags_of_words_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE bags_of_words_id_seq OWNER TO the_owner;

--
-- Name: bags_of_words_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: the_owner
--

ALTER SEQUENCE bags_of_words_id_seq OWNED BY bags_of_words.id;


--
-- Name: identities; Type: TABLE; Schema: public; Owner: the_owner; Tablespace: 
--

CREATE TABLE identities (
    response_id integer,
    identity json,
    id integer NOT NULL
);


ALTER TABLE identities OWNER TO the_owner;

--
-- Name: identities_id_seq; Type: SEQUENCE; Schema: public; Owner: the_owner
--

CREATE SEQUENCE identities_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE identities_id_seq OWNER TO the_owner;

--
-- Name: identities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: the_owner
--

ALTER SEQUENCE identities_id_seq OWNED BY identities.id;


--
-- Name: responses; Type: TABLE; Schema: public; Owner: the_owner; Tablespace: 
--

CREATE TABLE responses (
    id integer NOT NULL,
    source_url character varying,
    cleaned_content character varying,
    raw_content character varying,
    raw_content_md5 character varying(40),
    initial_harvest_date timestamp with time zone,
    source_url_sha character varying(100),
    inlinks character varying[],
    outlinks character varying[],
    host character varying,
    schemas character varying[],
    format character varying(20),
    headers json,
    namespaces json
);


ALTER TABLE responses OWNER TO the_owner;

--
-- Name: responses_id_seq; Type: SEQUENCE; Schema: public; Owner: the_owner
--

CREATE SEQUENCE responses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE responses_id_seq OWNER TO the_owner;

--
-- Name: responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: the_owner
--

ALTER SEQUENCE responses_id_seq OWNED BY responses.id;


--
-- Name: validations; Type: TABLE; Schema: public; Owner: the_owner; Tablespace: 
--

CREATE TABLE validations (
    id integer NOT NULL,
    validated_on timestamp with time zone,
    errors character varying[],
    valid boolean,
    response_id integer
);


ALTER TABLE validations OWNER TO the_owner;

--
-- Name: validations_id_seq; Type: SEQUENCE; Schema: public; Owner: the_owner
--

CREATE SEQUENCE validations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE validations_id_seq OWNER TO the_owner;

--
-- Name: validations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: the_owner
--

ALTER SEQUENCE validations_id_seq OWNED BY validations.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: the_owner
--

ALTER TABLE ONLY bags_of_words ALTER COLUMN id SET DEFAULT nextval('bags_of_words_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: the_owner
--

ALTER TABLE ONLY identities ALTER COLUMN id SET DEFAULT nextval('identities_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: the_owner
--

ALTER TABLE ONLY responses ALTER COLUMN id SET DEFAULT nextval('responses_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: the_owner
--

ALTER TABLE ONLY validations ALTER COLUMN id SET DEFAULT nextval('validations_id_seq'::regclass);


--
-- Name: bags_of_words_pkey; Type: CONSTRAINT; Schema: public; Owner: the_owner; Tablespace: 
--

ALTER TABLE ONLY bags_of_words
    ADD CONSTRAINT bags_of_words_pkey PRIMARY KEY (id);


--
-- Name: identity_pkey; Type: CONSTRAINT; Schema: public; Owner: the_owner; Tablespace: 
--

ALTER TABLE ONLY identities
    ADD CONSTRAINT identity_pkey PRIMARY KEY (id);


--
-- Name: responses_id_pkey; Type: CONSTRAINT; Schema: public; Owner: the_owner; Tablespace: 
--

ALTER TABLE ONLY responses
    ADD CONSTRAINT responses_id_pkey PRIMARY KEY (id);


--
-- Name: unique_url_sha; Type: CONSTRAINT; Schema: public; Owner: the_owner; Tablespace: 
--

ALTER TABLE ONLY responses
    ADD CONSTRAINT unique_url_sha UNIQUE (source_url_sha);


--
-- Name: validations_pkey; Type: CONSTRAINT; Schema: public; Owner: the_owner; Tablespace: 
--

ALTER TABLE ONLY validations
    ADD CONSTRAINT validations_pkey PRIMARY KEY (id);


--
-- Name: response_bags_of_words_fkey; Type: FK CONSTRAINT; Schema: public; Owner: the_owner
--

ALTER TABLE ONLY bags_of_words
    ADD CONSTRAINT response_bags_of_words_fkey FOREIGN KEY (response_id) REFERENCES responses(id);


--
-- Name: response_identity_fkey; Type: FK CONSTRAINT; Schema: public; Owner: the_owner
--

ALTER TABLE ONLY identities
    ADD CONSTRAINT response_identity_fkey FOREIGN KEY (response_id) REFERENCES responses(id);


--
-- Name: response_validation_fkey; Type: FK CONSTRAINT; Schema: public; Owner: the_owner
--

ALTER TABLE ONLY validations
    ADD CONSTRAINT response_validation_fkey FOREIGN KEY (response_id) REFERENCES responses(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: the_owner
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM the_owner;
GRANT ALL ON SCHEMA public TO the_owner;


--
-- Name: bags_of_words; Type: ACL; Schema: public; Owner: the_owner
--

REVOKE ALL ON TABLE bags_of_words FROM PUBLIC;
REVOKE ALL ON TABLE bags_of_words FROM the_owner;
GRANT ALL ON TABLE bags_of_words TO the_owner;
GRANT SELECT,INSERT,UPDATE ON TABLE bags_of_words TO the_user;


--
-- Name: bags_of_words_id_seq; Type: ACL; Schema: public; Owner: the_owner
--

REVOKE ALL ON SEQUENCE bags_of_words_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE bags_of_words_id_seq FROM the_owner;
GRANT ALL ON SEQUENCE bags_of_words_id_seq TO the_owner;
GRANT SELECT,USAGE ON SEQUENCE bags_of_words_id_seq TO the_user;


--
-- Name: identities; Type: ACL; Schema: public; Owner: the_owner
--

REVOKE ALL ON TABLE identities FROM PUBLIC;
REVOKE ALL ON TABLE identities FROM the_owner;
GRANT ALL ON TABLE identities TO the_owner;
GRANT SELECT,INSERT,UPDATE ON TABLE identities TO the_user;


--
-- Name: identities_id_seq; Type: ACL; Schema: public; Owner: the_owner
--

REVOKE ALL ON SEQUENCE identities_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE identities_id_seq FROM the_owner;
GRANT ALL ON SEQUENCE identities_id_seq TO the_owner;
GRANT SELECT,USAGE ON SEQUENCE identities_id_seq TO the_user;


--
-- Name: responses; Type: ACL; Schema: public; Owner: the_owner
--

REVOKE ALL ON TABLE responses FROM PUBLIC;
REVOKE ALL ON TABLE responses FROM the_owner;
GRANT ALL ON TABLE responses TO the_owner;
GRANT SELECT,INSERT,UPDATE ON TABLE responses TO the_user;


--
-- Name: responses_id_seq; Type: ACL; Schema: public; Owner: the_owner
--

REVOKE ALL ON SEQUENCE responses_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE responses_id_seq FROM the_owner;
GRANT ALL ON SEQUENCE responses_id_seq TO the_owner;
GRANT SELECT,USAGE ON SEQUENCE responses_id_seq TO the_user;


--
-- Name: validations; Type: ACL; Schema: public; Owner: the_owner
--

REVOKE ALL ON TABLE validations FROM PUBLIC;
REVOKE ALL ON TABLE validations FROM the_owner;
GRANT ALL ON TABLE validations TO the_owner;
GRANT SELECT,INSERT,UPDATE ON TABLE validations TO the_user;


--
-- Name: validations_id_seq; Type: ACL; Schema: public; Owner: the_owner
--

REVOKE ALL ON SEQUENCE validations_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE validations_id_seq FROM the_owner;
GRANT ALL ON SEQUENCE validations_id_seq TO the_owner;
GRANT SELECT,USAGE ON SEQUENCE validations_id_seq TO the_user;


--
-- PostgreSQL database dump complete
--

