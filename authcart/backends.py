from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend that allows users to authenticate
    using either their username or their email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD) or kwargs.get("email")

        if not username or not password:
            return None

        identifier = str(username).strip()

        try:
            # Query users matching either username or email (case-insensitive)
            users = UserModel.objects.filter(
                Q(username__iexact=identifier) | Q(email__iexact=identifier)
            )

            # Prioritize superusers, staff, and active accounts if multiple matches exist
            for user in users.order_by("-is_superuser", "-is_staff", "-is_active"):
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
        except Exception:
            return None

        return None
