from time import sleep

import psycopg2


while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres',
                                password='THEspecial4343', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print(">>> Database connectio successfull!")
        break
    except Exception as error:
        print("Connecting to Database failed!")
        print("Erorr>>>", error)
        sleep(2)

posts = [{
    "id": 1, "title": "Sample title", "content": "This is a content", "rating": 3, "published": False
}]

# factory = Factory(conn, cursor)


class Factory:

    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor

    def get_all(self, table: str, **args):
        self.cursor.execute(f"SELECT * FROM {table};")
        data = self.cursor.fetchall()
        return data

    def get_one(self, table: str, id: int):
        self.cursor.execute(f"SELECT * FROM {table} WHERE id={id};")
        data = self.cursor.fetchone()
        return data

    def delete_one(self, table: str, id: int):
        self.cursor.execute(
            f"DELETE * FROM {table} WHERE id={id} RETURNING *;")
        deleted = self.cursor.fetchone()
        return deleted

    def update_one(self, table: str, id: int, data: dict):
        sets = ""
        for key, val in data.items():
            sets += f"{key}='{val}', " if isinstance(
                val, str) else f"{key}={str(val)}, "
        sets = sets.strip(", ")
        self.cursor.execute(
            f"UPDATE {table} SET {sets} WHERE id={id} RETURNING *;")
        updated = self.cursor.fetchone()
        self.conn.commit()
        return updated

    def create_one(self, table: str, data: dict):
        if "id" in data:
            del data["id"]

        keys = "("
        values = "("
        for key, val in data.items():
            keys += f"{key}, "
            if isinstance(val, str):
                values += f"'{val}', "
            else:
                values += f"{str(val)}, "
        keys = keys.strip(", ") + ")"
        values = values.strip(", ") + ")"
        self.cursor.execute(
            f"INSERT INTO {table}{keys} VALUES {values} RETURNING *;")
        new_doc = self.cursor.fetchone()
        self.conn.commit()
        return new_doc
