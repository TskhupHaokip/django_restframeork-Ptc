from django.contrib.auth.models import User
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from api.serializers import UserSerializer,BookSerializer
from .models import Book
from rest_framework_simplejwt.tokens import RefreshToken


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"message": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 1. Initialize the token object with the provided refresh token
            token = RefreshToken(refresh_token)

            # 2. Add the token to the database blacklist
            token.blacklist()

            return Response(
                {"message": "Logged out successfully"},
                status=status.HTTP_200_OK
            )

        except TokenError:
            # Catches issues like expired, invalid, or tampered tokens
            return Response(
                {"message": "Invalid or expired refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"message": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class AllUserList(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get(self, request):
        users = self.get_queryset()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
