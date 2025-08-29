# Importamos librerÃƒÂ­as necesarias
import random  # Para generar cÃƒÂ³digos aleatorios de recuperaciÃƒÂ³n
from rest_framework import status, permissions  # Para respuestas HTTP y permisos
from rest_framework.views import APIView  # Para crear vistas basadas en clases
from rest_framework.response import Response  # Para devolver respuestas JSON
from users.api.serializers import (
    UserRegisterSerializer, UserUpdateSerializer,
    PasswordResetRequestSerializer, PasswordResetVerifySerializer,
    PasswordResetConfirmSerializer
)
from rest_framework.permissions import IsAuthenticated, AllowAny  # Permisos para vistas
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.models import User, PasswordResetToken  # Modelos de usuario y token
from django.core.mail import send_mail  # Para enviar emails
from django.conf import settings  # Para acceder a configuraciones (ej. email)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser  # Necesario para manejar imÃƒÂ¡genes

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from .utils import approve_signup_and_send_code
from django.core.files.storage import default_storage

# -----------------------------------------------------------
# VISTA DE REGISTRO DE USUARIO
# -----------------------------------------------------------
class RegisterView(APIView):
    """
    Vista para registrar nuevos usuarios.
    Permite subir imagen de perfil usando multipart/form-data.
    """
    permission_classes = [AllowAny]  # Cualquiera puede acceder
    parser_classes = [MultiPartParser, FormParser]  # Soporte para envÃƒÂ­o de archivos e imÃƒÂ¡genes

    @swagger_auto_schema(
        operation_summary='Registro de usuario',
        tags=['Auth'],
        operation_description='Crea un usuario nuevo. EnvÃ­a multipart/form-data si incluye profile_image, o JSON si no envÃ­a archivo.',
        consumes=['multipart/form-data', 'application/json'],
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, description='Correo'),
            openapi.Parameter('password', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, description='ContraseÃ±a'),
            openapi.Parameter('birthday', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, description='YYYY-MM-DD'),
            openapi.Parameter('first_name', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('last_name', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('phone', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('country', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('profile_image', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False)
        ],
        responses={
            201: openapi.Response(
                description='Usuario creado',
                examples={'application/json': {'id': 1, 'email': 'user@mail.com'}}
            )
        }
    )
    def post(self, request):
        """
        Maneja la solicitud POST para registrar un nuevo usuario.
        """
        serializer = UserRegisterSerializer(data=request.data, context={'request': request})  # Crea serializer con datos recibidos
        if serializer.is_valid(raise_exception=True):  # Valida datos, lanza excepciÃƒÂ³n si no son vÃƒÂ¡lidos
            serializer.save()  # Guarda el usuario en la base de datos
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Responde con datos del usuario
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------
# VISTA DE PERFIL DE USUARIO
# -----------------------------------------------------------
class userView(APIView):
    """
    Vista para obtener y actualizar informaciÃƒÂ³n del usuario autenticado.
    """
    permission_classes = [IsAuthenticated]  # Solo usuarios logueados
    parser_classes = [MultiPartParser, FormParser]  # Soporta envÃ­o de archivos para profile_image

    @swagger_auto_schema(operation_summary='Perfil del usuario (detalle)', tags=['Usuarios'],
                        responses={200: openapi.Response('OK', examples={'application/json': {
                            'id': 1,
                            'email': 'user@mail.com',
                            'birthday': '2000-01-01',
                            'first_name': 'Nelson',
                            'last_name': 'Giraldo',
                            'phone': '3000000000',
                            'country': 'CO',
                            'profile_image': None
                        }})})
    def get(self, request):
        """
        Devuelve informaciÃƒÂ³n del usuario autenticado.
        """
        serializer = UserRegisterSerializer(request.user, context={'request': request})  # Serializa datos del usuario
        return Response(serializer.data)  # Devuelve datos serializados en formato JSON

    @swagger_auto_schema(operation_summary='Actualizar perfil de usuario', tags=['Usuarios'],
                         request_body=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                              'first_name': openapi.Schema(type=openapi.TYPE_STRING, example='Nelson'),
                              'last_name': openapi.Schema(type=openapi.TYPE_STRING, example='Giraldo'),
                              'birthday': openapi.Schema(type=openapi.TYPE_STRING, example='2000-01-01'),
                              'phone': openapi.Schema(type=openapi.TYPE_STRING, example='3000000000'),
                              'country': openapi.Schema(type=openapi.TYPE_STRING, example='CO'),
                              'profile_image': openapi.Schema(type=openapi.TYPE_STRING, format='binary')
                            }
                         ))
    def put(self, request):
        """
        Actualiza datos del usuario, incluyendo imagen de perfil.
        """
        user = User.objects.get(id=request.user.id)  # Busca el usuario autenticado en BD
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)  # Permite actualizaciÃƒÂ³n parcial
        if serializer.is_valid(raise_exception=True):  # Valida datos enviados
            serializer.save()  # Guarda cambios en la base de datos
            return Response(UserUpdateSerializer(user, context={'request': request}).data)  # Devuelve datos actualizados con URL absoluta
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------
# DEBUG: INFO DE STORAGE
# -----------------------------------------------------------
"""
Nota: Se eliminaron las vistas de diagnóstico usadas durante la integración
de Cloudinary y el debug de despliegue para mantener el código limpio.
"""


# -----------------------------------------------------------
# SOLICITUD DE RESET DE CONTRASEÃƒâ€˜A
# -----------------------------------------------------------
class PasswordResetRequestView(APIView):
    """
    EnvÃƒÂ­a un cÃƒÂ³digo al correo para poder restablecer la contraseÃƒÂ±a.
    """
    permission_classes = [AllowAny]  # Cualquiera puede solicitarlo

    @swagger_auto_schema(operation_summary='Solicitar codigo de reseteo', tags=['Auth'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={'email': openapi.Schema(type=openapi.TYPE_STRING, example='user@mail.com')}
        ),
        responses={200: openapi.Response('OK', examples={'application/json': {'detail': 'Codigo enviado'}})}
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)  # Serializa datos recibidos
        serializer.is_valid(raise_exception=True)  # Valida datos

        email = serializer.validated_data["email"]  # Obtiene email
        try:
            user = User.objects.get(email=email)  # Busca usuario por email
        except User.DoesNotExist:
            return Response({"error": "No existe un usuario con ese correo."}, status=404)

        # Genera cÃƒÂ³digo aleatorio de 6 dÃƒÂ­gitos
        token = str(random.randint(100000, 999999))

        # Crea registro de token para ese usuario
        PasswordResetToken.objects.create(user=user, token=token)

        # EnvÃƒÂ­a correo real usando SMTP configurado en settings.py
        send_mail(
            subject="RecuperaciÃƒÂ³n de contraseÃƒÂ±a",
            message=f"Tu cÃƒÂ³digo de recuperaciÃƒÂ³n es: {token}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False  # Lanza error si no se puede enviar
        )

        return Response({"message": "Se ha enviado un cÃƒÂ³digo al correo."}, status=200)


# -----------------------------------------------------------
# VERIFICACIÃƒâ€œN DE TOKEN DE RECUPERACIÃƒâ€œN
# -----------------------------------------------------------
class PasswordResetVerifyView(APIView):
    """
    Verifica que el token enviado al correo sea vÃƒÂ¡lido.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetVerifySerializer(data=request.data)  # Valida email y token
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        token = serializer.validated_data["token"]

        try:
            user = User.objects.get(email=email)  # Busca usuario
            reset_token = PasswordResetToken.objects.filter(user=user, token=token).last()  # Busca ÃƒÂºltimo token
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado."}, status=404)

        # Comprueba si token sigue siendo vÃƒÂ¡lido
        if reset_token and reset_token.is_valid():
            return Response({"valid": True}, status=200)

        return Response({"valid": False}, status=400)


# -----------------------------------------------------------
# CONFIRMAR Y CAMBIAR CONTRASEÃƒâ€˜A
# -----------------------------------------------------------
class PasswordResetConfirmView(APIView):
    """
    Permite establecer nueva contraseÃƒÂ±a si el token es vÃƒÂ¡lido.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_summary='Confirmar reseteo de contrasena', tags=['Auth'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email','token','new_password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, example='user@mail.com'),
                'token': openapi.Schema(type=openapi.TYPE_STRING, example='123456'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, example='newPass123')
            }
        ),
        responses={200: openapi.Response('OK', examples={'application/json': {'message': 'Contrasena actualizada y sesiones cerradas.'}})}
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)  # Valida datos recibidos
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(email=email)  # Busca usuario
            reset_token = PasswordResetToken.objects.filter(user=user, token=token).last()
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado."}, status=404)

        if reset_token and reset_token.is_valid():
            user.set_password(new_password)  # Cambia contraseÃƒÂ±a
            user.save()

            # Revoca todos los tokens JWT anteriores para cerrar sesiones activas
            for outstanding_token in OutstandingToken.objects.filter(user=user):
                BlacklistedToken.objects.get_or_create(token=outstanding_token)

            # Elimina token usado
            reset_token.delete()
            return Response({"message": "ContraseÃƒÂ±a actualizada y sesiones cerradas."}, status=200)

        return Response({"error": "Token invÃƒÂ¡lido o expirado."}, status=400)


# -----------------------------------------------------------
# LOGIN Y REFRESH DE TOKENS JWT
# -----------------------------------------------------------
class LoginView(TokenObtainPairView):
    """
    Genera par de tokens (access y refresh) al iniciar sesiÃƒÂ³n.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary='Login (JWT pair)',
        tags=['Auth'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, example='user@mail.com'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, example='******'),
            }
        ),
        responses={
            200: openapi.Response(
                description='Tokens',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                ),
                examples={'application/json': {
                    'access': 'eyJhbGciOi...access...',
                    'refresh': 'eyJhbGciOi...refresh...'
                }}
            )
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RefreshView(TokenRefreshView):
    """
    Permite refrescar token de acceso usando refresh token.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary='Refrescar access token',
        tags=['Auth'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={'refresh': openapi.Schema(type=openapi.TYPE_STRING)}
        ),
        responses={
            200: openapi.Response(
                description='Nuevo access',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'access': openapi.Schema(type=openapi.TYPE_STRING)}
                ),
                examples={'application/json': {'access': 'eyJhbGciOi...access...'}}
            )
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# -----------------------------------------------------------
# LOGOUT DE USUARIO
# -----------------------------------------------------------
class LogoutView(APIView):
    """
    Revoca tokens JWT para cerrar sesiÃƒÂ³n del usuario.
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Logout (revocar tokens)',
        tags=['Auth'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'refresh': openapi.Schema(type=openapi.TYPE_STRING)},
            description='Opcional: si no se envÃƒÂ­a refresh, se revocan todos los tokens del usuario.'
        )
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh", None)  # Obtiene token refresh enviado
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # Revoca token especÃƒÂ­fico
                return Response({"detail": "Logout exitoso (refresh token revocado)."}, status=status.HTTP_205_RESET_CONTENT)
            
            # Si no se envÃƒÂ­a refresh, revoca todos los tokens del usuario
            tokens = OutstandingToken.objects.filter(user=request.user)
            for token in tokens:
                BlacklistedToken.objects.get_or_create(token=token)
            
            return Response({"detail": "Logout exitoso (todos los tokens revocados)."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------
# VISTA DE INFORMACIÃƒâ€œN BÃƒÂSICA DEL USUARIO
# -----------------------------------------------------------
class UserInfoView(APIView):
    """
    Devuelve informaciÃƒÂ³n bÃƒÂ¡sica del usuario autenticado.
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary='Info basica del usuario', tags=['Usuarios'],
                        responses={200: openapi.Response('OK', examples={'application/json': {
                            'username': None,
                            'email': 'user@mail.com',
                            'id': 1,
                            'profile_image': None
                        }})})
    def get(self, request):
        user = request.user  # Obtiene usuario autenticado
        img_url = None
        try:
            if user.profile_image:
                img_url = user.profile_image.url
        except Exception:
            img_url = None
        if img_url and not str(img_url).startswith(("http://", "https://")):
            img_url = request.build_absolute_uri(img_url)

        return Response({
            "username": user.username,
            "email": user.email,
            "id": user.id,
            "profile_image": img_url
        })


def _is_superuser(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(_is_superuser)
@transaction.atomic
def approve_signup_view(request, token: str):
    """
    Endpoint al que llega el botÃƒÂ³n 'Aceptar solicitud'.
    Requiere que el usuario estÃƒÂ© autenticado y sea superusuario.
    """
    if request.method != "GET":
        return HttpResponseBadRequest("MÃƒÂ©todo no permitido.")
    try:
        approve_signup_and_send_code(token)
    except Exception as e:
        return HttpResponseBadRequest(f"Error: {e}")
    return HttpResponse("Solicitud aprobada y cÃƒÂ³digo enviado al solicitante.")




