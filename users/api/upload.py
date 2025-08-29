from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ProfileImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary='Subir imagen de perfil',
        tags=['Usuarios'],
        manual_parameters=[
            openapi.Parameter('profile_image', openapi.IN_FORM, type=openapi.TYPE_FILE, required=True)
        ],
        consumes=['multipart/form-data']
    )
    def post(self, request):
        user = request.user
        try:
            f = request.FILES.get('profile_image')
            if not f:
                return Response({"detail": "Falta profile_image"}, status=400)
            user.profile_image.save(f.name, f, save=True)
            url = getattr(user.profile_image, 'url', None)
            if url and not str(url).startswith(("http://", "https://")):
                url = request.build_absolute_uri(url)
            return Response({"profile_image": url}, status=200)
        except Exception as e:
            return Response({"detail": str(e), "type": e.__class__.__name__}, status=500)
