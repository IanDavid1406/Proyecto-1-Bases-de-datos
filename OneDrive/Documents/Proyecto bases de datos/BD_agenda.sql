--
-- PostgreSQL database dump
--

\restrict epMRaFPrb0oTU6cajI375W7sc9512GP7315TKL2BgytaB2owgbXF2RnA6wpLVAT

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

-- Started on 2026-09-14 17:44:38

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
-- TOC entry 242 (class 1255 OID 16762)
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

--
-- TOC entry 244 (class 1255 OID 16805)
-- Name: fn_evitar_traslape_disponibilidad(); Type: FUNCTION; Schema: prototipo; Owner: postgres
--

CREATE FUNCTION prototipo.fn_evitar_traslape_disponibilidad() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    conflicto BOOLEAN;
BEGIN
    IF TG_OP = 'INSERT' THEN
        SELECT EXISTS (
            SELECT 1 FROM prototipo.disponibilidad_y_gestion d
            WHERE d.id_usuario = NEW.id_usuario
              AND d.dia_semana = NEW.dia_semana
              AND (NEW.hora_inicio, NEW.hora_fin) OVERLAPS (d.hora_inicio, d.hora_fin)
        ) INTO conflicto;
    ELSE -- UPDATE
        SELECT EXISTS (
            SELECT 1 FROM prototipo.disponibilidad_y_gestion d
            WHERE d.id_usuario = NEW.id_usuario
              AND d.dia_semana = NEW.dia_semana
              AND d.hora_inicio <> OLD.hora_inicio
              AND (NEW.hora_inicio, NEW.hora_fin) OVERLAPS (d.hora_inicio, d.hora_fin)
        ) INTO conflicto;
    END IF;

    IF conflicto THEN
        RAISE EXCEPTION 'Ya existe un bloque de disponibilidad que se traslapa para este usuario en ese día.';
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION prototipo.fn_evitar_traslape_disponibilidad() OWNER TO postgres;

--
-- TOC entry 243 (class 1255 OID 16783)
-- Name: fn_evitar_traslape_ubicacion(); Type: FUNCTION; Schema: prototipo; Owner: postgres
--

CREATE FUNCTION prototipo.fn_evitar_traslape_ubicacion() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.id_ubicacion IS NOT NULL THEN
        IF EXISTS (
            SELECT 1
            FROM prototipo.eventos e
            WHERE e.id_ubicacion = NEW.id_ubicacion
              AND e.id_evento <> NEW.id_evento
              AND (NEW.fecha_inicio, NEW.fecha_fin) OVERLAPS (e.fecha_inicio, e.fecha_fin)
        ) THEN
            RAISE EXCEPTION 'La ubicación % ya está asignada a otro evento en ese horario.', NEW.id_ubicacion;
        END IF;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION prototipo.fn_evitar_traslape_ubicacion() OWNER TO postgres;

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
-- TOC entry 5155 (class 0 OID 0)
-- Dependencies: 224
-- Name: categorias_id_categoria_seq; Type: SEQUENCE OWNED BY; Schema: prototipo; Owner: postgres
--

ALTER SEQUENCE prototipo.categorias_id_categoria_seq OWNED BY prototipo.categorias.id_categoria;


--
-- TOC entry 235 (class 1259 OID 16785)
-- Name: disponibilidad_y_gestion; Type: TABLE; Schema: prototipo; Owner: postgres
--

CREATE TABLE prototipo.disponibilidad_y_gestion (
    id_usuario integer NOT NULL,
    dia_semana integer NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fin time without time zone NOT NULL,
    CONSTRAINT chk_dia_semana_valido CHECK (((dia_semana >= 1) AND (dia_semana <= 7))),
    CONSTRAINT chk_rango_horas_disponibilidad CHECK ((hora_fin > hora_inicio))
);


ALTER TABLE prototipo.disponibilidad_y_gestion OWNER TO postgres;

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
    id_ubicacion integer,
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
-- TOC entry 5156 (class 0 OID 0)
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
-- TOC entry 5157 (class 0 OID 0)
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
-- TOC entry 241 (class 1259 OID 16840)
-- Name: tarea_usuario_asignado; Type: TABLE; Schema: prototipo; Owner: postgres
--

CREATE TABLE prototipo.tarea_usuario_asignado (
    id_tarea integer NOT NULL,
    id_usuario integer NOT NULL
);


ALTER TABLE prototipo.tarea_usuario_asignado OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 16812)
-- Name: tareas_evento; Type: TABLE; Schema: prototipo; Owner: postgres
--

CREATE TABLE prototipo.tareas_evento (
    id_tarea integer NOT NULL,
    id_evento integer NOT NULL,
    descripcion text NOT NULL,
    fecha_limite timestamp without time zone NOT NULL,
    prioridad character varying(20) DEFAULT 'media'::character varying NOT NULL,
    estado character varying(20) DEFAULT 'pendiente'::character varying NOT NULL,
    CONSTRAINT chk_estado_enum CHECK (((estado)::text = ANY ((ARRAY['pendiente'::character varying, 'en_progreso'::character varying, 'completada'::character varying, 'cancelada'::character varying])::text[]))),
    CONSTRAINT chk_prioridad_enum CHECK (((prioridad)::text = ANY ((ARRAY['baja'::character varying, 'media'::character varying, 'alta'::character varying, 'critica'::character varying])::text[])))
);


ALTER TABLE prototipo.tareas_evento OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 16811)
-- Name: tareas_evento_id_tarea_seq; Type: SEQUENCE; Schema: prototipo; Owner: postgres
--

CREATE SEQUENCE prototipo.tareas_evento_id_tarea_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE prototipo.tareas_evento_id_tarea_seq OWNER TO postgres;

--
-- TOC entry 5158 (class 0 OID 0)
-- Dependencies: 238
-- Name: tareas_evento_id_tarea_seq; Type: SEQUENCE OWNED BY; Schema: prototipo; Owner: postgres
--

ALTER SEQUENCE prototipo.tareas_evento_id_tarea_seq OWNED BY prototipo.tareas_evento.id_tarea;


--
-- TOC entry 234 (class 1259 OID 16765)
-- Name: ubicaciones; Type: TABLE; Schema: prototipo; Owner: postgres
--

CREATE TABLE prototipo.ubicaciones (
    id_ubicacion integer NOT NULL,
    tipo_ubicacion character varying(50) NOT NULL,
    capacidad integer NOT NULL,
    direccion text NOT NULL,
    CONSTRAINT chk_capacidad_positiva CHECK ((capacidad > 0))
);


ALTER TABLE prototipo.ubicaciones OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 16764)
-- Name: ubicaciones_id_ubicacion_seq; Type: SEQUENCE; Schema: prototipo; Owner: postgres
--

CREATE SEQUENCE prototipo.ubicaciones_id_ubicacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE prototipo.ubicaciones_id_ubicacion_seq OWNER TO postgres;

--
-- TOC entry 5159 (class 0 OID 0)
-- Dependencies: 233
-- Name: ubicaciones_id_ubicacion_seq; Type: SEQUENCE OWNED BY; Schema: prototipo; Owner: postgres
--

ALTER SEQUENCE prototipo.ubicaciones_id_ubicacion_seq OWNED BY prototipo.ubicaciones.id_ubicacion;


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
-- TOC entry 5160 (class 0 OID 0)
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
-- TOC entry 237 (class 1259 OID 16807)
-- Name: vista_concurrencia_usuarios; Type: VIEW; Schema: prototipo; Owner: postgres
--

CREATE VIEW prototipo.vista_concurrencia_usuarios AS
 SELECT a.id_usuario AS usuario_1,
    b.id_usuario AS usuario_2,
    a.dia_semana,
    GREATEST(a.hora_inicio, b.hora_inicio) AS inicio_comun,
    LEAST(a.hora_fin, b.hora_fin) AS fin_comun
   FROM (prototipo.disponibilidad_y_gestion a
     JOIN prototipo.disponibilidad_y_gestion b ON (((a.dia_semana = b.dia_semana) AND (a.id_usuario < b.id_usuario) AND ((a.hora_inicio, a.hora_fin) OVERLAPS (b.hora_inicio, b.hora_fin)))));


ALTER VIEW prototipo.vista_concurrencia_usuarios OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 16801)
-- Name: vista_disponibilidad_usuarios; Type: VIEW; Schema: prototipo; Owner: postgres
--

CREATE VIEW prototipo.vista_disponibilidad_usuarios AS
 SELECT u.id_usuario,
    u.nombre,
    u.apellido,
    d.dia_semana,
    d.hora_inicio,
    d.hora_fin
   FROM (prototipo.usuarios u
     JOIN prototipo.disponibilidad_y_gestion d ON ((u.id_usuario = d.id_usuario)))
  WHERE (u.activo = true)
  ORDER BY d.dia_semana, d.hora_inicio;


ALTER VIEW prototipo.vista_disponibilidad_usuarios OWNER TO postgres;

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
-- TOC entry 240 (class 1259 OID 16835)
-- Name: vista_tareas_vencidas; Type: VIEW; Schema: prototipo; Owner: postgres
--

CREATE VIEW prototipo.vista_tareas_vencidas AS
 SELECT t.id_tarea,
    t.descripcion,
    t.fecha_limite,
    t.prioridad,
    t.estado,
    e.titulo AS evento
   FROM (prototipo.tareas_evento t
     JOIN prototipo.eventos e ON ((t.id_evento = e.id_evento)))
  WHERE ((t.fecha_limite < CURRENT_TIMESTAMP) AND ((t.estado)::text <> 'completada'::text));


ALTER VIEW prototipo.vista_tareas_vencidas OWNER TO postgres;

--
-- TOC entry 4928 (class 2604 OID 16686)
-- Name: categorias id_categoria; Type: DEFAULT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.categorias ALTER COLUMN id_categoria SET DEFAULT nextval('prototipo.categorias_id_categoria_seq'::regclass);


--
-- TOC entry 4929 (class 2604 OID 16700)
-- Name: eventos id_evento; Type: DEFAULT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.eventos ALTER COLUMN id_evento SET DEFAULT nextval('prototipo.eventos_id_evento_seq'::regclass);


--
-- TOC entry 4931 (class 2604 OID 16744)
-- Name: log_accesos id_log; Type: DEFAULT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.log_accesos ALTER COLUMN id_log SET DEFAULT nextval('prototipo.log_accesos_id_log_seq'::regclass);


--
-- TOC entry 4934 (class 2604 OID 16815)
-- Name: tareas_evento id_tarea; Type: DEFAULT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.tareas_evento ALTER COLUMN id_tarea SET DEFAULT nextval('prototipo.tareas_evento_id_tarea_seq'::regclass);


--
-- TOC entry 4933 (class 2604 OID 16768)
-- Name: ubicaciones id_ubicacion; Type: DEFAULT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.ubicaciones ALTER COLUMN id_ubicacion SET DEFAULT nextval('prototipo.ubicaciones_id_ubicacion_seq'::regclass);


--
-- TOC entry 4925 (class 2604 OID 16649)
-- Name: usuarios id_usuario; Type: DEFAULT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.usuarios ALTER COLUMN id_usuario SET DEFAULT nextval('prototipo.usuarios_id_usuario_seq'::regclass);


--
-- TOC entry 5138 (class 0 OID 16683)
-- Dependencies: 225
-- Data for Name: categorias; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.categorias (id_categoria, nombre, id_categoria_padre) FROM stdin;
1	Reuniones	\N
2	Eventos Sociales	\N
3	Fiestas	2
\.


--
-- TOC entry 5146 (class 0 OID 16785)
-- Dependencies: 235
-- Data for Name: disponibilidad_y_gestion; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.disponibilidad_y_gestion (id_usuario, dia_semana, hora_inicio, hora_fin) FROM stdin;
\.


--
-- TOC entry 5140 (class 0 OID 16697)
-- Dependencies: 227
-- Data for Name: eventos; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.eventos (id_evento, id_usuario_propietario, id_categoria, titulo, descripcion, fecha_inicio, fecha_fin, id_ubicacion) FROM stdin;
\.


--
-- TOC entry 5143 (class 0 OID 16741)
-- Dependencies: 230
-- Data for Name: log_accesos; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.log_accesos (id_log, id_usuario, fecha_acceso) FROM stdin;
\.


--
-- TOC entry 5141 (class 0 OID 16722)
-- Dependencies: 228
-- Data for Name: participaciones; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.participaciones (id_evento, id_invitado, rol, estado_confirmacion) FROM stdin;
\.


--
-- TOC entry 5149 (class 0 OID 16840)
-- Dependencies: 241
-- Data for Name: tarea_usuario_asignado; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.tarea_usuario_asignado (id_tarea, id_usuario) FROM stdin;
\.


--
-- TOC entry 5148 (class 0 OID 16812)
-- Dependencies: 239
-- Data for Name: tareas_evento; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.tareas_evento (id_tarea, id_evento, descripcion, fecha_limite, prioridad, estado) FROM stdin;
\.


--
-- TOC entry 5145 (class 0 OID 16765)
-- Dependencies: 234
-- Data for Name: ubicaciones; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.ubicaciones (id_ubicacion, tipo_ubicacion, capacidad, direccion) FROM stdin;
\.


--
-- TOC entry 5136 (class 0 OID 16670)
-- Dependencies: 223
-- Data for Name: usuario_emails; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.usuario_emails (id_usuario, email) FROM stdin;
\.


--
-- TOC entry 5135 (class 0 OID 16658)
-- Dependencies: 222
-- Data for Name: usuario_telefonos; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.usuario_telefonos (id_usuario, telefono) FROM stdin;
\.


--
-- TOC entry 5134 (class 0 OID 16646)
-- Dependencies: 221
-- Data for Name: usuarios; Type: TABLE DATA; Schema: prototipo; Owner: postgres
--

COPY prototipo.usuarios (id_usuario, nombre, apellido, fecha_registro, activo) FROM stdin;
\.


--
-- TOC entry 5161 (class 0 OID 0)
-- Dependencies: 224
-- Name: categorias_id_categoria_seq; Type: SEQUENCE SET; Schema: prototipo; Owner: postgres
--

SELECT pg_catalog.setval('prototipo.categorias_id_categoria_seq', 3, true);


--
-- TOC entry 5162 (class 0 OID 0)
-- Dependencies: 226
-- Name: eventos_id_evento_seq; Type: SEQUENCE SET; Schema: prototipo; Owner: postgres
--

SELECT pg_catalog.setval('prototipo.eventos_id_evento_seq', 1, false);


--
-- TOC entry 5163 (class 0 OID 0)
-- Dependencies: 229
-- Name: log_accesos_id_log_seq; Type: SEQUENCE SET; Schema: prototipo; Owner: postgres
--

SELECT pg_catalog.setval('prototipo.log_accesos_id_log_seq', 1, false);


--
-- TOC entry 5164 (class 0 OID 0)
-- Dependencies: 238
-- Name: tareas_evento_id_tarea_seq; Type: SEQUENCE SET; Schema: prototipo; Owner: postgres
--

SELECT pg_catalog.setval('prototipo.tareas_evento_id_tarea_seq', 1, false);


--
-- TOC entry 5165 (class 0 OID 0)
-- Dependencies: 233
-- Name: ubicaciones_id_ubicacion_seq; Type: SEQUENCE SET; Schema: prototipo; Owner: postgres
--

SELECT pg_catalog.setval('prototipo.ubicaciones_id_ubicacion_seq', 1, false);


--
-- TOC entry 5166 (class 0 OID 0)
-- Dependencies: 220
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE SET; Schema: prototipo; Owner: postgres
--

SELECT pg_catalog.setval('prototipo.usuarios_id_usuario_seq', 1, false);


--
-- TOC entry 4950 (class 2606 OID 16690)
-- Name: categorias categorias_pkey; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.categorias
    ADD CONSTRAINT categorias_pkey PRIMARY KEY (id_categoria);


--
-- TOC entry 4952 (class 2606 OID 16711)
-- Name: eventos eventos_pkey; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.eventos
    ADD CONSTRAINT eventos_pkey PRIMARY KEY (id_evento);


--
-- TOC entry 4956 (class 2606 OID 16748)
-- Name: log_accesos log_accesos_pkey; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.log_accesos
    ADD CONSTRAINT log_accesos_pkey PRIMARY KEY (id_log);


--
-- TOC entry 4954 (class 2606 OID 16729)
-- Name: participaciones participaciones_pkey; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.participaciones
    ADD CONSTRAINT participaciones_pkey PRIMARY KEY (id_evento, id_invitado);


--
-- TOC entry 4960 (class 2606 OID 16795)
-- Name: disponibilidad_y_gestion pk_disponibilidad_y_gestion; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.disponibilidad_y_gestion
    ADD CONSTRAINT pk_disponibilidad_y_gestion PRIMARY KEY (id_usuario, dia_semana, hora_inicio);


--
-- TOC entry 4964 (class 2606 OID 16846)
-- Name: tarea_usuario_asignado pk_tarea_usuario_asignado; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.tarea_usuario_asignado
    ADD CONSTRAINT pk_tarea_usuario_asignado PRIMARY KEY (id_tarea, id_usuario);


--
-- TOC entry 4962 (class 2606 OID 16826)
-- Name: tareas_evento pk_tareas_evento; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.tareas_evento
    ADD CONSTRAINT pk_tareas_evento PRIMARY KEY (id_tarea);


--
-- TOC entry 4958 (class 2606 OID 16777)
-- Name: ubicaciones pk_ubicaciones; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.ubicaciones
    ADD CONSTRAINT pk_ubicaciones PRIMARY KEY (id_ubicacion);


--
-- TOC entry 4948 (class 2606 OID 16676)
-- Name: usuario_emails usuario_emails_pkey; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.usuario_emails
    ADD CONSTRAINT usuario_emails_pkey PRIMARY KEY (id_usuario, email);


--
-- TOC entry 4946 (class 2606 OID 16664)
-- Name: usuario_telefonos usuario_telefonos_pkey; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.usuario_telefonos
    ADD CONSTRAINT usuario_telefonos_pkey PRIMARY KEY (id_usuario, telefono);


--
-- TOC entry 4944 (class 2606 OID 16657)
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id_usuario);


--
-- TOC entry 4978 (class 2620 OID 16763)
-- Name: categorias trg_evitar_ciclo; Type: TRIGGER; Schema: prototipo; Owner: postgres
--

CREATE TRIGGER trg_evitar_ciclo BEFORE INSERT OR UPDATE ON prototipo.categorias FOR EACH ROW EXECUTE FUNCTION prototipo.evitar_ciclo_categorias();


--
-- TOC entry 4980 (class 2620 OID 16806)
-- Name: disponibilidad_y_gestion trg_evitar_traslape_disponibilidad; Type: TRIGGER; Schema: prototipo; Owner: postgres
--

CREATE TRIGGER trg_evitar_traslape_disponibilidad BEFORE INSERT OR UPDATE ON prototipo.disponibilidad_y_gestion FOR EACH ROW EXECUTE FUNCTION prototipo.fn_evitar_traslape_disponibilidad();


--
-- TOC entry 4979 (class 2620 OID 16784)
-- Name: eventos trg_evitar_traslape_ubicacion; Type: TRIGGER; Schema: prototipo; Owner: postgres
--

CREATE TRIGGER trg_evitar_traslape_ubicacion BEFORE INSERT OR UPDATE ON prototipo.eventos FOR EACH ROW EXECUTE FUNCTION prototipo.fn_evitar_traslape_ubicacion();


--
-- TOC entry 4967 (class 2606 OID 16691)
-- Name: categorias categorias_id_categoria_padre_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.categorias
    ADD CONSTRAINT categorias_id_categoria_padre_fkey FOREIGN KEY (id_categoria_padre) REFERENCES prototipo.categorias(id_categoria);


--
-- TOC entry 4968 (class 2606 OID 16717)
-- Name: eventos eventos_id_categoria_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.eventos
    ADD CONSTRAINT eventos_id_categoria_fkey FOREIGN KEY (id_categoria) REFERENCES prototipo.categorias(id_categoria);


--
-- TOC entry 4969 (class 2606 OID 16778)
-- Name: eventos eventos_id_ubicacion_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.eventos
    ADD CONSTRAINT eventos_id_ubicacion_fkey FOREIGN KEY (id_ubicacion) REFERENCES prototipo.ubicaciones(id_ubicacion);


--
-- TOC entry 4970 (class 2606 OID 16712)
-- Name: eventos eventos_id_usuario_propietario_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.eventos
    ADD CONSTRAINT eventos_id_usuario_propietario_fkey FOREIGN KEY (id_usuario_propietario) REFERENCES prototipo.usuarios(id_usuario);


--
-- TOC entry 4976 (class 2606 OID 16847)
-- Name: tarea_usuario_asignado fk_asig_tarea; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.tarea_usuario_asignado
    ADD CONSTRAINT fk_asig_tarea FOREIGN KEY (id_tarea) REFERENCES prototipo.tareas_evento(id_tarea) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 4977 (class 2606 OID 16852)
-- Name: tarea_usuario_asignado fk_asig_usuario; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.tarea_usuario_asignado
    ADD CONSTRAINT fk_asig_usuario FOREIGN KEY (id_usuario) REFERENCES prototipo.usuarios(id_usuario) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 4974 (class 2606 OID 16796)
-- Name: disponibilidad_y_gestion fk_disponibilidad_usuario; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.disponibilidad_y_gestion
    ADD CONSTRAINT fk_disponibilidad_usuario FOREIGN KEY (id_usuario) REFERENCES prototipo.usuarios(id_usuario) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 4975 (class 2606 OID 16827)
-- Name: tareas_evento fk_tareas_evento_evento; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.tareas_evento
    ADD CONSTRAINT fk_tareas_evento_evento FOREIGN KEY (id_evento) REFERENCES prototipo.eventos(id_evento) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 4973 (class 2606 OID 16749)
-- Name: log_accesos log_accesos_id_usuario_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.log_accesos
    ADD CONSTRAINT log_accesos_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES prototipo.usuarios(id_usuario);


--
-- TOC entry 4971 (class 2606 OID 16730)
-- Name: participaciones participaciones_id_evento_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.participaciones
    ADD CONSTRAINT participaciones_id_evento_fkey FOREIGN KEY (id_evento) REFERENCES prototipo.eventos(id_evento) ON DELETE CASCADE;


--
-- TOC entry 4972 (class 2606 OID 16735)
-- Name: participaciones participaciones_id_invitado_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.participaciones
    ADD CONSTRAINT participaciones_id_invitado_fkey FOREIGN KEY (id_invitado) REFERENCES prototipo.usuarios(id_usuario);


--
-- TOC entry 4966 (class 2606 OID 16677)
-- Name: usuario_emails usuario_emails_id_usuario_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.usuario_emails
    ADD CONSTRAINT usuario_emails_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES prototipo.usuarios(id_usuario);


--
-- TOC entry 4965 (class 2606 OID 16665)
-- Name: usuario_telefonos usuario_telefonos_id_usuario_fkey; Type: FK CONSTRAINT; Schema: prototipo; Owner: postgres
--

ALTER TABLE ONLY prototipo.usuario_telefonos
    ADD CONSTRAINT usuario_telefonos_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES prototipo.usuarios(id_usuario);


-- Completed on 2026-09-14 17:44:38

--
-- PostgreSQL database dump complete
--

\unrestrict epMRaFPrb0oTU6cajI375W7sc9512GP7315TKL2BgytaB2owgbXF2RnA6wpLVAT

