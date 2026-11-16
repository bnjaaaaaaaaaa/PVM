import os
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Conservación Marina - PMV", page_icon="🌊", layout="wide")

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "conservacion_marina_db")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "root")

@st.cache_resource
def get_engine():
    url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    return create_engine(url, pool_pre_ping=True)

engine = get_engine()

def get_enum_values(table, column, fallback):
    try:
        res = pd.read_sql(text(f"SHOW COLUMNS FROM {table} LIKE '{column}'"), engine)
        type_str = str(res.iloc[0]["Type"])
        if type_str.lower().startswith("enum("):
            vals = type_str[5:-1].split(",")
            return [v.strip().strip("'") for v in vals]
    except Exception:
        pass
    return fallback

# --- 1. CONTROL DE USUARIOS Y ROLES ---
st.sidebar.title("🌊 Sistema Marino")
if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None

if st.session_state.usuario_activo is None:
    st.sidebar.subheader("Inicio de Sesión")
    with st.sidebar.form("login_form"):
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        submit_login = st.form_submit_button("Ingresar")

    with st.sidebar.expander("🔑 Ver usuarios disponibles en la BD"):
        try:
            df_demo = pd.read_sql(text("""
                SELECT u.username, u.password, GROUP_CONCAT(r.nombre_rol SEPARATOR ', ') AS rol
                FROM usuarios u
                JOIN usuarios_roles ur ON u.id_usuario = ur.id_usuario
                JOIN roles r ON ur.id_rol = r.id_rol
                WHERE u.activo = 1 AND u.estado_cuenta = 'Activa'
                GROUP BY u.id_usuario, u.username, u.password
                LIMIT 6
            """), engine)
            st.dataframe(df_demo, hide_index=True, use_container_width=True)
        except Exception as e:
            st.error(f"Error conectando a BD: {e}")

    if submit_login:
        query = text("""
            SELECT u.id_usuario, u.username, t.nombre, GROUP_CONCAT(r.nombre_rol SEPARATOR ', ') AS nombre_rol
            FROM usuarios u
            JOIN trabajadores t ON u.id_trabajador = t.id_trabajador
            JOIN usuarios_roles ur ON u.id_usuario = ur.id_usuario
            JOIN roles r ON ur.id_rol = r.id_rol
            WHERE u.username = :u AND u.password = :p
              AND u.activo = 1 AND u.estado_cuenta = 'Activa'
            GROUP BY u.id_usuario, u.username, t.nombre
        """)
        df_u = pd.read_sql(query, engine, params={"u": user_input, "p": pass_input})
        if not df_u.empty:
            st.session_state.usuario_activo = df_u.iloc[0].to_dict()
            st.rerun()
        else:
            st.sidebar.error("Credenciales inválidas o cuenta suspendida.")
    st.title("🌊 Sistema Integral de Gestión de Centros de Conservación Marina")
    st.info("Inicia sesión en el panel izquierdo con un usuario activo para acceder a los módulos.")
    st.stop()

user = st.session_state.usuario_activo
st.sidebar.success(f"👤 **{user['nombre']}**\n\nRol: `{user['nombre_rol']}`")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.usuario_activo = None
    st.rerun()

modulo = st.sidebar.radio(
    "Navegación",
    ["📊 Dashboard Analítico", "📝 Operaciones Transaccionales", "⚙️ Gestión CRUD"]
)

# --- 2. DASHBOARD ANALÍTICO ---
if modulo == "📊 Dashboard Analítico":
    st.title("📊 Dashboard de Conservación Marina")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Centros Activos", pd.read_sql(text("SELECT COUNT(*) c FROM centros_conservacion WHERE activo=1"), engine)["c"][0])
    c2.metric("Especies Registradas", pd.read_sql(text("SELECT COUNT(*) c FROM especies WHERE activo=1"), engine)["c"][0])
    c3.metric("Monitoreos Científicos", pd.read_sql(text("SELECT COUNT(*) c FROM monitoreos"), engine)["c"][0])
    c4.metric("Inscripciones Actividades", pd.read_sql(text("SELECT COUNT(*) c FROM participacion_actividades"), engine)["c"][0])

    # Filtros generales (centro y período)
    df_cen = pd.read_sql(text("SELECT codigo_centro, nombre FROM centros_conservacion WHERE activo=1 ORDER BY nombre"), engine)
    rango = pd.read_sql(text("SELECT MIN(fecha_actividad) ini, MAX(fecha_actividad) fin FROM actividades"), engine)
    f1, f2, f3 = st.columns([2, 1, 1])
    centro_sel = f1.selectbox("Centro", [None] + df_cen["codigo_centro"].tolist(),
                              format_func=lambda x: "Todos los centros" if x is None else df_cen.loc[df_cen["codigo_centro"]==x, "nombre"].values[0])
    fecha_ini = f2.date_input("Desde", value=rango["ini"][0])
    fecha_fin = f3.date_input("Hasta", value=rango["fin"][0])
    params = {"c": centro_sel, "ini": fecha_ini, "fin": fecha_fin}

    # Pregunta 1 (Fase 1)
    st.subheader("1. Sectores con más actividades y visitantes")
    df1 = pd.read_sql(text("""
        SELECT CONCAT(s.nombre, ' (', c.nombre, ')') AS sector,
               COUNT(DISTINCT a.id_actividad) AS actividades,
               COUNT(DISTINCT p.id_visitante) AS visitantes
        FROM actividades a
        JOIN sectores_marinos s ON s.num_sector = a.num_sector AND s.codigo_centro = a.codigo_centro
        JOIN centros_conservacion c ON c.codigo_centro = s.codigo_centro
        LEFT JOIN participacion_actividades p ON p.id_actividad = a.id_actividad
        WHERE a.activo = 1
          AND (:c IS NULL OR a.codigo_centro = :c)
          AND a.fecha_actividad BETWEEN :ini AND :fin
        GROUP BY s.codigo_centro, s.num_sector, s.nombre, c.nombre
        ORDER BY actividades DESC, visitantes DESC
        LIMIT 10
    """), engine, params=params)
    if df1.empty:
        st.info("No hay actividades con esos filtros.")
    else:
        fig1 = px.bar(df1.sort_values("actividades"), x="actividades", y="sector", orientation="h",
                      color="visitantes", hover_data=["visitantes"], labels={"actividades": "Actividades", "sector": ""})
        st.plotly_chart(fig1, use_container_width=True)

    # Pregunta 2 (Fase 1)
    st.subheader("2. Distribución de especies: peces, mamíferos marinos y corales")
    if centro_sel is None:
        sector_sel = None
        st.caption("Selecciona un centro para filtrar también por sector.")
    else:
        df_s = pd.read_sql(text("SELECT num_sector, nombre FROM sectores_marinos WHERE codigo_centro=:c"), engine, params={"c": centro_sel})
        sector_sel = st.selectbox("Sector", [None] + df_s["num_sector"].tolist(),
                                  format_func=lambda x: "Todos los sectores" if x is None else df_s.loc[df_s["num_sector"]==x, "nombre"].values[0])
    df2 = pd.read_sql(text("""
        SELECT CASE
                 WHEN pz.codigo_especie IS NOT NULL THEN 'Pez'
                 WHEN mm.codigo_especie IS NOT NULL THEN 'Mamífero marino'
                 WHEN co.codigo_especie IS NOT NULL THEN 'Coral'
                 ELSE 'No clasificada'
               END AS clasificacion,
               COUNT(DISTINCT m.codigo_especie) AS especies
        FROM monitoreos m
        LEFT JOIN peces pz ON pz.codigo_especie = m.codigo_especie
        LEFT JOIN mamiferos_marinos mm ON mm.codigo_especie = m.codigo_especie
        LEFT JOIN corales co ON co.codigo_especie = m.codigo_especie
        WHERE (:c IS NULL OR m.codigo_centro = :c)
          AND (:s IS NULL OR m.num_sector = :s)
        GROUP BY clasificacion
    """), engine, params={"c": centro_sel, "s": sector_sel})
    st.plotly_chart(px.pie(df2, names="clasificacion", values="especies", hole=0.4), use_container_width=True)

    # Pregunta 3 (Fase 1)
    st.subheader("3. Cantidad de participantes vs. evaluación promedio")
    df3 = pd.read_sql(text("""
        SELECT a.id_actividad, a.tipo_actividad, c.nombre AS centro, s.nombre AS sector,
               (SELECT COUNT(*) FROM participacion_actividades p WHERE p.id_actividad = a.id_actividad) AS participantes,
               (SELECT ROUND(AVG(e.calificacion), 2) FROM evaluaciones e WHERE e.id_actividad = a.id_actividad) AS evaluacion_promedio
        FROM actividades a
        JOIN sectores_marinos s ON s.num_sector = a.num_sector AND s.codigo_centro = a.codigo_centro
        JOIN centros_conservacion c ON c.codigo_centro = a.codigo_centro
        WHERE a.activo = 1
          AND (:c IS NULL OR a.codigo_centro = :c)
          AND a.fecha_actividad BETWEEN :ini AND :fin
    """), engine, params=params).dropna(subset=["evaluacion_promedio"])
    if df3.empty:
        st.info("No hay actividades evaluadas con esos filtros.")
    else:
        st.plotly_chart(px.scatter(df3, x="participantes", y="evaluacion_promedio", color="tipo_actividad",
                                   hover_data=["centro", "sector"], range_y=[0, 5.2]), use_container_width=True)
        st.dataframe(df3, hide_index=True, use_container_width=True)

    # Pregunta 4 (propuesta del grupo)
    st.subheader("4. Ocupación de cupos y asistencia por tipo de actividad")
    df4 = pd.read_sql(text("""
        SELECT a.tipo_actividad,
               ROUND(100 * SUM(r.reservas) / SUM(a.capacidad_maxima), 1) AS ocupacion_pct,
               ROUND(100 * SUM(r.asistentes) / SUM(r.reservas), 1) AS asistencia_pct
        FROM actividades a
        JOIN (SELECT id_actividad, COUNT(*) AS reservas, SUM(asistio) AS asistentes
              FROM participacion_actividades GROUP BY id_actividad) r ON r.id_actividad = a.id_actividad
        WHERE a.activo = 1
          AND a.fecha_actividad <= CURDATE()   -- solo actividades ya realizadas
          AND (:c IS NULL OR a.codigo_centro = :c)
          AND a.fecha_actividad BETWEEN :ini AND :fin
        GROUP BY a.tipo_actividad
    """), engine, params=params)
    if df4.empty:
        st.info("No hay reservas con esos filtros.")
    else:
        st.plotly_chart(px.bar(df4, x="tipo_actividad", y=["ocupacion_pct", "asistencia_pct"], barmode="group",
                               labels={"value": "%", "tipo_actividad": "", "variable": ""}), use_container_width=True)
        st.caption("Ocupación = reservas / cupos disponibles. Asistencia = asistentes / reservas. Ayuda a decidir si ajustar la capacidad de cada tipo de actividad.")

# --- 3. FORMULARIO TRANSACCIONAL ---
elif modulo == "📝 Operaciones Transaccionales":
    st.title("📝 Operaciones Transaccionales")
    tab1, tab2 = st.tabs(["🎟️ Inscribir Visitante en Actividad", "🔬 Registrar Monitoreo Científico"])

    with tab1:
        df_vis = pd.read_sql(text("SELECT id_visitante, nombre_completo FROM visitantes ORDER BY id_visitante"), engine)
        df_act = pd.read_sql(text("""
            SELECT a.id_actividad, a.tipo_actividad, a.fecha_actividad, a.capacidad_maxima,
                   COUNT(p.id_visitante) AS inscritos
            FROM actividades a
            JOIN centros_conservacion c ON c.codigo_centro = a.codigo_centro
            LEFT JOIN participacion_actividades p ON a.id_actividad = p.id_actividad
            WHERE a.activo = 1 AND c.activo = 1
            GROUP BY a.id_actividad, a.tipo_actividad, a.fecha_actividad, a.capacidad_maxima
            ORDER BY a.fecha_actividad DESC
        """), engine)

        with st.form("form_inscripcion"):
            vis_sel = st.selectbox("Visitante", df_vis["id_visitante"], format_func=lambda x: f"{x} - {df_vis.loc[df_vis['id_visitante']==x, 'nombre_completo'].values[0]}")
            act_sel = st.selectbox("Actividad", df_act["id_actividad"], format_func=lambda x: f"ID {x}: {df_act.loc[df_act['id_actividad']==x, 'tipo_actividad'].values[0]} - {df_act.loc[df_act['id_actividad']==x, 'fecha_actividad'].values[0]} ({df_act.loc[df_act['id_actividad']==x, 'inscritos'].values[0]}/{df_act.loc[df_act['id_actividad']==x, 'capacidad_maxima'].values[0]} cupos)")
            fecha_res = st.date_input("Fecha de reserva", value=date.today())
            asistio_chk = st.checkbox("El visitante asistió (marcar solo si la actividad ya se realizó)", value=False)
            if st.form_submit_button("Registrar Participación"):
                fila_act = df_act[df_act["id_actividad"] == act_sel].iloc[0]
                ya_inscrito = pd.read_sql(text("""
                    SELECT COUNT(*) n FROM participacion_actividades WHERE id_visitante=:v AND id_actividad=:a
                """), engine, params={"v": int(vis_sel), "a": int(act_sel)})["n"][0]
                if ya_inscrito > 0:
                    st.error("Este visitante ya está inscrito en esta actividad.")
                elif fila_act["inscritos"] >= fila_act["capacidad_maxima"]:
                    st.error("Sin cupos disponibles para esta actividad.")
                elif fecha_res > pd.to_datetime(fila_act["fecha_actividad"]).date():
                    st.error("La fecha de reserva no puede ser posterior a la fecha de la actividad.")
                else:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO participacion_actividades (id_visitante, id_actividad, fecha_reserva, asistio)
                                VALUES (:v, :a, :f, :asist)
                            """), {"v": int(vis_sel), "a": int(act_sel), "f": fecha_res, "asist": 1 if asistio_chk else 0})
                        st.success("✅ Participación registrada y contabilizada en MySQL.")
                    except Exception as e:
                        st.error(f"No se pudo registrar: {e}")

    with tab2:
        df_sec = pd.read_sql(text("""
            SELECT s.codigo_centro, s.num_sector, c.nombre AS centro, s.nombre AS sector
            FROM sectores_marinos s
            JOIN centros_conservacion c ON s.codigo_centro = c.codigo_centro
            WHERE c.activo = 1
        """), engine)
        df_esp = pd.read_sql(text("SELECT codigo_especie, nombre_comun FROM especies WHERE activo=1"), engine)

        with st.form("form_monitoreo"):
            idx_sec = st.selectbox("Centro y Sector Marino", df_sec.index, format_func=lambda i: f"{df_sec.loc[i, 'centro']} - Sector {df_sec.loc[i, 'num_sector']} ({df_sec.loc[i, 'sector']})")
            esp_sel = st.selectbox("Especie Observada", df_esp["codigo_especie"], format_func=lambda x: df_esp.loc[df_esp["codigo_especie"]==x, "nombre_comun"].values[0])
            cant = st.number_input("Cantidad Observada", min_value=1, value=12)
            cond = st.text_input("Condiciones Ambientales", value="Oleaje moderado, visibilidad alta, 14.5°C")
            obs = st.text_area("Observaciones", value="Avistamiento registrado desde plataforma PMV.")
            if st.form_submit_button("Guardar Monitoreo"):
                if not cond.strip():
                    st.error("Las condiciones ambientales son obligatorias.")
                else:
                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO monitoreos (fecha, cantidad_observada, condiciones_ambientales, observaciones, codigo_centro, num_sector, codigo_especie)
                            VALUES (:f, :cant, :cond, :obs, :cc, :ns, :ce)
                        """), {
                            "f": date.today(), "cant": int(cant), "cond": cond, "obs": obs,
                            "cc": int(df_sec.loc[idx_sec, "codigo_centro"]),
                            "ns": int(df_sec.loc[idx_sec, "num_sector"]),
                            "ce": int(esp_sel)
                        })
                    st.success("✅ Monitoreo científico guardado exitosamente.")

# --- 4. GESTIÓN CRUD (CON CONTROL DE ROLES) ---
elif modulo == "⚙️ Gestión CRUD":
    st.title("⚙️ Gestión de Entidades Maestras (CRUD)")
    es_admin = "admin" in user["nombre_rol"].lower()
    if not es_admin:
        st.warning(f"Tu rol ({user['nombre_rol']}) solo tiene permisos de consulta. Inicia sesión como Administrador para crear o modificar.")

    entidad = st.selectbox("Seleccionar Tabla Maestra", ["Centros de Conservación", "Especies Marinas"])

    if entidad == "Centros de Conservación":
        estados_centro = get_enum_values("centros_conservacion", "estado_conservacion", ["Óptimo", "Estable", "En Riesgo", "Crítico"])
        df_centros = pd.read_sql(text("""
            SELECT codigo_centro, nombre, region_ubicacion, estado_conservacion, capacidad_operativa, presupuesto, activo
            FROM centros_conservacion ORDER BY codigo_centro DESC
        """), engine)
        st.dataframe(df_centros, use_container_width=True, hide_index=True)

        if es_admin:
            t_crear, t_editar = st.tabs(["➕ Crear Centro", "🔄 Actualizar / Desactivar Centro"])
            with t_crear:
                df_reg = pd.read_sql(text("SELECT codigo_region, nombre_oficial FROM regiones_maritimas"), engine)
                with st.form("crear_centro"):
                    nom = st.text_input("Nombre del Centro", value="Centro Marino Bahía Sur")
                    reg_id = st.selectbox("Región Marítima", df_reg["codigo_region"], format_func=lambda x: df_reg.loc[df_reg["codigo_region"]==x, "nombre_oficial"].values[0])
                    dir_c = st.text_input("Dirección", value="Costanera Norte Km 14")
                    mail_c = st.text_input("Correo Contacto", value="bahiasur@conservacion.cl")
                    sup_c = st.number_input("Superficie Protegida (ha)", min_value=10.0, value=1500.0)
                    pres_c = st.number_input("Presupuesto Anual", min_value=0.0, value=25000000.0)
                    cap_c = st.number_input("Capacidad Operativa", min_value=1, value=100)
                    est_c = st.selectbox("Estado Conservación", estados_centro)
                    if st.form_submit_button("Guardar Centro"):
                        reg_nom = df_reg.loc[df_reg["codigo_region"] == reg_id, "nombre_oficial"].values[0]
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO centros_conservacion
                                    (nombre, fecha_creacion, superficie_protegida, presupuesto, capacidad_operativa,
                                     estado_conservacion, region_ubicacion, correo_contacto, direccion, codigo_region, activo)
                                    VALUES (:n, :f, :s, :p, :cap, :est, :ru, :mail, :dir, :cr, 1)
                                """), {
                                    "n": nom, "f": date.today(), "s": sup_c, "p": pres_c, "cap": int(cap_c),
                                    "est": est_c, "ru": reg_nom, "mail": mail_c, "dir": dir_c, "cr": int(reg_id)
                                })
                            st.success("✅ Centro creado exitosamente.")
                        except Exception:
                            st.error("No se pudo crear: ya existe un centro con ese nombre o correo.")

            with t_editar:
                with st.form("editar_centro"):
                    c_id = st.selectbox("Código Centro", df_centros["codigo_centro"])
                    nuevo_est = st.selectbox("Nuevo Estado", estados_centro)
                    nuevo_act = st.radio("Estado Lógico", [1, 0], format_func=lambda x: "Activo (1)" if x == 1 else "Inactivo (0)")
                    if st.form_submit_button("Actualizar Centro"):
                        with engine.begin() as conn:
                            conn.execute(text("""
                                UPDATE centros_conservacion SET estado_conservacion=:e, activo=:a WHERE codigo_centro=:id
                            """), {"e": nuevo_est, "a": int(nuevo_act), "id": int(c_id)})
                        st.success("✅ Centro actualizado.")
                        st.rerun()

    else:
        estados_especie = get_enum_values("especies", "estado_conservacion", ["Preocupación Menor", "Vulnerable", "En Peligro", "En Peligro Crítico"])
        df_esp_all = pd.read_sql(text("""
            SELECT codigo_especie, nombre_cientifico, nombre_comun, estado_conservacion, fecha_incorporacion, activo
            FROM especies ORDER BY codigo_especie DESC
        """), engine)
        st.dataframe(df_esp_all, use_container_width=True, hide_index=True)

        if es_admin:
            t_ce, t_ee = st.tabs(["➕ Crear Especie", "🔄 Actualizar / Desactivar Especie"])
            with t_ce:
                with st.form("crear_especie"):
                    nc = st.text_input("Nombre Científico", value="Lontra felina")
                    ncom = st.text_input("Nombre Común", value="Chungungo")
                    este = st.selectbox("Estado Conservación", estados_especie)
                    if st.form_submit_button("Guardar Especie"):
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO especies (nombre_cientifico, nombre_comun, estado_conservacion, fecha_incorporacion, activo)
                                    VALUES (:nc, :ncom, :est, :f, 1)
                                """), {"nc": nc, "ncom": ncom, "est": este, "f": date.today()})
                            st.success("✅ Especie registrada.")
                        except Exception:
                            st.error("No se pudo crear: ya existe una especie con ese nombre científico.")
            with t_ee:
                with st.form("editar_especie"):
                    e_id = st.selectbox("Código Especie", df_esp_all["codigo_especie"])
                    est_e2 = st.selectbox("Nuevo Estado", estados_especie)
                    act_e2 = st.radio("Estado Lógico", [1, 0], format_func=lambda x: "Activo (1)" if x == 1 else "Inactivo (0)")
                    if st.form_submit_button("Actualizar Especie"):
                        with engine.begin() as conn:
                            conn.execute(text("""
                                UPDATE especies SET estado_conservacion=:e, activo=:a WHERE codigo_especie=:id
                            """), {"e": est_e2, "a": int(act_e2), "id": int(e_id)})
                        st.success("✅ Especie actualizada.")
                        st.rerun()