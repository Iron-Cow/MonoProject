# Create your views here.
from account.models import User as custom_user
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import CustomTokenObtainPairSerializer, UserSerializer

User: custom_user = get_user_model()  # pyright: ignore[reportAssignmentType]


class IsOwnerOrAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_object_permission(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, request, _, obj
    ) -> bool:
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return bool(
            request.user
            and obj.tg_id == request.user.tg_id
            or request.user.is_superuser
        )


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.prefetch_related("family_members")
    lookup_field = "tg_id"

    def get_permissions(self):
        permission = IsAdminUser()
        if self.action in ("partial_update", "update", "retrieve"):
            permission = IsOwnerOrAdminUser()

        return [permission]

    def update(self, request, *args, **kwargs):
        if self.action == "partial_update":
            return super().update(request, *args, **kwargs)
        return Response(
            {"details": "No PUT updates allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


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
                {"status": "ok", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        elif User.objects.filter(tg_id=request.data["tg_id"]).exists():
            return Response(
                {"status": "fail", "data": "user exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {"status": "fail", "data": "not valid"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# TODO: add unit tests
class FamilyMemberApiView(APIView):
    def delete(self, request, tg_id=None, member_tg_id=None):
        user = get_object_or_404(
            User, tg_id=tg_id
        )  # pyright: ignore[reportArgumentType]
        family_member = get_object_or_404(
            User, tg_id=member_tg_id
        )  # pyright: ignore[reportArgumentType]
        user.family_members.remove(family_member)
        return Response(status=status.HTTP_200_OK)

    def post(self, request, tg_id=None, member_tg_id=None):
        user = get_object_or_404(
            User, tg_id=tg_id
        )  # pyright: ignore[reportArgumentType]
        family_member = get_object_or_404(
            User, tg_id=member_tg_id
        )  # pyright: ignore[reportArgumentType]
        user.family_members.add(family_member)
        return Response(status=status.HTTP_201_CREATED)

    def get(self, request, tg_id=None):
        user = get_object_or_404(
            User.objects.prefetch_related("family_members"), tg_id=tg_id
        )  # pyright: ignore[reportArgumentType]
        return Response(
            {"members": [i.name for i in user.family_members.all()]},
            status=status.HTTP_200_OK,
        )


class FamilyMemberListApiView(APIView):
    def get(self, request, tg_id=None):
        user = get_object_or_404(
            User.objects.prefetch_related("family_members"), tg_id=tg_id
        )  # pyright: ignore[reportArgumentType]
        return Response(
            {"members": [i.name for i in user.family_members.all()]},
            status=status.HTTP_200_OK,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    token_obtain_pair = TokenObtainPairView.as_view()
