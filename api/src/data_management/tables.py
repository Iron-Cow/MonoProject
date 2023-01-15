import sqlalchemy as db
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import insert
from .config import CURRENCIES, CATEGORIES, CATEGORIES_MSO

from data_management.engine import DBManager

db_manager = DBManager()

metadata = db.MetaData()
USER_TABLE_NAME = "users"
CURRENCY_TABLE_NAME = "currencies"
CATEGORIES_TABLE_NAME = "categories"
CATEGORIES_MSO_TABLE_NAME = "categories_mso"
MONOBANK_ACCOUNT_TABLE_NAME = "monobank_accounts"
MONOBANK_CARD_TABLE_NAME = "monobank_cards"
MONOBANK_JAR_TABLE_NAME = "monobank_jars"
MONOBANK_TRANSACTION_TABLE_NAME = "monobank_transactions"

Users = db.Table(
    USER_TABLE_NAME, metadata,
    db.Column('id', db.Integer(), primary_key=True),
    db.Column('tg_id', db.String(255), nullable=False, index=True, unique=True),
    db.Column('is_superuser', db.Boolean(), default=False, nullable=False),
    db.Column('is_admin', db.Boolean(), default=False, nullable=False),
)

Currencies = db.Table(
    CURRENCY_TABLE_NAME, metadata,
    db.Column('code', db.Integer, nullable=False, unique=True,primary_key=True),
    db.Column('name', db.String(16), index=True, unique=True),
    db.Column('flag', db.String(16), unique=False),
    db.Column('symbol', db.String(16), unique=False),
)

Categories = db.Table(
    CATEGORIES_TABLE_NAME, metadata,
    db.Column('id', db.Integer(), primary_key=True),
    db.Column('name', db.String(255), unique=False),
    db.Column('symbol', db.String(16), unique=False),
)

Categories_MSO = db.Table(
    CATEGORIES_MSO_TABLE_NAME, metadata,
    db.Column('id', db.Integer(), primary_key=True),
    db.Column('mso', db.Integer(), unique=True),
    db.Column('category', db.Integer(), ForeignKey(f"{Categories.name}.id")),
)

Monobank_Account = db.Table(
    MONOBANK_ACCOUNT_TABLE_NAME, metadata,
    db.Column('id', db.Integer(), primary_key=True),
    db.Column('client_id', db.String(255), unique=True, nullable=False),
    db.Column('monotoken', db.String(255), unique=True),
    db.Column('web_hook_url', db.String(255)),
    db.Column('name', db.String(255)),
    db.Column('tg_id', db.String(255)),

)

Monobank_Card = db.Table(
    MONOBANK_CARD_TABLE_NAME, metadata,
    db.Column('account_id', db.String(255), unique=True, nullable=False, primary_key=True),
    db.Column('send_id', db.String(255)),
    db.Column('currency_code', ForeignKey(f"{Currencies.name}.code")),
    db.Column('balance', db.Integer()),
    db.Column('cashback_type', db.String(255)),
    db.Column('credit_limit', db.Integer()),
    db.Column('type', db.String(255)),
    db.Column('iban', db.String(255)),
)

Monobank_Jar = db.Table(
    MONOBANK_JAR_TABLE_NAME, metadata,
    db.Column('jar_id', db.String(255), unique=True, nullable=False, primary_key=True),
    db.Column('send_id', db.String(255)),
    db.Column('title', db.String(255)),
    db.Column('currency_code', db.Integer(),  ForeignKey(f"{Currencies.name}.code")),
    db.Column('balance', db.Integer()),
    db.Column('description', db.Text()),
    db.Column('goal', db.Integer()),
)

Monobank_Transaction = db.Table(
    MONOBANK_TRANSACTION_TABLE_NAME, metadata,
    db.Column('id', db.String(255), unique=True, nullable=False, primary_key=True),
    db.Column('time', db.Integer()),
    db.Column('description', db.Text()),
    db.Column('mcc', db.Integer()),
    db.Column('original_mcc', db.Integer()),
    db.Column('amount', db.Integer()),
    db.Column('operation_amount', db.Integer()),
    db.Column('currency_code', db.Integer(), ForeignKey(f"{Currencies.name}.code")),
    db.Column('commission_rate', db.Integer()),
    db.Column('cashback_amount', db.Integer()),
    db.Column('balance', db.Integer()),
    db.Column('hold', db.Boolean()),
    db.Column('receipt_id', db.String(255)),
    db.Column('account_type', db.String(255)),
    db.Column('account_id', db.String(255)),

)

# Create empty tables on first run
metadata.create_all(db_manager.engine)


def fill_table_with_default_values(table: db.Table, values: list[dict], ):
    query = insert(table).values(values).on_conflict_do_nothing()
    db_manager.execute_dml_query(query)




# Create default values on first launch
fill_table_with_default_values(Currencies, CURRENCIES)
fill_table_with_default_values(Categories, CATEGORIES)
fill_table_with_default_values(Categories_MSO, CATEGORIES_MSO)
