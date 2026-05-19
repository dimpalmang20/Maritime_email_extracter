import sqlite3


def create_database():

    conn = sqlite3.connect("maritime.db")

    cursor = conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS maritime_records (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        cargo TEXT,

        cargo_type TEXT,

        load_port TEXT,

        discharge_port TEXT,

        quantity INTEGER,

        dwt TEXT,

        vessel_type TEXT,

        laycan TEXT,

        confidence_score REAL,

        extraction_status TEXT
    )

    """)

    conn.commit()

    conn.close()


def save_record(data):

    conn = sqlite3.connect("maritime.db")

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO maritime_records (

        cargo,
        cargo_type,
        load_port,
        discharge_port,
        quantity,
        dwt,
        vessel_type,
        laycan,
        confidence_score,
        extraction_status

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        data.get("cargo"),

        data.get("cargo_type"),

        data.get("load_port"),

        data.get("discharge_port"),

        data.get("quantity"),

        str(data.get("dwt")),

        data.get("vessel_type"),

        str(data.get("laycan")),

        data.get("confidence_score"),

        data.get("extraction_status")
    ))

    conn.commit()

    conn.close()

def search_by_cargo(cargo_name):

    conn = sqlite3.connect("maritime.db")

    cursor = conn.cursor()

    cursor.execute("""

    SELECT * FROM maritime_records
    WHERE cargo LIKE ?

    """, (f"%{cargo_name}%", ))

    results = cursor.fetchall()

    conn.close()

    return results

def search_by_vessel(vessel_type):

    conn = sqlite3.connect("maritime.db")

    cursor = conn.cursor()

    cursor.execute("""

    SELECT * FROM maritime_records
    WHERE vessel_type LIKE ?

    """, (f"%{vessel_type}%", ))

    results = cursor.fetchall()

    conn.close()

    return results

def get_all_records():

    conn = sqlite3.connect("maritime.db")

    cursor = conn.cursor()

    cursor.execute("""

    SELECT * FROM maritime_records

    """)

    results = cursor.fetchall()

    conn.close()

    return results

def search_by_port(port_name):

    conn = sqlite3.connect("maritime.db")

    cursor = conn.cursor()

    cursor.execute("""

    SELECT * FROM maritime_records
    WHERE load_port LIKE ?
    OR discharge_port LIKE ?

    """, (

        f"%{port_name}%",

        f"%{port_name}%"
    ))

    results = cursor.fetchall()

    conn.close()

    return results