from django.urls import path
from users.api.views import (
    RegisterView, userView,
    PasswordResetRequestView, PasswordResetVerifyView, PasswordResetConfirmView,
    LogoutView, UserInfoView, LoginView, RefreshView, approve_signup_view,
)

urlpatterns = [
    # Registro y login
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', RefreshView.as_view(), name='token_refresh'),

    # Información del usuario
    path('auth/me/', userView.as_view(), name='user_view'),
    path('auth/user/', UserInfoView.as_view(), name='user_info'),

    # Logout
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    # Reset de contraseña
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),  
    # Envía código de verificación al correo del usuario
    path('auth/password-verify/', PasswordResetVerifyView.as_view(), name='password_verify'),  
    # Confirma el código y permite cambiar la contraseña
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # Aprobación de registro pendiente
    path("approve-signup/<str:token>/", approve_signup_view, name="approve-signup"),
]
