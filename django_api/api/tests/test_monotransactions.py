import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from monobank.models import MonoCard, MonoTransaction

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.usefixtures("pre_created_mono_card")
def test_create_transaction_from_webhook(pre_created_mono_card):
    user = User.objects.create_user("test_user", "test_password")

    monocard = MonoCard.objects.get(id="pre_created_id2")
    transaction_data = {
        "id": "FUTockmzmwvnuCL0",
        "time": 1665250419,
        "description": "Укрпошта",
        "mcc": 5999,
        "originalMcc": 5999,
        "amount": -18200,
        "operationAmount": -18200,
        "currencyCode": 980,
        "commissionRate": 0,
        "cashbackAmount": 0,
        "balance": 6961482,
        "hold": True,
        "receiptId": "T6X3-2ET0-CKT0-EBP1",
    }

    # Call the task function directly
    MonoTransaction.create_transaction_from_webhook(  # type: ignore
        monocard.id,  # Pass the account ID
        transaction_data,
    )

    # Retrieve the created transaction from the database
    try:
        mono_transaction = MonoTransaction.objects.get(id=transaction_data["id"])
        assert mono_transaction.id == transaction_data["id"]
        assert mono_transaction.time == transaction_data["time"]
        assert mono_transaction.description == transaction_data["description"]
        # Add assertions for other fields
    except ObjectDoesNotExist:
        pytest.fail("Transaction was not created")
