# Sistema Integral de Gestión de Centros de Conservación Marina

Proyecto semestral TDFI103 – Bases de Datos, Fase 2 (Caso 3) · Grupo 6

Base de datos en MySQL 8 y Producto Mínimo Viable (PMV) en Python/Streamlit, desplegado con Docker Compose.

## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| `script_integral_final.sql` | Script integral: crea la base, las tablas, las restricciones, los datos, las 6 vistas y los 6 procedimientos. |
| `generador_datos.py` | Generador de datos sintéticos con Faker (semilla fija, siempre genera los mismos datos). |
| `poblamiento.sql` | Insert masivo generado por `generador_datos.py`. |
| `app.py` | PMV en Streamlit: login con roles, formulario, CRUD y dashboard. |
| `Dockerfile` | Imagen de la aplicación (Python 3.12 + Streamlit). |
| `docker-compose.yml` | Servicios `db` (MySQL 8) y `web` (Streamlit). |
| `requirements.txt` | Librerías de Python. |
| `docs/Informe_Fase2.docx` | Informe del proyecto. |

## Cómo ejecutarlo

### Opción rápida: GitHub Codespaces

En el repositorio haz clic en **Code › Codespaces › Create codespace on main**. El Codespace levanta MySQL y el PMV con el mismo `docker-compose.yml` y abre la web en el puerto 8501 (la primera vez se demora unos minutos). Si no se abre sola, ve a la pestaña **Ports** y abre el puerto 8501.

### En tu computador

Requisito: tener Docker instalado (o abrir el repositorio en GitHub Codespaces).

```bash
docker compose up --build -d
```

Después abre http://localhost:8501 (en Codespaces: pestaña **Ports**, puerto 8501).

La primera vez, MySQL carga automáticamente `script_integral_final.sql`. Para borrar la base y crearla de nuevo:

```bash
docker compose down -v
docker compose up --build -d
```

### Usuarios de prueba

| Usuario | Contraseña | Rol | Permisos |
|---|---|---|---|
| `admin` | `1234` | Administrador | Formulario, CRUD completo y dashboard |
| `operador` | `1234` | Operador | Formulario y dashboard; en el CRUD solo puede consultar |

## Probar las vistas y procedimientos

### Desde el navegador (Adminer)

Abre el puerto **8080** (en Codespaces: pestaña **Ports**) e ingresa con: Sistema **MySQL**, Servidor **db**, Usuario **root**, Contraseña **root**, Base de datos **conservacion_marina_db**. Luego entra a **Comando SQL** y ejecuta las consultas.

### Desde la terminal

Con los contenedores levantados:

```bash
docker exec -it mysql_conservacion mysql -uroot -proot conservacion_marina_db
```

Ejemplos:

```sql
SELECT * FROM v_r5_tasa_asistencia_sector ORDER BY tasa_asistencia_pct DESC;
CALL sp_r9_actividades_sobre_promedio(14, '2025-11-01', '2026-11-30');
```

## Regenerar los datos

```bash
pip install faker
python generador_datos.py   # genera poblamiento.sql
```
