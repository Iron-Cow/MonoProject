# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAdminUser, BasePermission
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model

User = get_user_model()


class IsOwnerOrAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return bool(request.user and obj.tg_id == request.user.tg_id or request.user.is_superuser)


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'tg_id'

    def get_permissions(self):
        permission = IsAdminUser()
        if self.action in ('partial_update', 'update', 'retrieve'):
            permission = IsOwnerOrAdminUser()

        return [permission]

    def update(self, request, *args, **kwargs):
        if self.action == "partial_update":
            return super().update(request, *args, **kwargs)
            return Response({'details': 'No PUT updates allowed.'},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    # def retrieve(self, request, tg_id=None, *args, **kwargs):
    #     q = User.objects.filter(tg_id=tg_id)
    #
    #     if not q.exists():
    #         return Response({'details': 'Invalid id'}, status.HTTP_404_NOT_FOUND)
    #
    #     # retrieve only to owner or admin
    #     if q.first().tg_id != request.user.tg_id and not request.user.is_superuser:
    #         return Response({'details': 'You do not have permission to perform this action.'}, status.HTTP_404_NOT_FOUND)
    #
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)


class UserView(APIView):
    def get(self, request):
        return Response({"hello": "world"}, status=status.HTTP_200_OK)

    def get_single(self, request, tg_id: str):
        return Response({"hello": "world2"}, status=status.HTTP_200_OK)

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

    def post(self, request):
        return Response({"data": "Not Implemented"}, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    token_obtain_pair = TokenObtainPairView.as_view()
