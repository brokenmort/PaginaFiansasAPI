# Finansas API – Documentación de Uso

API para finanzas personales (Django + DRF + JWT). Permite gestionar ingresos/egresos (fijos y extra), ahorros con movimientos, préstamos y reportes. La documentación Swagger está disponible en `/docs`.

## Producción (Heroku)

- Base URL: `https://pagina-web-finansas-b6474cfcee14.herokuapp.com`
- Docs (Swagger): `https://pagina-web-finansas-b6474cfcee14.herokuapp.com/docs/`
- JSON/YAML: `/swagger.json`, `/swagger.yaml`

Insomnia (usar entorno Heroku):
- Importa `web/docs/insomnia_finansas.json` → selecciona entorno `Heroku`.
- Haz Login (`Auth → Login`), copia `access` al entorno y prueba endpoints.
- Para ahorros, crea uno y usa su `id` en la variable `ahorroId` del entorno.

## Ejecución local

- Requisitos: Python 3.11+, pip, virtualenv recomendado.
- Crear entorno y dependencias:
  - `python -m venv .venv`
  - En Windows PowerShell: `.\.venv\Scripts\Activate`
  - `pip install -r web/requirements.txt`
- Migraciones y superusuario:
  - `python web/manage.py migrate`
  - `python web/manage.py createsuperuser`
- Ejecutar servidor:
  - `python web/manage.py runserver`
- Documentación: `http://localhost:8000/docs/`

## Variables de entorno

- `DJANGO_SECRET_KEY`: cadena aleatoria segura (obligatoria en producción)
- `DJANGO_DEBUG`: `False` en producción
- `DATABASE_URL`: Postgres en producción (Heroku la define)
- Email (opcional para reset password): `EMAIL_USER`, `EMAIL_PASS`

## Despliegue en Heroku (resumen)

- Buildpacks: Python
- Ficheros clave: `Procfile`, `.python-version`, `web/requirements.txt`
- Config vars: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False` (+ email si aplica)
- Base de datos: `heroku-postgresql:essential-0` o superior
- Release phase migra la BD: `release: python manage.py migrate`

## Estructura principal

- `web/` proyecto Django (raíz del repo)
  - `users/`, `ingresos/`, `egresos/`, `ahorros/`, `prestamos/`, `reports/`
  - `web/web/urls.py` rutas, Swagger y routers
  - `web/web/settings.py` configuración (DB, CORS, Swagger, JWT)
  - `docs/insomnia_finansas.json` colección Insomnia

## Notas

- Seguridad: todos los recursos de negocio requieren JWT; solo ves tus propios datos (campo `owner`).
- Archivos estáticos/medios: para producción se recomienda S3/Cloudinary para `MEDIA` (Heroku FS es efímero).

## Autenticación

- Login: `POST /api/auth/login/`  -> `{ "email": "...", "password": "..." }`
- Refresh: `POST /api/auth/token/refresh/` -> `{ "refresh": "..." }`
- Usuario actual: `GET /api/auth/me/`
- Logout: `POST /api/auth/logout/`
- Header para el resto de rutas: `Authorization: Bearer <access>`

## Endpoints Principales

- Ingresos Fijos: `GET/POST /api/IngresosFijos/`, `GET/PUT/PATCH/DELETE /api/IngresosFijos/{id}/`
- Ingresos Extra: `GET/POST /api/IngresosExtra/`, `GET/PUT/PATCH/DELETE /api/IngresosExtra/{id}/`
- Egresos Fijos: `GET/POST /api/EgresosFijos/`, `GET/PUT/PATCH/DELETE /api/EgresosFijos/{id}/`
- Egresos Extra: `GET/POST /api/EgresosExtra/`, `GET/PUT/PATCH/DELETE /api/EgresosExtra/{id}/`
- Ahorros: `GET/POST /api/ahorros/`, `GET/PUT/PATCH/DELETE /api/ahorros/{id}/`
  - Movimientos: `GET/POST /api/ahorros/{id}/movimientos/`
  - Depositar: `POST /api/ahorros/{id}/depositar/` ({ amount, note })
  - Retirar: `POST /api/ahorros/{id}/retirar/` ({ amount, note })
- Préstamos: `GET/POST /api/prestamos/`, `GET/PUT/PATCH/DELETE /api/prestamos/{id}/`

## Reportes

- Resumen: `GET /api/reports/summary/?start=YYYY-MM-DD&end=YYYY-MM-DD`
- Flujo mensual (extra): `GET /api/reports/cashflow/monthly/?start=...&end=...`

## Filtros Disponibles (query params)

- IngresosFijos: `name`, `quantity`, `period`
- IngresosExtra: `name`, `quantity`, `date`
- EgresosFijos: `name`, `quantity`, `period`
- EgresosExtra: `name`, `quantity`, `date`
- Ahorros: `name`, `quantity`, `period`

## Ejemplos con cURL

```bash
# 1) Login y guardar ACCESS en variable
ACCESS=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@mail.com","password":"your-pass"}' | jq -r .access)

# 2) Crear ingreso fijo
curl -s -X POST http://localhost:8000/api/IngresosFijos/ \
  -H "Authorization: Bearer $ACCESS" -H 'Content-Type: application/json' \
  -d '{"name":"Salario","reason":"Pago mensual","quantity":"1000.00","period":"Mensual"}'

# 3) Crear egreso extra
curl -s -X POST http://localhost:8000/api/EgresosExtra/ \
  -H "Authorization: Bearer $ACCESS" -H 'Content-Type: application/json' \
  -d '{"name":"Comida","reason":"Restaurante","quantity":"25.00","date":"2025-08-28"}'

# 4) Crear ahorro y depositar
AH=$(curl -s -X POST http://localhost:8000/api/ahorros/ \
  -H "Authorization: Bearer $ACCESS" -H 'Content-Type: application/json' \
  -d '{"name":"Viaje","reason":"Vacaciones","quantity":"2000.00","payment":"200.00","loan":false,"period":"Mensual","accrued":"0.00","missing":"2000.00"}')
AH_ID=$(echo "$AH" | jq -r .id)
curl -s -X POST http://localhost:8000/api/ahorros/$AH_ID/depositar/ \
  -H "Authorization: Bearer $ACCESS" -H 'Content-Type: application/json' \
  -d '{"amount":"200.00","note":"salario"}'

# 5) Reporte resumen del mes
curl -s -X GET 'http://localhost:8000/api/reports/summary/?start=2025-08-01&end=2025-08-31' \
  -H "Authorization: Bearer $ACCESS"
```

> Nota: estos ejemplos usan `jq` para extraer campos de la respuesta.

## Insomnia – Colección lista para importar

Archivo: `web/docs/insomnia_finansas.json`

1. Abrir Insomnia → Application → Preferences → Data → Import Data → From File.
2. Seleccionar el archivo `insomnia_finansas.json`.
3. En el entorno `Local`, definir `baseUrl` (por defecto `http://localhost:8000`) y `access` (token JWT después de hacer login).

### Variables de entorno (Insomnia)

```json
{
  "baseUrl": "http://localhost:8000",
  "access": "<PEGAR_TOKEN_ACCESS_AQUI>"
}
```

## Swagger / OpenAPI

- UI: `http://localhost:8000/docs/`
- JSON: `http://localhost:8000/swagger.json`
- YAML: `http://localhost:8000/swagger.yaml`

## Notas de Seguridad

- Todos los recursos de negocio requieren JWT (`IsAuthenticated`).
- Cada registro se asocia a `owner` automáticamente en creación y se filtra por usuario autenticado.

## Próximos pasos sugeridos

- Categorías para ingresos/egresos y presupuestos mensuales.
- Exportación CSV/Excel por rango.
- Estandarizar rutas a kebab-case.
