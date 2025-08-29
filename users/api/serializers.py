# Importamos serializers de DRF
from rest_framework import serializers
# Importamos el modelo de usuario personalizado
from users.models import User


# -----------------------------------------------------------
# SERIALIZER PARA REGISTRO DE USUARIO
# -----------------------------------------------------------
class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer que gestiona el registro de nuevos usuarios.
    Permite recibir y guardar la imagen de perfil junto con los demás datos.
    """
    password = serializers.CharField(write_only=True, min_length=8)  # Contraseña solo escritura
    profile_image = serializers.ImageField(required=False)  # Campo para la imagen de perfil (opcional)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password',
            'birthday',
            'first_name',
            'last_name',
            'phone',
            'country',
            'profile_image',  # Añadimos la imagen en los campos que se aceptan
        )
        extra_kwargs = {
            'birthday': {'required': True},
            'phone': {'required': True},
            'country': {'required': True},
            'password': {'write_only': True, 'required': True},
            'email': {'required': True},
        }

    def create(self, validated_data):
        """
        Sobrescribimos create para encriptar contraseña y guardar imagen.
        """
        password = validated_data.pop('password', None)  # Extraemos la contraseña
        instance = self.Meta.model(**validated_data)  # Creamos instancia del modelo User
        if password is not None:
            instance.set_password(password)  # Encriptamos contraseña
        instance.save()  # Guardamos usuario
        return instance


# -----------------------------------------------------------
# SERIALIZER PARA MOSTRAR DATOS BÁSICOS DEL USUARIO
# -----------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer usado para retornar información básica de usuario.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'profile_image')  # Añadimos la imagen


# -----------------------------------------------------------
# SERIALIZER PARA ACTUALIZAR DATOS DEL USUARIO
# -----------------------------------------------------------
class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer que permite actualizar datos del usuario incluyendo imagen.
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'birthday', 'phone', 'country', 'profile_image')


# -----------------------------------------------------------
# SERIALIZERS PARA RESET DE CONTRASEÑA
# -----------------------------------------------------------
class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer para solicitar un código de reseteo de contraseña.
    """
    email = serializers.EmailField()


class PasswordResetVerifySerializer(serializers.Serializer):
    """
    Serializer para verificar código enviado al correo.
    """
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer para confirmar el cambio de contraseña.
    """
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)
