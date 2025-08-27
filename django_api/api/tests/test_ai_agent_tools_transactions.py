from datetime import datetime, timezone

import pytest
from ai_agent.tools.monotransations import get_daily_mono_transactions
from django.contrib.auth import get_user_model
from monobank.models import MonoAccount, MonoCard, MonoTransaction

User = get_user_model()


@pytest.mark.django_db
def test_get_daily_mono_transactions_filters_by_tg_id_and_family(
    pre_created_user,
    pre_created_mono_account,
    pre_created_currency,
    pre_created_categories_mso,
    pre_created_mono_card,
    pre_created_family_for_precreated_user,
):
    # Prepare a specific day and timestamps
    day = "2025-01-02"
    ts = int(datetime(2025, 1, 2, 12, 0, tzinfo=timezone.utc).timestamp())

    # Ensure pre_created_user has at least one card (provided by pre_created_mono_card)
    user_card = pre_created_mono_card[0]

    # Create a transaction for the main user on that day
    MonoTransaction.objects.create(
        id="user_tx_1",
        time=ts,
        description="user spend",
        mcc=pre_created_categories_mso[0],
        amount=-1000,
        commission_rate=0,
        currency=pre_created_currency,
        balance=10000,
        hold=True,
        receipt_id="",
        account=user_card,
        cashback_amount=0,
        comment="",
    )

    # Family member was created and linked by fixture; fetch existing account and create a card
    family_user = pre_created_family_for_precreated_user
    fam_account = MonoAccount.objects.get(user=family_user)
    fam_card = MonoCard.objects.create(
        monoaccount=fam_account,
        id="fam_card_1",
        send_id="fam_send",
        currency=pre_created_currency,
        cashback_type="cashback",
        balance=100,
        credit_limit=0,
        masked_pan=["masked"],
        type="white",
        iban="fam_iban",
    )

    MonoTransaction.objects.create(
        id="fam_tx_1",
        time=ts,
        description="family spend",
        mcc=pre_created_categories_mso[0],
        amount=-2000,
        commission_rate=0,
        currency=pre_created_currency,
        balance=10000,
        hold=True,
        receipt_id="",
        account=fam_card,
        cashback_amount=0,
        comment="",
    )

    # When include_family=True, both user's and family member's tx should be returned
    result_with_family = get_daily_mono_transactions(
        day=day, tg_id=pre_created_user.tg_id, include_family=True
    )
    descs_with_family = {item["description"] for item in result_with_family}
    assert "user spend" in descs_with_family
    assert "family spend" in descs_with_family

    # When include_family=False, only user's tx should be returned
    result_without_family = get_daily_mono_transactions(
        day=day, tg_id=pre_created_user.tg_id, include_family=False
    )
    descs_without_family = {item["description"] for item in result_without_family}
    assert "user spend" in descs_without_family
    assert "family spend" not in descs_without_family
