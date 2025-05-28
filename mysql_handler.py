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
        self.database.close()
        self.cursor.close()
        self.cursor = None
        self.database = None

    def run_query(self, query: str) -> None:
        self.cursor.execute(query)

    def fetch_query_data(self, limit=1):
        return self.cursor.fetchmany(size=limit)
