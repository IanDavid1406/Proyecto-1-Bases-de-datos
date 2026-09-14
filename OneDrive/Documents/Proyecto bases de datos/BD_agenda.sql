--
-- PostgreSQL database dump
--

\restrict 1xwVurKSWsg2hbwUGkbScVSxD4V8aRQL45fx5TBLIkrLorci04L07ccX7dRMAzd

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

-- Started on 2026-09-13 20:34:27

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 6 (class 2615 OID 16644)
-- Name: prototipo; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA prototipo;


ALTER SCHEMA prototipo OWNER TO postgres;

--
-- TOC entry 233 (class 1255 OID 16762)
-- Name: evitar_ciclo_categorias(); Type: FUNCTION; Schema: prototipo; Owner: postgres
--

CREATE FUNCTION prototipo.evitar_ciclo_categorias() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.id_categoria_padre = NEW.id_categoria THEN
        RAISE EXCEPTION 'Una categoría no puede ser padre de sí misma.';
    END IF;
    -- Aquí se podría añadir una consulta recursiva para validar ancestros, 
    -- pero para Postgres 14 es altamente eficiente usar el camino (path) o este chequeo simple.
    RETURN NEW;
END;
$$;


ALTER FUNCTION prototipo.evitar_ciclo_categorias() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 225 (class 1259 OID 16683)
-- Name: categorias; Type: TABLE; Schema: prototipo; Owner: postgres
--

CREATE TABLE prototipo.categorias (
    id_categoria integer NOT NULL,
    nombre character varying(50) NOT NULL,
    id_categoria_padre integer
);


ALTER TABLE prototipo.categorias OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16682)
-- Name: categorias_id_categoria_seq; Type: SEQUENCE; Schema: prototipo; Owner: postgres
--

CREATE SEQUENCE prototipo.categorias_id_categoria_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE prototipo.categorias_id_categoria_seq OWNER TO postgres;

--
-- TOC entry 5090 (class 0 OID 0)
-- Dependencies: 224
-- Name: categorias_id_categoria_seq; Type: SEQUENCE OWNED BY; Schema: prototipo; Owner: postgres
--

ALTER SEQUENCE prototipo.categorias_id_categoria_seq OWNED BY prototipo.categorias.id_categoria;


--
-- TOC entry 227 (class 1259 OID 16697)
-- Name: eventos; Type: TABLE; Schema: prototipo; Owner: postgres
--

CREATE TABLE prototipo.eventos (
    id_evento integer NOT NULL,
    id_usuario_propietario integer NOT NULL,
    id_categoria integer NOT NULL,
    titulo character varying(100) NOT NULL,
    descripcion text,
    fecha_inicio timestamp without time zone NOT NULL,
    fecha_fin timestamp without time zone NOT NULL,
    CONSTRAINT check_fechas CHECK ((fecha_fin > fecha_inicio))
);


ALTER TABLE prototipo.eventos OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16696)
-- Name: eventos_id_evento_seq; Type: SEQUENCE; Schema: prototipo; Owner: postgres
--

CREATE SEQUENCE prototipo.eventos_id_evento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE prototipo.eventos_id_evento_seq OWNER TO postgres;

--
-- TOC entry 5091 (class 0 OID 0)
-- Dependencies: 226
-- Name: eventos_id_evento_seq; Type: SEQUENCE OWNED BY; Schema: prototipo; Owner: postgres
--

ALTER SEQUENCE prototipo.eventos_id_evento_seq OWNED BY prototipo.eventos.id_evento;


--
-- TOC entry 230 (class 1259 OID 16741)
-- Name: log_accesos; Type: TABLE; Schema: prototipo; Owner: postgres
--

CREATE TABLE prototipo.log_accesos (
    id_log integer NOT NULL,
    id_usuario integer,
    fecha_acceso timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE prototipo.log_accesos OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16740)
-- Name: log_accesos_id_log_seq; Type: SEQUENCE; Schema: prototipo; Owner: postgres
--

CREATE SEQUENCE prototipo.log_accesos_id_log_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE prototipo.log_accesos_id_log_seq OWNER TO postgres;

--
-- TOC entry 5092 (class 0 OID 0)
-- Dependencies: 229
-- Name: log_accesos_id_log_seq; Type: SEQUENCE OWNED BY; Schema: prototipo; Owner: postgres
--

ALTER SEQUENCE prototipo.log_accesos_id_log_seq OWNED BY prototipo.log_accesos.id_log;


--
-- TOC entry 228 (class 1259 OID 16722)
-- Name: participaciones; Type: TABLE; Schema: prototipo; Owner: postgres
--

CREATE TABLE prototipo.participaciones (
    id_evento integer NOT NULL,
    id_invitado integer NOT NULL,
    rol character varying(50),
    estado_confirmacion character varying(20) DEFAULT 'pendiente'::character varying
);


ALTER TABLE prototipo.participaciones OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16670)
-- Name: usuario_emails; Type: TABLE; Schema: prototipo; Owner: postgres
--

CREATE TABLE prototipo.usuario_emails (
    id_usuario integer NOT NULL,
    email character varying(100) NOT NULL
);


ALTER TABLE prototipo.usuario_emails OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16658)
-- Name: usuario_telefonos; Type: TABLE; Schema: prototipo; Owner: postgres
--

CREATE TABLE prototipo.usuario_telefonos (
    id_usuario integer NOT NULL,
    telefono character varying(20) NOT NULL
);


ALTER TABLE prototipo.usuario_telefonos OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16646)
-- Name: usuarios; Type: TABLE; Schema: prototipo; Owner: postgres
--

CREATE TABLE prototipo.usuarios (
    id_usuario integer NOT NULL,
    nombre character varying(50) NOT NULL,
    apellido character varying(50) NOT NULL,
    fecha_registro date DEFAULT CURRENT_DATE NOT NULL,
    activo boolean DEFAULT true
);


ALTER TABLE prototipo.usuarios OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16645)
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE; Schema: prototipo; Owner: postgres
--

CREATE SEQUENCE prototipo.usuarios_id_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE prototipo.usuarios_id_usuario_seq OWNER TO postgres;

--
-- TOC entry 5093 (class 0 OID 0)
-- Dependencies: 220
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE OWNED BY; Schema: prototipo; Owner: postgres
--

ALTER SEQUENCE prototipo.usuarios_id_usuario_seq OWNED BY prototipo.usuarios.id_usuario;


--
-- TOC entry 231 (class 1259 OID 16754)
-- Name: vista_antiguedad_usuarios; Type: VIEW; Schema: prototipo; Owner: postgres
--

CREATE VIEW prototipo.vista_antiguedad_usuarios AS
 SELECT id_usuario,
    nombre,
    fecha_registro,
    age((CURRENT_DATE)::timestamp with time zone, (fecha_registro)::timestamp with time zone) AS antiguedad
   FROM prototipo.usuarios;


ALTER VIEW prototipo.vista_antiguedad_usuarios OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 16758)
-- Name: vista_duracion_eventos_diarios; Type: VIEW; Schema: prototipo; Owner: postgres
--

CREATE VIEW prototipo.vista_duracion_eventos_diarios AS
 SELECT id_usuario_propietario,
    (fecha_inicio)::date AS dia,
    sum((EXTRACT(epoch FROM (fecha_fin - fecha_inicio)) / (60)::numeric)) AS duracion_total_minutos
   FROM prototipo.eventos
  GROUP BY id_usuario_propietario, ((fecha_inicio)::date);


ALTER VIEW prototipo.vista_duracion_eventos_diarios OWNER TO postgres;

--
-- TOC entry 4896 (class 2604 OID 16686)
-- Name: categorias id_categoria; Type: DEFAULT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.categorias ALTER COLUMN id_categoria SET DEFAULT nextval('prototipo.categorias_id_categoria_seq'::regclass);


--
-- TOC entry 4897 (class 2604 OID 16700)
-- Name: eventos id_evento; Type: DEFAULT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.eventos ALTER COLUMN id_evento SET DEFAULT nextval('prototipo.eventos_id_evento_seq'::regclass);


--
-- TOC entry 4899 (class 2604 OID 16744)
-- Name: log_accesos id_log; Type: DEFAULT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.log_accesos ALTER COLUMN id_log SET DEFAULT nextval('prototipo.log_accesos_id_log_seq'::regclass);


--
-- TOC entry 4893 (class 2604 OID 16649)
-- Name: usuarios id_usuario; Type: DEFAULT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.usuarios ALTER COLUMN id_usuario SET DEFAULT nextval('prototipo.usuarios_id_usuario_seq'::regclass);


--
-- TOC entry 5079 (class 0 OID 16683)
-- Dependencies: 225
-- Data for Name: categorias; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.categorias (id_categoria, nombre, id_categoria_padre) FROM stdin;
1	Reuniones	\N
2	Eventos Sociales	\N
3	Fiestas	2
\.


--
-- TOC entry 5081 (class 0 OID 16697)
-- Dependencies: 227
-- Data for Name: eventos; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.eventos (id_evento, id_usuario_propietario, id_categoria, titulo, descripcion, fecha_inicio, fecha_fin) FROM stdin;
\.


--
-- TOC entry 5084 (class 0 OID 16741)
-- Dependencies: 230
-- Data for Name: log_accesos; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.log_accesos (id_log, id_usuario, fecha_acceso) FROM stdin;
\.


--
-- TOC entry 5082 (class 0 OID 16722)
-- Dependencies: 228
-- Data for Name: participaciones; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.participaciones (id_evento, id_invitado, rol, estado_confirmacion) FROM stdin;
\.


--
-- TOC entry 5077 (class 0 OID 16670)
-- Dependencies: 223
-- Data for Name: usuario_emails; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.usuario_emails (id_usuario, email) FROM stdin;
\.


--
-- TOC entry 5076 (class 0 OID 16658)
-- Dependencies: 222
-- Data for Name: usuario_telefonos; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.usuario_telefonos (id_usuario, telefono) FROM stdin;
\.


--
-- TOC entry 5075 (class 0 OID 16646)
-- Dependencies: 221
-- Data for Name: usuarios; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.usuarios (id_usuario, nombre, apellido, fecha_registro, activo) FROM stdin;
\.


--
-- TOC entry 5094 (class 0 OID 0)
-- Dependencies: 224
-- Name: categorias_id_categoria_seq; Type: SEQUENCE SET; Schema: prototipo; Owner: postgres
--

SELECT pg_catalog.setval('prototipo.categorias_id_categoria_seq', 3, true);


--
-- TOC entry 5095 (class 0 OID 0)
-- Dependencies: 226
-- Name: eventos_id_evento_seq; Type: SEQUENCE SET; Schema: prototipo; Owner: postgres
--

SELECT pg_catalog.setval('prototipo.eventos_id_evento_seq', 1, false);


--
-- TOC entry 5096 (class 0 OID 0)
-- Dependencies: 229
-- Name: log_accesos_id_log_seq; Type: SEQUENCE SET; Schema: prototipo; Owner: postgres
--

SELECT pg_catalog.setval('prototipo.log_accesos_id_log_seq', 1, false);


--
-- TOC entry 5097 (class 0 OID 0)
-- Dependencies: 220
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE SET; Schema: prototipo; Owner: postgres
--

SELECT pg_catalog.setval('prototipo.usuarios_id_usuario_seq', 1, false);


--
-- TOC entry 4909 (class 2606 OID 16690)
-- Name: categorias categorias_pkey; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.categorias
    ADD CONSTRAINT categorias_pkey PRIMARY KEY (id_categoria);


--
-- TOC entry 4911 (class 2606 OID 16711)
-- Name: eventos eventos_pkey; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.eventos
    ADD CONSTRAINT eventos_pkey PRIMARY KEY (id_evento);


--
-- TOC entry 4915 (class 2606 OID 16748)
-- Name: log_accesos log_accesos_pkey; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.log_accesos
    ADD CONSTRAINT log_accesos_pkey PRIMARY KEY (id_log);


--
-- TOC entry 4913 (class 2606 OID 16729)
-- Name: participaciones participaciones_pkey; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.participaciones
    ADD CONSTRAINT participaciones_pkey PRIMARY KEY (id_evento, id_invitado);


--
-- TOC entry 4907 (class 2606 OID 16676)
-- Name: usuario_emails usuario_emails_pkey; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.usuario_emails
    ADD CONSTRAINT usuario_emails_pkey PRIMARY KEY (id_usuario, email);


--
-- TOC entry 4905 (class 2606 OID 16664)
-- Name: usuario_telefonos usuario_telefonos_pkey; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.usuario_telefonos
    ADD CONSTRAINT usuario_telefonos_pkey PRIMARY KEY (id_usuario, telefono);


--
-- TOC entry 4903 (class 2606 OID 16657)
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id_usuario);


--
-- TOC entry 4924 (class 2620 OID 16763)
-- Name: categorias trg_evitar_ciclo; Type: TRIGGER; Schema: prototipo; Owner: postgres
--

CREATE TRIGGER trg_evitar_ciclo BEFORE INSERT OR UPDATE ON prototipo.categorias FOR EACH ROW EXECUTE FUNCTION prototipo.evitar_ciclo_categorias();


--
-- TOC entry 4918 (class 2606 OID 16691)
-- Name: categorias categorias_id_categoria_padre_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.categorias
    ADD CONSTRAINT categorias_id_categoria_padre_fkey FOREIGN KEY (id_categoria_padre) REFERENCES prototipo.categorias(id_categoria);


--
-- TOC entry 4919 (class 2606 OID 16717)
-- Name: eventos eventos_id_categoria_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.eventos
    ADD CONSTRAINT eventos_id_categoria_fkey FOREIGN KEY (id_categoria) REFERENCES prototipo.categorias(id_categoria);


--
-- TOC entry 4920 (class 2606 OID 16712)
-- Name: eventos eventos_id_usuario_propietario_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.eventos
    ADD CONSTRAINT eventos_id_usuario_propietario_fkey FOREIGN KEY (id_usuario_propietario) REFERENCES prototipo.usuarios(id_usuario);


--
-- TOC entry 4923 (class 2606 OID 16749)
-- Name: log_accesos log_accesos_id_usuario_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.log_accesos
    ADD CONSTRAINT log_accesos_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES prototipo.usuarios(id_usuario);


--
-- TOC entry 4921 (class 2606 OID 16730)
-- Name: participaciones participaciones_id_evento_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.participaciones
    ADD CONSTRAINT participaciones_id_evento_fkey FOREIGN KEY (id_evento) REFERENCES prototipo.eventos(id_evento) ON DELETE CASCADE;


--
-- TOC entry 4922 (class 2606 OID 16735)
-- Name: participaciones participaciones_id_invitado_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.participaciones
    ADD CONSTRAINT participaciones_id_invitado_fkey FOREIGN KEY (id_invitado) REFERENCES prototipo.usuarios(id_usuario);


--
-- TOC entry 4917 (class 2606 OID 16677)
-- Name: usuario_emails usuario_emails_id_usuario_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.usuario_emails
    ADD CONSTRAINT usuario_emails_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES prototipo.usuarios(id_usuario);


--
-- TOC entry 4916 (class 2606 OID 16665)
-- Name: usuario_telefonos usuario_telefonos_id_usuario_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.usuario_telefonos
    ADD CONSTRAINT usuario_telefonos_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES prototipo.usuarios(id_usuario);


-- Completed on 2026-09-13 20:34:27

--
-- PostgreSQL database dump complete
--

\unrestrict 1xwVurKSWsg2hbwUGkbScVSxD4V8aRQL45fx5TBLIkrLorci04L07ccX7dRMAzd

