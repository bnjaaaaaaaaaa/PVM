"""
Generador de datos sintéticos - Proyecto TDFI103 Fase 2
Caso 3: Sistema Integral de Gestión de Centros de Conservación Marina

Genera el archivo poblamiento.sql con INSERT masivos para la base
conservacion_marina_db. Usa una semilla fija, así que siempre produce
los mismos datos (poblamiento reproducible).

Uso:  python generador_datos.py
Requisitos: pip install faker
"""
import random
from datetime import date, timedelta
from faker import Faker

SEMILLA = 2026
random.seed(SEMILLA)
fake = Faker('es_CL')
fake.seed_instance(SEMILLA)

FECHA_BASE = date(2026, 11, 15)   # "hoy" para el poblamiento (fecha fija = reproducible)

# Volúmenes (rangos de la pauta entre paréntesis)
NUM_TRABAJADORES = 50     # 40 a 80
NUM_MONITOREOS = 350      # 250 a 500
NUM_ACTIVIDADES = 160     # 120 a 250
NUM_ACT_FUTURAS = 10      # actividades próximas, para probar el formulario del PMV
NUM_VISITANTES = 200      # 150 a 300
NUM_PARTICIPACIONES = 1000  # 800 a 1500
PROB_EVALUAR = 0.68       # probabilidad de que un asistente evalúe la actividad


def esc(texto):
    """Escapa comillas simples para SQL."""
    return str(texto).replace("'", "''")


def val(v):
    if v is None:
        return 'NULL'
    if isinstance(v, (int, float)):
        return str(v)
    return f"'{esc(v)}'"


def insert_masivo(tabla, columnas, filas, lote=100):
    """Devuelve sentencias INSERT de varias filas (insert masivo)."""
    out = []
    for i in range(0, len(filas), lote):
        valores = ',\n'.join('(' + ', '.join(val(x) for x in f) + ')' for f in filas[i:i + lote])
        out.append(f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES\n{valores};")
    return '\n'.join(out)


def fecha_entre(ini, fin):
    return ini + timedelta(days=random.randint(0, (fin - ini).days))


sql = ["-- ==========================================================",
       "-- POBLAMIENTO - CENTROS DE CONSERVACIÓN MARINA (generado con generador_datos.py)",
       f"-- Semilla: {SEMILLA} | Fecha base: {FECHA_BASE}",
       "-- ==========================================================",
       "SET NAMES utf8mb4;",
       "USE conservacion_marina_db;", ""]

# ---------------------------------------------------------------- 1. REGIONES MARÍTIMAS
regiones = [  # nombre, nivel de protección, superficie protegida (km2), presupuesto anual
    ("Región Marítima de Arica y Parinacota", "Reserva Marina", 18450.50, 210000000),
    ("Región Marítima de Antofagasta", "Reserva Marina", 32780.20, 340000000),
    ("Región Marítima de Atacama", "Parque Marino", 41250.75, 395000000),
    ("Región Marítima de Coquimbo", "Reserva Marina", 28900.00, 380000000),
    ("Región Marítima de Valparaíso", "Parque Marino", 742500.30, 1450000000),
    ("Región Marítima del Biobío", "Área Marina Costera Protegida", 15320.40, 260000000),
    ("Región Marítima de Los Lagos", "Área Marina Costera Protegida", 64800.90, 610000000),
    ("Región Marítima de Magallanes", "Parque Marino", 136900.60, 890000000),
]
sql.append("-- 1. REGIONES MARÍTIMAS")
sql.append(insert_masivo("regiones_maritimas",
                         ["codigo_region", "nombre_oficial", "nivel_proteccion", "superficie_protegida", "presupuesto_anual"],
                         [(i + 1, *r) for i, r in enumerate(regiones)]))

# ---------------------------------------------------------------- 2. CENTROS DE CONSERVACIÓN
# nombre, código región, nombre región, zona ecológica, dirección
centros = [
    ("Centro Marino La Lisera", 1, "Arica y Parinacota", "N", "Av. Comandante San Martín 3200, Arica"),
    ("Centro Marino Punta Coloso", 2, "Antofagasta", "N", "Ruta 1 km 14, Antofagasta"),
    ("Centro Marino Isla Santa María", 2, "Antofagasta", "N", "Caleta Constitución s/n, Mejillones"),
    ("Centro Marino Pan de Azúcar", 3, "Atacama", "N", "Caleta Pan de Azúcar s/n, Chañaral"),
    ("Centro Marino Isla Chañaral", 3, "Atacama", "N", "Caleta Chañaral de Aceituno s/n, Freirina"),
    ("Centro Marino Punta de Choros", 4, "Coquimbo", "C", "Caleta Punta de Choros s/n, La Higuera"),
    ("Centro Marino Tongoy", 4, "Coquimbo", "C", "Costanera de Tongoy 450, Coquimbo"),
    ("Centro Marino Las Cruces", 5, "Valparaíso", "C", "Osvaldo Marín 1, Las Cruces"),
    ("Centro Marino Juan Fernández", 5, "Valparaíso", "JF", "Larraín Alcalde 320, San Juan Bautista"),
    ("Centro Marino Rapa Nui", 5, "Valparaíso", "RN", "Caleta Hanga Roa s/n, Isla de Pascua"),
    ("Centro Marino Isla Mocha", 6, "Biobío", "S", "Sector La Hacienda s/n, Isla Mocha"),
    ("Centro Marino Lafken Mapu Lahual", 7, "Los Lagos", "S", "Caleta Condor s/n, Río Negro"),
    ("Centro Marino Chiloé", 7, "Los Lagos", "S", "Costanera Pedro Montt 210, Ancud"),
    ("Centro Marino Francisco Coloane", 8, "Magallanes", "A", "Isla Carlos III s/n, Punta Arenas"),
    ("Centro Marino Seno Almirantazgo", 8, "Magallanes", "A", "Bahía Ainsworth s/n, Porvenir"),
]
estados_centro = ["Óptimo", "Estable", "Estable", "En Riesgo", "Crítico"]
filas = []
for i, (nom, reg, reg_nom, zona, dirc) in enumerate(centros, start=1):
    slug = nom.lower().replace("centro marino ", "").replace(" ", "").replace("á", "a").replace("é", "e") \
        .replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    filas.append((i, nom, str(fecha_entre(date(2005, 1, 1), date(2020, 12, 31))),
                  round(random.uniform(850, 24500), 2), round(random.uniform(90e6, 420e6), 2),
                  random.randint(40, 260), random.choice(estados_centro), f"Región de {reg_nom}",
                  f"contacto.{slug}@conservacionmarina.cl", dirc, reg, 1))
sql.append("\n-- 2. CENTROS DE CONSERVACIÓN")
sql.append(insert_masivo("centros_conservacion",
                         ["codigo_centro", "nombre", "fecha_creacion", "superficie_protegida", "presupuesto",
                          "capacidad_operativa", "estado_conservacion", "region_ubicacion", "correo_contacto",
                          "direccion", "codigo_region", "activo"], filas))
ZONA_CENTRO = {i: c[3] for i, c in enumerate(centros, start=1)}

# ---------------------------------------------------------------- 3. SECTORES MARINOS (3 por centro)
tipos_sector = ["Arrecife", "Bahía", "Caleta", "Islote", "Pradera de Algas", "Canal", "Punta", "Fondo Rocoso"]
lugares = ["Los Lobos", "El Faro", "Los Pelícanos", "Las Gaviotas", "Piedra Blanca", "Los Choros", "El Sauce",
           "Punta Negra", "La Ballena", "Las Tortugas", "El Muelle", "Los Huiros", "La Herradura", "Las Conchas",
           "Los Cormoranes", "El Morro", "La Puntilla", "Los Pingüinos", "El Sargazo", "Los Corales"]
temp_zona = {"N": (15, 21), "C": (12, 17), "JF": (14, 19), "RN": (20, 26), "S": (9, 14), "A": (5, 10)}
filas, SECTORES = [], []
for cc in range(1, len(centros) + 1):
    usados = set()
    for ns in range(1, 4):
        while True:
            nombre = f"{random.choice(tipos_sector)} {random.choice(lugares)}"
            if nombre not in usados:
                usados.add(nombre)
                break
        t0, t1 = temp_zona[ZONA_CENTRO[cc]]
        acceso = random.choices(["Público", "Restringido", "Solo Investigación"], [5, 3, 2])[0]
        filas.append((ns, cc, nombre, round(random.uniform(120, 4800), 2), round(random.uniform(4, 180), 2),
                      round(random.uniform(t0, t1), 1), acceso, random.randint(35, 98)))
        SECTORES.append((cc, ns, acceso))
sql.append("\n-- 3. SECTORES MARINOS")
sql.append(insert_masivo("sectores_marinos",
                         ["num_sector", "codigo_centro", "nombre", "extension", "profundidad_promedio", "temperatura",
                          "nivel_acceso", "biodiversidad_estimada"], filas))

# ---------------------------------------------------------------- 4. ESPECIES (+ subtipos ISA)
# nombre común, nombre científico, estado de conservación, zonas donde se observa
TODAS = "N C S A JF"
peces = [
    ("Jurel", "Trachurus murphyi", "Vulnerable", "N C S JF"),
    ("Anchoveta", "Engraulis ringens", "Preocupación Menor", "N C"),
    ("Sardina común", "Strangomera bentincki", "Preocupación Menor", "C S"),
    ("Merluza común", "Merluccius gayi", "Vulnerable", "C S"),
    ("Merluza austral", "Merluccius australis", "Vulnerable", "S A"),
    ("Congrio dorado", "Genypterus blacodes", "Preocupación Menor", "S A"),
    ("Congrio colorado", "Genypterus chilensis", "Preocupación Menor", "N C S"),
    ("Reineta", "Brama australis", "Preocupación Menor", "C S"),
    ("Corvina", "Cilus gilberti", "Preocupación Menor", "N C"),
    ("Lenguado de ojos grandes", "Hippoglossina macrops", "Preocupación Menor", "N C"),
    ("Bacalao de profundidad", "Dissostichus eleginoides", "En Peligro", "S A"),
    ("Pez espada", "Xiphias gladius", "Preocupación Menor", "N C JF"),
    ("Sierra", "Thyrsites atun", "Preocupación Menor", "C S"),
    ("Cabrilla común", "Paralabrax humeralis", "Preocupación Menor", "N C"),
    ("Pejerrey de mar", "Odontesthes regia", "Preocupación Menor", "N C S"),
    ("Rollizo", "Pinguipes chilensis", "Preocupación Menor", "N C S"),
    ("Vieja negra", "Graus nigra", "Vulnerable", "N C"),
    ("Bilagay", "Cheilodactylus variegatus", "Preocupación Menor", "N C"),
    ("Jerguilla", "Aplodactylus punctatus", "Preocupación Menor", "N C"),
    ("Tollo", "Mustelus mento", "Vulnerable", "C S"),
    ("Tiburón azulejo", "Prionace glauca", "En Peligro", "N C JF"),
    ("Tiburón marrajo", "Isurus oxyrinchus", "En Peligro", "N C JF"),
    ("Pez luna", "Mola mola", "Vulnerable", "C S JF"),
    ("Breca de Juan Fernández", "Nemadactylus gayi", "Vulnerable", "JF"),
    ("Pez mariposa de Pascua", "Chaetodon litus", "Preocupación Menor", "RN"),
]
mamiferos = [
    ("Lobo marino común", "Otaria flavescens", "Preocupación Menor", "N C S A"),
    ("Lobo fino austral", "Arctocephalus australis", "Preocupación Menor", "S A"),
    ("Lobo fino de Juan Fernández", "Arctocephalus philippii", "Vulnerable", "JF"),
    ("Elefante marino del sur", "Mirounga leonina", "Preocupación Menor", "A"),
    ("Foca leopardo", "Hydrurga leptonyx", "Preocupación Menor", "A"),
    ("Chungungo", "Lontra felina", "En Peligro", "N C S"),
    ("Huillín", "Lontra provocax", "En Peligro", "S A"),
    ("Ballena azul", "Balaenoptera musculus", "En Peligro", "S"),
    ("Ballena fin", "Balaenoptera physalus", "Vulnerable", "N C S"),
    ("Ballena sei", "Balaenoptera borealis", "En Peligro", "S A"),
    ("Ballena jorobada", "Megaptera novaeangliae", "Preocupación Menor", "N C S A"),
    ("Ballena franca austral", "Eubalaena australis", "En Peligro Crítico", "S"),
    ("Ballena minke antártica", "Balaenoptera bonaerensis", "Preocupación Menor", "A"),
    ("Ballena de Bryde", "Balaenoptera edeni", "Preocupación Menor", "N C"),
    ("Cachalote", "Physeter macrocephalus", "Vulnerable", "N C JF"),
    ("Orca", "Orcinus orca", "Preocupación Menor", "S A"),
    ("Delfín chileno", "Cephalorhynchus eutropia", "En Peligro", "C S"),
    ("Delfín austral", "Lagenorhynchus australis", "Preocupación Menor", "S A"),
    ("Delfín oscuro", "Lagenorhynchus obscurus", "Preocupación Menor", "N C"),
    ("Delfín nariz de botella", "Tursiops truncatus", "Preocupación Menor", "N C"),
    ("Delfín común", "Delphinus delphis", "Preocupación Menor", "N C"),
    ("Marsopa espinosa", "Phocoena spinipinnis", "Vulnerable", "C S"),
    ("Calderón negro", "Globicephala melas", "Preocupación Menor", "S A"),
    ("Delfín de Risso", "Grampus griseus", "Preocupación Menor", "N C"),
    ("Tonina overa", "Cephalorhynchus commersonii", "Preocupación Menor", "A"),
]
corales = [
    ("Coral copa de fiordo", "Desmophyllum dianthus", "Vulnerable", "S A"),
    ("Coral de aguas frías", "Desmophyllum pertusum", "Vulnerable", "S A"),
    ("Coral copa de Huinay", "Caryophyllia huinayensis", "Vulnerable", "S"),
    ("Coral solitario de fiordo", "Tethocyathus endesa", "En Peligro", "S A"),
    ("Coral abanico solitario", "Flabellum thouarsii", "Preocupación Menor", "A"),
    ("Coral de ojos", "Madrepora oculata", "Vulnerable", "S A"),
    ("Coral coliflor", "Pocillopora verrucosa", "Vulnerable", "RN"),
    ("Coral lobulado", "Porites lobata", "Vulnerable", "RN"),
    ("Coral de surcos", "Pavona varians", "Preocupación Menor", "RN"),
    ("Coral incrustante", "Montipora aequituberculata", "Vulnerable", "RN"),
    ("Coral estrella púrpura", "Leptastrea purpurea", "Preocupación Menor", "RN"),
    ("Coral arena estrellado", "Psammocora stellata", "En Peligro", "RN"),
    ("Coral hongo", "Cycloseris vaughani", "Preocupación Menor", "RN"),
    ("Coral negro", "Antipathes speciosa", "En Peligro", "JF RN"),
    ("Coral negro de profundidad", "Bathypathes patula", "Vulnerable", "JF"),
    ("Hidrocoral rojo", "Errina antarctica", "Vulnerable", "A"),
    ("Gorgonia chilena", "Primnoella chilensis", "Preocupación Menor", "S A"),
    ("Gorgonia de fiordo", "Thouarella variabilis", "Vulnerable", "S A"),
    ("Coral chicle", "Paragorgia arborea", "Vulnerable", "A"),
    ("Coral copa anaranjado", "Javania cailleti", "Preocupación Menor", "C S"),
]
no_clasificadas = [  # invertebrados: no pertenecen a ningún subtipo del modelo
    ("Loco", "Concholepas concholepas", "Vulnerable", "N C S"),
    ("Erizo rojo", "Loxechinus albus", "Vulnerable", "C S A"),
    ("Centolla", "Lithodes santolla", "Vulnerable", "A"),
    ("Pulpo del norte", "Octopus mimus", "Preocupación Menor", "N C"),
    ("Calamar de Humboldt", "Dosidicus gigas", "Preocupación Menor", "N C S"),
    ("Choro zapato", "Choromytilus chorus", "Vulnerable", "C S"),
    ("Picoroco", "Austromegabalanus psittacus", "Preocupación Menor", "N C S"),
    ("Estrella de mar sol", "Heliaster helianthus", "Preocupación Menor", "N C"),
    ("Jaiba mora", "Homalaspis plana", "Preocupación Menor", "N C S"),
    ("Langosta de Juan Fernández", "Jasus frontalis", "Vulnerable", "JF"),
]
ESPECIES = []   # (codigo, grupo, zonas)
f_esp, f_pez, f_mam, f_cor, f_dist = [], [], [], [], []
zonas_txt = {"N": "Norte de Chile (Corriente de Humboldt)", "C": "Costa central de Chile", "S": "Sur de Chile y mar interior de Chiloé",
             "A": "Fiordos y canales patagónicos", "JF": "Archipiélago Juan Fernández", "RN": "Isla de Pascua (Rapa Nui)"}
codigo = 0
for grupo, lista in [("pez", peces), ("mamifero", mamiferos), ("coral", corales), ("otro", no_clasificadas)]:
    for com, cien, estado, zonas in lista:
        codigo += 1
        z = zonas.split()
        ESPECIES.append((codigo, grupo, z))
        f_esp.append((codigo, cien, com, estado, str(fecha_entre(date(2012, 1, 1), date(2024, 12, 31))), 1))
        for zz in z[:2]:
            f_dist.append((codigo, zonas_txt[zz]))
        if grupo == "pez":
            f_pez.append((codigo, random.choice(["Cicloidea", "Ctenoidea", "Placoidea", "Sin escamas"]),
                          random.choice(["Homocerca", "Heterocerca", "Dorsal espinosa", "Pectoral alargada"])))
        elif grupo == "mamifero":
            f_mam.append((codigo, random.randint(9, 16),
                          "Pulmonar con espiráculo" if ("Ballena" in com or "Delfín" in com or com in ("Cachalote", "Orca", "Marsopa espinosa", "Calderón negro", "Tonina overa"))
                          else "Pulmonar con apnea prolongada"))
        elif grupo == "coral":
            f_cor.append((codigo, random.choice(["Ramificada", "Masiva", "Incrustante", "Solitaria", "Abanico"]),
                          round(random.uniform(0.5, 25.0), 2)))
sql.append("\n-- 4. ESPECIES, DISTRIBUCIÓN GEOGRÁFICA Y SUBTIPOS")
sql.append(insert_masivo("especies", ["codigo_especie", "nombre_cientifico", "nombre_comun", "estado_conservacion",
                                      "fecha_incorporacion", "activo"], f_esp))
sql.append(insert_masivo("distribuciones_especie", ["codigo_especie", "zona_geografica"], f_dist))
sql.append(insert_masivo("peces", ["codigo_especie", "tipo_escama", "tipo_aleta"], f_pez))
sql.append(insert_masivo("mamiferos_marinos", ["codigo_especie", "periodo_gestacion", "mecanismo_respiratorio"], f_mam))
sql.append(insert_masivo("corales", ["codigo_especie", "tipo_estructura", "tasa_crecimiento"], f_cor))

# ---------------------------------------------------------------- 5. MONITOREOS
condiciones = ["Mar calmo, visibilidad alta", "Oleaje moderado, visibilidad media", "Marejada, visibilidad baja",
               "Viento sur fuerte, corriente intensa", "Neblina costera, mar calmo", "Marea baja, agua clara"]
rango_cant = {"pez": (10, 320), "mamifero": (1, 45), "coral": (2, 80), "otro": (5, 220)}
filas = []
for i in range(1, NUM_MONITOREOS + 1):
    cc, ns, _ = random.choice(SECTORES)
    zona = ZONA_CENTRO[cc]
    candidatas = [e for e in ESPECIES if zona in e[2]]
    cod, grupo, _ = random.choice(candidatas)
    lo, hi = rango_cant[grupo]
    obs = random.choice(["Registro en transecto de buceo.", "Avistamiento desde embarcación.",
                         "Conteo desde punto fijo en la costa.", None, "Individuos juveniles presentes."])
    filas.append((i, str(fecha_entre(date(2024, 11, 15), FECHA_BASE)), random.randint(lo, hi),
                  random.choice(condiciones), obs, cc, ns, cod))
sql.append("\n-- 5. MONITOREOS DE ESPECIES")
sql.append(insert_masivo("monitoreos", ["id_monitoreo", "fecha", "cantidad_observada", "condiciones_ambientales",
                                        "observaciones", "codigo_centro", "num_sector", "codigo_especie"], filas))

# ---------------------------------------------------------------- 6. TRABAJADORES Y ESPECIALIZACIONES
def rut_chileno(n):
    cuerpo = random.randint(8_000_000, 24_999_999) + n
    s, m = 0, 2
    for d in reversed(str(cuerpo)):
        s += int(d) * m
        m = 2 if m == 7 else m + 1
    dv = 11 - s % 11
    dv = "0" if dv == 11 else "K" if dv == 10 else str(dv)
    return f"{cuerpo:,}".replace(",", ".") + f"-{dv}"

f_trab, f_adm, f_gua, f_con, f_inv = [], [], [], [], []
for i in range(1, NUM_TRABAJADORES + 1):
    f_trab.append((i, rut_chileno(i), fake.name()))
    tipo = i % 4
    if tipo == 1:
        f_adm.append((i, random.choice(["Dirección del centro", "Finanzas y presupuesto", "Recursos humanos",
                                         "Atención de visitantes", "Logística marítima"])))
    elif tipo == 2:
        cc = random.randint(1, len(centros))
        f_gua.append((i, f"Sectores de {centros[cc - 1][0].replace('Centro Marino ', '')}",
                      random.choice(["Mañana", "Tarde", "Noche"])))
    elif tipo == 3:
        f_con.append((i, random.choice(["Mamíferos marinos", "Arrecifes de coral", "Peces costeros", "Bosques de algas"]),
                      random.choice(["Recuperación del chungungo", "Monitoreo de ballena azul", "Restauración de huirales",
                                     "Protección de corales de fiordo", "Plan de manejo del loco"])))
    else:
        f_inv.append((i, random.choice(["Biólogo Marino", "Magíster en Ciencias del Mar", "Doctorado en Oceanografía",
                                        "Doctorado en Ecología"]),
                      random.choice(["Efectos del cambio climático", "Dinámica poblacional", "Acidificación del océano",
                                     "Biodiversidad de profundidad", "Ecología de cetáceos"])))
sql.append("\n-- 6. TRABAJADORES Y ESPECIALIZACIONES")
sql.append(insert_masivo("trabajadores", ["id_trabajador", "rut", "nombre"], f_trab))
sql.append(insert_masivo("administrativos", ["id_trabajador", "area_asignada"], f_adm))
sql.append(insert_masivo("guardaparques", ["id_trabajador", "zona_patrullaje", "turno_asignado"], f_gua))
sql.append(insert_masivo("conservacionistas", ["id_trabajador", "especialidad_conservacion", "proyecto_asignado"], f_con))
sql.append(insert_masivo("investigadores", ["id_trabajador", "grado_academico", "linea_investigacion"], f_inv))

# ---------------------------------------------------------------- 7. ROLES Y USUARIOS (1 cuenta por trabajador)
sql.append("\n-- 7. ROLES Y USUARIOS")
sql.append(insert_masivo("roles", ["id_rol", "nombre_rol", "descripcion_permisos"], [
    (1, "Administrador", "Acceso total: formulario, CRUD de tablas maestras y dashboard."),
    (2, "Operador", "Registra participaciones y monitoreos, consulta el CRUD y el dashboard."),
]))
f_usr, f_ur = [], []
for i in range(1, NUM_TRABAJADORES + 1):
    if i == 1:
        user, rol = "admin", 1
    elif i == 2:
        user, rol = "operador", 2
    else:
        user = f"user_{i}"
        rol = 1 if i % 5 == 0 else 2
    estado = "Suspendida" if i in (13, 27, 41) else "Activa"
    f_usr.append((i, user, "1234", estado, i, 1))
    f_ur.append((i, rol))
sql.append(insert_masivo("usuarios", ["id_usuario", "username", "password", "estado_cuenta", "id_trabajador", "activo"], f_usr))
sql.append(insert_masivo("usuarios_roles", ["id_usuario", "id_rol"], f_ur))

# ---------------------------------------------------------------- 8. VISITANTES
f_vis, correos = [], set()
dominios = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "uc.cl", "inacap.cl"]
for i in range(1, NUM_VISITANTES + 1):
    nombre = fake.name()
    base = (nombre.split()[0][0] + nombre.split()[-1]).lower()
    for a, b in zip("áéíóúñü", "aeiounu"):
        base = base.replace(a, b)
    correo = f"{base}{random.randint(1, 999)}@{random.choice(dominios)}"
    while correo in correos:
        correo = f"{base}{random.randint(1, 9999)}@{random.choice(dominios)}"
    correos.add(correo)
    f_vis.append((i, nombre, correo))
sql.append("\n-- 8. VISITANTES")
sql.append(insert_masivo("visitantes", ["id_visitante", "nombre_completo", "correo_contacto"], f_vis))

# ---------------------------------------------------------------- 9. ACTIVIDADES (solo en sectores con acceso público o restringido)
tipos_act = ["Recorrido Guiado", "Taller Educativo", "Observación Marina", "Limpieza Costera"]
sect_visitables = [s for s in SECTORES if s[2] != "Solo Investigación"]
popularidad_centro = {cc: random.uniform(0.5, 1.6) for cc in range(1, len(centros) + 1)}
asistencia_sector = {(s[0], s[1]): random.uniform(0.55, 0.97) for s in SECTORES}
ACTIVIDADES = []  # (id, fecha, capacidad, centro, sector, tipo)
filas = []
for i in range(1, NUM_ACTIVIDADES + 1):
    cc, ns, _ = random.choices(sect_visitables, [popularidad_centro[s[0]] for s in sect_visitables])[0]
    if i <= NUM_ACTIVIDADES - NUM_ACT_FUTURAS:
        f = fecha_entre(date(2025, 11, 15), FECHA_BASE - timedelta(days=3))
    else:
        f = fecha_entre(FECHA_BASE + timedelta(days=5), FECHA_BASE + timedelta(days=45))
    tipo = random.choice(tipos_act)
    cap = random.choice([10, 12, 15, 15, 20, 20, 25, 30, 35, 40])
    ACTIVIDADES.append((i, f, cap, cc, ns, tipo))
    filas.append((i, tipo, str(f), cap, cc, ns, 1))
sql.append("\n-- 9. ACTIVIDADES")
sql.append(insert_masivo("actividades", ["id_actividad", "tipo_actividad", "fecha_actividad", "capacidad_maxima",
                                         "codigo_centro", "num_sector", "activo"], filas))

# ---------------------------------------------------------------- 10. PARTICIPACIONES (respetan cupo y fechas)
peso_act = {a[0]: popularidad_centro[a[3]] * random.uniform(0.4, 1.6) * (0.35 if a[1] > FECHA_BASE else 1) for a in ACTIVIDADES}
peso_vis = {v[0]: random.choice([0.4, 1, 1, 1, 2, 3.5]) for v in f_vis}
inscritos = {a[0]: 0 for a in ACTIVIDADES}
pares = set()
PART = []
ids_act, w_act = list(peso_act), list(peso_act.values())
ids_vis, w_vis = list(peso_vis), list(peso_vis.values())
while len(PART) < NUM_PARTICIPACIONES:
    ia = random.choices(ids_act, w_act)[0]
    iv = random.choices(ids_vis, w_vis)[0]
    act = ACTIVIDADES[ia - 1]
    if (iv, ia) in pares or inscritos[ia] >= act[2]:
        continue
    pares.add((iv, ia))
    inscritos[ia] += 1
    f_act = act[1]
    f_res = max(date(2025, 10, 1), f_act - timedelta(days=random.randint(1, 40)))
    f_res = min(f_res, FECHA_BASE)
    if f_act > FECHA_BASE:
        asistio = 0                               # la actividad aún no se realiza
    else:
        asistio = 1 if random.random() < asistencia_sector[(act[3], act[4])] else 0
    PART.append((iv, ia, str(f_res), asistio))
sql.append("\n-- 10. PARTICIPACIÓN / RESERVAS")
sql.append(insert_masivo("participacion_actividades", ["id_visitante", "id_actividad", "fecha_reserva", "asistio"], PART))

# ---------------------------------------------------------------- 11. EVALUACIONES (solo de quienes asistieron)
comentarios = {
    5: ["Excelente experiencia, los guías explicaron todo muy bien.", "Vimos muchas especies, totalmente recomendable.", None],
    4: ["Muy buena actividad, aprendimos bastante.", "Buena organización, aunque empezó un poco tarde.", None],
    3: ["Estuvo bien, pero el grupo era muy grande.", "Regular, el clima no ayudó mucho.", None],
    2: ["Faltó información sobre las especies.", "Poca organización al inicio.", None],
    1: ["No se realizó el recorrido completo.", "Mala experiencia, muy desordenado.", None],
}
calidad_act = {a[0]: random.uniform(-0.9, 0.9) for a in ACTIVIDADES}
correlativo = {a[0]: 0 for a in ACTIVIDADES}
f_eval = []
for iv, ia, f_res, asistio in PART:
    act = ACTIVIDADES[ia - 1]
    if not asistio or random.random() > PROB_EVALUAR:
        continue
    nota = round(3.8 + calidad_act[ia] + random.gauss(0, 0.9))
    nota = max(1, min(5, nota))
    correlativo[ia] += 1
    f_ev = min(act[1] + timedelta(days=random.randint(0, 10)), FECHA_BASE)
    f_eval.append((correlativo[ia], ia, iv, nota, str(f_ev), random.choice(comentarios[nota])))
sql.append("\n-- 11. EVALUACIONES")
sql.append(insert_masivo("evaluaciones", ["correlativo", "id_actividad", "id_visitante", "calificacion", "fecha", "comentario"], f_eval))

with open("poblamiento.sql", "w", encoding="utf-8") as f:
    f.write("\n".join(sql) + "\n")

print("Archivo poblamiento.sql generado:")
for nombre, n in [("regiones", len(regiones)), ("centros", len(centros)), ("sectores", len(SECTORES)),
                  ("especies", len(f_esp)), ("monitoreos", NUM_MONITOREOS), ("trabajadores", NUM_TRABAJADORES),
                  ("actividades", NUM_ACTIVIDADES), ("visitantes", NUM_VISITANTES),
                  ("participaciones", len(PART)), ("evaluaciones", len(f_eval)), ("usuarios", len(f_usr))]:
    print(f"  {nombre:16s} {n}")
