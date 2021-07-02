import sqlite3
from types import new_class
import petl

conn = sqlite3.connect("rasa.db")


print("connected")


class Repo:
    table = petl.empty()

    @staticmethod
    def initDb():
        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            employee_code TEXT UNIQUE NOT NULL,
            number INTEGER NOT NULL,
            email TEXT UNIQUE NOT NULL
        );
    """
        )

        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS nomination_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER UNIQUE NOT NULL,
            justification TEXT NOT NULL,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        );
        """
        )
        conn.commit()

    @staticmethod
    def insertCandidate(name, emp_code, number, email):
        conn.execute(
            """
      INSERT INTO candidates (NAME, EMPLOYEE_CODE, NUMBER, EMAIL) VALUES (?, ?, ?, ?);
    """,
            (name, emp_code, number, email),
        )
        conn.commit()

    @staticmethod
    def insertNominee(name, justification):
        name += "%"
        cur = conn.cursor()
        cur.execute("""SELECT * FROM candidates WHERE name like ?""", (name,))
        rows = cur.fetchall()
        candidate = rows[0]
        conn.execute(
            """
      INSERT INTO nomination_table (justification, candidate_id) VALUES (?, ?);
    """,
            (justification, candidate[0]),
        )
        conn.commit()

    @staticmethod
    def select():
        Repo.table = petl.fromdb(conn, "SELECT * from candidates")
        return str(Repo.table)

    @staticmethod
    def selectNominees():
        nominee_table = petl.fromdb(
            conn,
            "SELECT c.id, c.name, c.employee_code, c.number, c.email, n.justification from nomination_table n join candidates c ON c.id = n.candidate_id",
        )
        return str(nominee_table)

    @staticmethod
    def delete(value):

        name = value + "%"
        cur = conn.cursor()

        cur.execute(
            """
      SELECT * FROM candidates WHERE name like ? OR employee_code like ?
    """,
            (name, value,),
        )

        rows = cur.fetchall()

        if len(rows) == 0:
            return False

        conn.execute(
            """
      DELETE FROM candidates WHERE name like ? OR employee_code like ?
    """,
            (name, value,),
        )
        conn.commit()

        return True

    @staticmethod
    def rename_column(name, new_name):
        new_table = petl.rename(Repo.table, name, new_name)
        Repo.table = new_table
        # petl.todb(new_table, conn, "candidates")
        return str(new_table)

    @staticmethod
    def remove_column(name):
        new_table = petl.cutout(Repo.table, name)
        Repo.table = new_table
        return str(new_table)

    @staticmethod
    def exists(nominee_name):
        nominee_name += "%"
        cur = conn.cursor()
        cur.execute("""SELECT * FROM candidates WHERE name like ?""", (nominee_name,))

        rows = cur.fetchall()

        if len(rows) > 0:
            return True

        return False
