# Create your views here.
import secrets
import string
import uuid

from account.models import User as custom_user
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, BasePermission, IsAdminUser
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


# Family invite/code flow (no DB models, cache-backed)
CODE_TTL_SECONDS = 10 * 60  # 10 minutes
INVITE_TTL_SECONDS = 24 * 60 * 60  # 24 hours


def _generate_code(length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class FamilyInviteCodeApiView(APIView):
    """Generate a short-lived invite code for a specific user tg_id."""

    permission_classes = [AllowAny]

    def post(self, request, tg_id: str | None = None):
        if tg_id is None:
            return Response({"error": "tg_id is required"}, status=400)

        # Ensure user exists
        user = get_object_or_404(
            User, tg_id=tg_id
        )  # pyright: ignore[reportArgumentType]

        # Reuse existing valid code if present
        existing_code_key = f"family_code_user:{user.tg_id}"
        existing_code = cache.get(existing_code_key)
        if existing_code:
            return Response(
                {"code": existing_code, "expires_in": CODE_TTL_SECONDS},
                status=200,
            )

        # Generate a unique code and store mapping
        for _ in range(5):
            code = _generate_code(6)
            code_key = f"family_code:{code}"
            if not cache.get(code_key):
                cache.set(code_key, str(user.tg_id), timeout=CODE_TTL_SECONDS)
                cache.set(existing_code_key, code, timeout=CODE_TTL_SECONDS)
                return Response(
                    {"code": code, "expires_in": CODE_TTL_SECONDS}, status=201
                )

        return Response({"error": "failed to generate code"}, status=500)


class FamilyInviteProposalApiView(APIView):
    """Resolve a family invite code and create a pending invite in cache.

    Body:
    - inviter_tg_id: required
    - code: required
    """

    permission_classes = [AllowAny]

    def post(self, request):
        inviter_tg_id = str(request.data.get("inviter_tg_id") or "").strip()
        code = str(request.data.get("code") or "").strip().upper()
        if not inviter_tg_id or not code:
            return Response(
                {"error": "inviter_tg_id and code are required"}, status=400
            )

        inviter = get_object_or_404(
            User, tg_id=inviter_tg_id
        )  # pyright: ignore[reportArgumentType]

        # Resolve code -> member_tg_id
        member_tg_id = cache.get(f"family_code:{code}")
        if not member_tg_id:
            return Response({"error": "invalid_or_expired_code"}, status=404)

        if str(member_tg_id) == str(inviter.tg_id):
            return Response({"error": "cannot_invite_self"}, status=400)

        member = get_object_or_404(
            User, tg_id=member_tg_id
        )  # pyright: ignore[reportArgumentType]

        # Invalidate the code after consumption
        cache.delete(f"family_code:{code}")
        cache.delete(f"family_code_user:{member_tg_id}")

        # Create pending invite
        invite_id = uuid.uuid4().hex
        invite_key = f"family_invite:{invite_id}"
        payload = {
            "invite_id": invite_id,
            "inviter_tg_id": str(inviter.tg_id),
            "member_tg_id": str(member.tg_id),
            "status": "pending",
        }
        cache.set(invite_key, payload, timeout=INVITE_TTL_SECONDS)

        return Response(
            {
                "invite_id": invite_id,
                "inviter_tg_id": str(inviter.tg_id),
                "member_tg_id": str(member.tg_id),
                "status": "pending",
            },
            status=201,
        )


class FamilyInviteDecisionApiView(APIView):
    """Accept or decline a pending invite.

    Body:
    - invite_id: required
    - decision: "accept" | "decline"
    """

    permission_classes = [AllowAny]

    def post(self, request):
        invite_id = str(request.data.get("invite_id") or "").strip()
        decision = str(request.data.get("decision") or "").strip().lower()
        actor_tg_id = str(request.data.get("actor_tg_id") or "").strip()
        if not invite_id or decision not in ("accept", "decline"):
            return Response({"error": "invalid_request"}, status=400)

        invite_key = f"family_invite:{invite_id}"
        invite = cache.get(invite_key)
        if not invite:
            return Response({"error": "invite_not_found_or_expired"}, status=404)

        if invite.get("status") in ("accepted", "declined"):
            return Response(invite, status=200)

        inviter_tg_id = invite.get("inviter_tg_id")
        member_tg_id = invite.get("member_tg_id")

        # Ensure only intended member can act
        if not actor_tg_id or actor_tg_id != str(invite.get("member_tg_id")):
            return Response({"error": "forbidden"}, status=403)

        if decision == "accept":
            inviter = get_object_or_404(
                User, tg_id=inviter_tg_id
            )  # pyright: ignore[reportArgumentType]
            member = get_object_or_404(
                User, tg_id=member_tg_id
            )  # pyright: ignore[reportArgumentType]
            inviter.family_members.add(member)
            # symmetrical M2M ensures both sides
            invite["status"] = "accepted"
        else:
            invite["status"] = "declined"

        cache.set(invite_key, invite, timeout=60 * 10)  # short keep after decision

        return Response(
            {
                "invite_id": invite_id,
                "status": invite["status"],
                "inviter_tg_id": inviter_tg_id,
                "member_tg_id": member_tg_id,
            },
            status=200,
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
