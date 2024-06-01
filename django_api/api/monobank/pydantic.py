from typing import Union

from pydantic import BaseModel, field_validator, model_validator

from .models import CategoryMSO, Currency, MonoCard, MonoDataNotFound, MonoJar


class TransactionItem(BaseModel):
    amount: int
    balance: int
    cashback_amount: int
    commission_rate: int
    currency: Currency | int = 0
    description: str
    hold: bool
    id: str
    mcc: CategoryMSO
    operation_amount: int
    original_mcc: int
    time: int
    comment: str | None = None
    receipt_id: str | None = None

    @model_validator(mode="before")
    def set_currency(cls, values):
        currency_code = values.get("currency_code")
        if not currency_code:
            return values
        if not values.get("currency"):
            if Currency.objects.filter(code=currency_code).exists():
                values["currency"] = Currency.objects.get(code=currency_code)
            else:
                values[
                    "currency"
                ] = currency_code  # Note: trigger to generate or log not existed currency code
        return values

    @field_validator("currency", mode="before")
    def transform_currency(cls, value) -> CategoryMSO:
        if isinstance(value, int) or not value:
            raise MonoDataNotFound(
                f"Unknown currency code: {value}"
            )  # TODO: generate currency in case of new currency
        return value

    @field_validator("mcc", mode="before")
    def transform_mcc(cls, value) -> CategoryMSO:
        if CategoryMSO.objects.filter(mso=value).exists():
            return CategoryMSO.objects.get(mso=value)
        raise MonoDataNotFound(
            f"Unknown mso code: {value}"
        )  # TODO: generate new MSO on the fly instead of error

    class Config:
        arbitrary_types_allowed = True


class TransactionData(BaseModel):
    account: Union[MonoCard, MonoJar]
    statement_item: TransactionItem

    # statement_type: Optional[str] = Field(..., alias="type", )  # Use alias for `type`

    @field_validator("account", mode="before")
    def transform_account(cls, value) -> Union[MonoCard, MonoJar]:
        if MonoCard.objects.filter(id=value).exists():
            return MonoCard.objects.get(id=value)
        elif MonoJar.objects.filter(id=value).exists():
            return MonoJar.objects.get(id=value)
        raise MonoDataNotFound(f"Invalid account ID: {value}")

    class Config:
        arbitrary_types_allowed = True
