import mysql.connector


class MySqlHandler:

    def __init__(self, credentials, connector=mysql.connector):
        self._connector = connector
        self.credentials = credentials
        self.database = None
        self.cursor = None

    def connect_to_database(self) -> None:
        self.database = self._connector.connect(**self.credentials)
        self.cursor = self.database.cursor()

    def disconnect_from_database(self) -> None:
        self.cursor.close()
        self.database.close()
        self.cursor = None
        self.database = None

    def run_query(self, query: str, limit=1) -> list[tuple]:
        self.cursor.execute(query)
        return self.cursor.fetchsome(size=limit)
