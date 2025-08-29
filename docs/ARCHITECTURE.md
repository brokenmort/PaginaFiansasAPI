# Arquitectura del proyecto

- Backend: Django + DRF
  - Apps: users, ingresos, egresos, ahorros, prestamos
  - Autenticación: JWT (simplejwt)
  - CORS: django-cors-headers
  - Documentación: drf-spectacular (`/schema`, `/docs`, `/redoc`)
- Deploy: Heroku (gunicorn + whitenoise)
- Base de datos: DATABASE_URL (Postgres en Heroku)
- Estáticos: `STATIC_ROOT` con `whitenoise`
- Media: Cloudinary (si `CLOUDINARY_URL` está definido)

## Flujo de subida de imágenes
- Campo `users.User.profile_image` (ImageField)
- Storage: `MediaCloudinaryStorage` cuando hay `CLOUDINARY_URL`
- Serializers devuelven URL absoluta (`request` en `context`)

## Endpoints clave
- `POST /api/auth/login/` → JWT
- `GET/PUT /api/auth/me/` → perfil del usuario
- `GET /docs/` → Swagger UI (esquema en `/schema/`)

## Ajustes de producción (Heroku)
- `DJANGO_DEBUG=False`
- `DJANGO_SECRET_KEY=<secreto>`
- `CLOUDINARY_URL` (o CLOUDINARY_* por separado)
- `DATABASE_URL` (Postgres)
