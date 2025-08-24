from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    FamilyInviteCodeApiView,
    FamilyInviteDecisionApiView,
    FamilyInviteProposalApiView,
    FamilyMemberApiView,
    FamilyMemberListApiView,
    UserViewSet,
)

router = routers.DefaultRouter()
router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "users/<str:tg_id>/family_code/",
        FamilyInviteCodeApiView.as_view(),
        name="family-code-generate",
    ),
    path(
        "users/family_invite/proposal/",
        FamilyInviteProposalApiView.as_view(),
        name="family-invite-proposal",
    ),
    path(
        "users/family_invite/decision/",
        FamilyInviteDecisionApiView.as_view(),
        name="family-invite-decision",
    ),
    path(
        "users/<str:tg_id>/family_members/<str:member_tg_id>/",
        FamilyMemberApiView.as_view(),
    ),
    path("users/<str:tg_id>/family_members/", FamilyMemberListApiView.as_view()),
    path("token/", CustomTokenObtainPairView.as_view(), name="token-obtain"),
    path("token-refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
