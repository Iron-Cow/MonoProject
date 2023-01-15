from serpy import DictSerializer, IntField, Field, StrField, BoolField, MethodField
from humps import decamelize


class CustomDictSerializer(DictSerializer):
    def to_value(self, instance) -> dict:
        snaked_instance = decamelize(instance)
        return super().to_value(snaked_instance)


class UserSerializer(DictSerializer):
    tg_id = StrField()
    is_superuser = MethodField("set_is_superuser")
    is_admin = MethodField("set_is_admin")

    def set_is_superuser(self, obj: dict):
        return bool(obj.get("is_superuser", False))

    def set_is_admin(self, obj: dict):
        return bool(obj.get("is_admin", False))


class ClientInfoSerializer(CustomDictSerializer):
    monotoken = StrField()
    client_id = StrField()
    name = StrField()
    web_hook_url = StrField()
    tg_id = StrField()

class AccountSerializer(CustomDictSerializer):
    account_id = StrField("id")
    send_id = StrField()
    currency_code = IntField()
    balance = IntField()
    cashback_type = StrField()
    credit_limit = IntField()
    type = StrField()
    iban = StrField()


class JarSerializer(CustomDictSerializer):
    jar_id = StrField("id")
    send_id = StrField()
    title = StrField()
    currency_code = IntField()
    balance = IntField()
    description = StrField()
    goal = IntField()


class TransactionSerializer(CustomDictSerializer):
    id = StrField("id")
    time = IntField()
    description = StrField()
    mcc = IntField()
    original_mcc = IntField()
    amount = IntField()
    operation_amount = IntField()
    currency_code = IntField()
    commission_rate = IntField()
    cashback_amount = IntField()
    balance = IntField()
    hold = BoolField()
    receipt_id = MethodField("get_receipt_id")

    def get_receipt_id(self, obj: dict):
        return obj.get("receipt_id", "")

class ClientInfoWithAccountsSerializer(ClientInfoSerializer):
    # # monotoken = StrField()
    # client_id = StrField("clientId")
    # name = StrField()
    accounts = AccountSerializer(many=True)
    jars = JarSerializer(many=True)
