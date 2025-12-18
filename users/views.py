from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from users.serializers import UserSerializer


@extend_schema(
    summary="Register a new user",
    description="Create a new user account.",
    request=UserSerializer,
    responses={
        201: UserSerializer,
        400: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            name="Successful registration",
            value={
                "id": 1,
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe"
            },
            response_only=True,
            status_codes=["201"],
        ),
    ],
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


@extend_schema(
    summary="Login user",
    description="Authenticate user and return auth token.",
    request=AuthTokenSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            name="Successful login",
            value={
                "token": "a1b2c3d4e5f6..."
            },
            response_only=True,
            status_codes=["200"],
        ),
    ],
)
class LoginUserView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


@extend_schema(
    summary="Retrieve user profile",
    description="Retrieve authenticated user's profile.",
    responses={
        200: UserSerializer,
        401: OpenApiTypes.OBJECT,
    },
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication, )

    def get_object(self):
        return self.request.user