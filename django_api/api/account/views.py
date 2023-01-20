# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView


class UserView(APIView):
    def get(self, request):
        return Response({"hello": "world"}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "ok", "data": serializer.data}, status=status.HTTP_201_CREATED
            )
        elif User.objects.get(tg_id=request.data['tg_id']):
            return Response(
                {"status": "fail", "data": "user exists"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {"status": "fail", "data": "not valid"}, status=status.HTTP_400_BAD_REQUEST
            )


class CustomTokenObtainPairView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer
    token_obtain_pair = TokenObtainPairView.as_view()
