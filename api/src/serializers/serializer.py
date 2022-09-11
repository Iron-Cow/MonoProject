from serpy import DictSerializer, IntField, Field, StrField, BoolField, MethodField


class UserSerializer(DictSerializer):
    tg_id = StrField()
    is_superuser = MethodField("set_is_superuser")
    is_admin = MethodField("set_is_admin")

    def set_is_superuser(self, obj: dict):
        return bool(obj.get("is_superuser", False))

    def set_is_admin(self, obj: dict):
        return bool(obj.get("is_admin", False))