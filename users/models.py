# Importamos las clases necesarias desde Django
from django.db import models  # Para definir modelos y campos de base de datos
import os
from django.contrib.auth.models import AbstractUser, BaseUserManager  # Para crear un usuario personalizado
from django.utils import timezone  # Para manejar fechas y horas con zona horaria
import datetime  # Para trabajar con operaciones de fecha y tiempo


# -----------------------------------------------------------
# MANAGER PERSONALIZADO PARA EL MODELO USER
# -----------------------------------------------------------
class UserManager(BaseUserManager):
    """
    Manager que gestiona la creación de usuarios y superusuarios
    utilizando el correo electrónico en lugar de username.
    """
    use_in_migrations = True  # Permite usar este manager en migraciones

    def _create_user(self, email, password, **extra_fields):
        """
        Método interno que crea y guarda un usuario.
        Se utiliza tanto para usuarios normales como para superusuarios.
        """
        if not email:  # Validamos que el email no sea vacío
            raise ValueError("El email es obligatorio")

        email = self.normalize_email(email)  # Normaliza el email (minúsculas)
        user = self.model(email=email, **extra_fields)  # Crea instancia del modelo User
        user.set_password(password)  # Encripta la contraseña antes de guardarla
        user.save(using=self._db)  # Guarda el usuario en la base de datos
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Crea un usuario normal.
        """
        extra_fields.setdefault("is_staff", False)  # No es staff por defecto
        extra_fields.setdefault("is_superuser", False)  # No es superusuario por defecto
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Crea un superusuario con permisos de administrador.
        """
        extra_fields.setdefault("is_staff", True)  # Obligatorio para superusuarios
        extra_fields.setdefault("is_superuser", True)  # Obligatorio para superusuarios

        # Validaciones para evitar errores de configuración
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser debe tener is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


# -----------------------------------------------------------
# MODELO PERSONALIZADO DE USUARIO
# -----------------------------------------------------------
class User(AbstractUser):
    """
    Modelo de usuario personalizado que usa email como campo principal
    y agrega información adicional como cumpleaños, teléfono, país e imagen.
    """
    username = None  # Eliminamos el campo username porque usaremos email
    email = models.EmailField(unique=True)  # Email único como identificador

    # Definimos los campos obligatorios para la autenticación
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Solo pedimos email y password para crear el usuario

    # Campos adicionales de información del usuario
    birthday = models.DateField(default="2000-01-01")  # Fecha de nacimiento
    phone = models.CharField(max_length=15, default="0000000000")  # Teléfono
    country = models.CharField(max_length=50, default="Unknown")  # País

    # NUEVO: Campo para almacenar imagen de perfil
    profile_image = models.ImageField(
        upload_to="profile_images/",  # Carpeta dentro de MEDIA_ROOT donde se guardan
        default="profile_images/default.png",  # Imagen por defecto si no se sube ninguna
        blank=True,  # Permite que quede vacío al registrarse
        null=True  # Permite que quede vacío en la base de datos
    )

    # Asociamos el Manager personalizado
    objects = UserManager()

    def __str__(self):
        """
        Representación del objeto User en texto.
        """
        return self.email


# -----------------------------------------------------------
# MODELO PARA RECUPERACIÓN DE CONTRASEÑA
# -----------------------------------------------------------
class PasswordResetToken(models.Model):
    """
    Modelo para almacenar tokens temporales de recuperación de contraseña.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario
    token = models.CharField(max_length=6)  # Ejemplo: "123456"
    created_at = models.DateTimeField(auto_now_add=True)  # Se guarda automáticamente al crear

    def is_valid(self):
        """
        Verifica si el token sigue siendo válido.
        Expira a los 10 minutos de haber sido creado.
        """
        return timezone.now() < self.created_at + datetime.timedelta(minutes=10)


class PasswordResetCode(models.Model):
    user_email = models.EmailField()
    code = models.CharField(max_length=12)
    purpose = models.CharField(max_length=32, default="reset")  # "reset" | "signup" | etc.
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self) -> bool:
        return timezone.now() <= self.expires_at


class PendingSignup(models.Model):
    email = models.EmailField()
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    extra_info = models.JSONField(blank=True, null=True)  # opcional
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.email} (aprobado: {bool(self.approved_at)})"

# ======================================================
# Forzar Cloudinary para profile_image si está configurado
# (no requiere migración; ajusta el storage en tiempo de carga)
# ======================================================
try:
    from django.conf import settings as _settings
    if os.environ.get("CLOUDINARY_URL") or getattr(_settings, 'DEFAULT_FILE_STORAGE', '').endswith('MediaCloudinaryStorage'):
        from cloudinary_storage.storage import MediaCloudinaryStorage
        # Cambia el storage del campo profile_image a Cloudinary
        User._meta.get_field('profile_image').storage = MediaCloudinaryStorage()
except Exception:
    # Silenciar cualquier error de import o en entorno local sin Cloudinary
    pass
