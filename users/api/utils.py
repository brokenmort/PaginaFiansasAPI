# users/api/utils.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core import signing
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
import secrets
from datetime import timedelta

from ..models import PasswordResetCode, PendingSignup  # ver modelos más abajo


def _send_html_email(subject: str, to: list[str], template_name: str, context: dict):
    """
    Envía un email con versión HTML y texto plano fallback.
    Usa templates en `templates/emails/`.
    """
    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)  # fallback de texto

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=to,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def _generate_numeric_code(length: int = 6) -> str:
    """
    Genera un código numérico aleatorio criptográficamente seguro.
    """
    # 10**6 = 1,000,000; devolvemos string con ceros a la izquierda si hace falta
    upper = 10 ** length
    code = secrets.randbelow(upper)
    return f"{code:0{length}d}"


def send_reset_code(email: str, length: int = 6) -> str:
    """
    Genera un código de recuperación y lo envía al correo del usuario con HTML.
    También persiste el código para validarlo después.
    """
    code = _generate_numeric_code(length=length)

    # Guarda el código para validación futura
    PasswordResetCode.objects.create(
        user_email=email,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=15),  # 15 min de validez
    )

    context = {
        "code": code,
        "app_name": getattr(settings, "APP_NAME", "Tu Aplicación"),
        "support_email": getattr(settings, "SUPPORT_EMAIL", None),
        "valid_minutes": 15,
    }
    _send_html_email(
        subject="Código de recuperación",
        to=[email],
        template_name="emails/reset_code.html",
        context=context,
    )
    return code


# -------------------------
# Flujo de aprobación de registro
# -------------------------

def send_signup_request_to_admins(pending: PendingSignup, request=None):
    """
    Envía un correo a superusuarios con el botón 'Aceptar solicitud'.
    El enlace lleva un token firmado para aprobar la solicitud.
    Requiere configurar SITE_DOMAIN o usar `request` para armar la URL absoluta.
    """
    # Token firmado con datos mínimos
    token = signing.dumps({"pending_id": pending.id}, salt="approve-signup")
    path = reverse("approve-signup", kwargs={"token": token})

    if request is not None:
        scheme = "https" if request.is_secure() else "http"
        base = f"{scheme}://{request.get_host()}"
    else:
        # Fallback: lee de settings
        base = getattr(settings, "SITE_DOMAIN", "http://localhost:8000")

    approve_url = f"{base}{path}"

    User = get_user_model()
    admin_emails = list(User.objects.filter(is_superuser=True, is_active=True)
                        .values_list("email", flat=True))

    if not admin_emails:
        return

    context = {
        "pending": pending,
        "approve_url": approve_url,
        "app_name": getattr(settings, "APP_NAME", "Tu Aplicación"),
    }
    _send_html_email(
        subject=f"Nueva solicitud de registro: {pending.email}",
        to=admin_emails,
        template_name="emails/signup_request_admin.html",
        context=context,
    )


def approve_signup_and_send_code(token: str, code_length: int = 6) -> str:
    """
    Valida el token de aprobación, marca la solicitud como aprobada y
    envía el código de registro al correo del solicitante.
    Lanza excepción si el token es inválido o ya usado.
    """
    data = signing.loads(token, salt="approve-signup", max_age=60 * 60 * 24)  # 24h
    pending_id = data["pending_id"]
    pending = PendingSignup.objects.select_for_update().get(id=pending_id)

    if pending.approved_at is not None:
        raise ValueError("La solicitud ya fue aprobada.")

    # Marca aprobada
    pending.approved_at = timezone.now()
    pending.save(update_fields=["approved_at"])

    # Genera y guarda código de registro (puedes reutilizar PasswordResetCode o otro modelo)
    code = _generate_numeric_code(length=code_length)
    PasswordResetCode.objects.create(
        user_email=pending.email,
        code=code,
        purpose="signup",  # opcional: distinguir uso
        expires_at=timezone.now() + timedelta(minutes=30),
    )

    # Envía correo al solicitante
    context = {
        "code": code,
        "app_name": getattr(settings, "APP_NAME", "Tu Aplicación"),
        "valid_minutes": 30,
    }
    _send_html_email(
        subject="Tu código de registro",
        to=[pending.email],
        template_name="emails/signup_code.html",
        context=context,
    )

    return code
