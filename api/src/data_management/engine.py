import sqlalchemy as db
from sqlalchemy.sql.dml import UpdateBase
from sqlalchemy.sql.selectable import Select
from .config import config


class DBManager:
    SQLALCHEMY_DATABASE_URL = f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:5432/{config.DB_NAME}"

    def __init__(self):
        self.engine = db.create_engine(
            self.SQLALCHEMY_DATABASE_URL
        )

    def get_connection(self):
        return self.engine.connect()

    def execute_dml_query(self, query: UpdateBase):
        with self.get_connection() as connection:
            connection.execute(query)

    def execute_select_query(self, query: Select) -> list[dict]:
        with self.get_connection() as connection:
            result = connection.execute(query).fetchall()
            return [dict(i) for i in result]
