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

Users = db.Table(
    USER_TABLE_NAME, metadata,
    db.Column('id', db.Integer(), primary_key=True),
    db.Column('tg_id', db.String(255), nullable=False, index=True, unique=True),
    db.Column('is_superuser', db.Boolean(), default=False, nullable=False),
    db.Column('is_admin', db.Boolean(), default=False, nullable=False),
)

Currencies = db.Table(
    CURRENCY_TABLE_NAME, metadata,
    db.Column('id', db.Integer(), primary_key=True),
    db.Column('code', db.Integer, nullable=False, index=True, unique=True),
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

# Create empty tables on first run
metadata.create_all(db_manager.engine)

def fill_table_with_default_values(table: db.Table, values: list[dict], ):
    query = insert(table).values(values).on_conflict_do_nothing()
    db_manager.execute_dml_query(query)


# Create default values on first launch
fill_table_with_default_values(Currencies, CURRENCIES)
fill_table_with_default_values(Categories, CATEGORIES)
fill_table_with_default_values(Categories_MSO, CATEGORIES_MSO)
