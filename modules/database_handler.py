from sqlalchemy import create_engine, text
from config.config import DB_URI


def get_engine():
    return create_engine(DB_URI)


def execute_sql_script(engine, script_path):
    """
    Method to execute a *.sql script.
    """
    with engine.connect() as connection:
        with open(script_path, "r") as file:
            script = file.read()
            statements = script.split(
                ";"
            )  # Split the script into individual statements
            for statement in statements:
                if statement.strip():  # Ensure statement is not empty
                    connection.execute(text(statement))


def create_tables():
    """
    Method to create the required tables.
    """
    engine = get_engine()
    execute_sql_script(engine, "sql/create_tables.sql")
