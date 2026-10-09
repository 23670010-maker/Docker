import os

import pymysql
from werkzeug.security import generate_password_hash


def conexion():
    return pymysql.connect(
        host="mysql",
        user="minierp_user",
        password="minierp123",
        database="minierp",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )


ADMIN_PASSWORD = os.environ["DEMO_ADMIN_PASSWORD"]

CONSULTA_PASSWORD = os.environ["DEMO_CONSULTA_PASSWORD"]


usuarios = [
    (
        "admin",
        generate_password_hash(ADMIN_PASSWORD),
        "admin"
    ),
    (
        "consulta",
        generate_password_hash(CONSULTA_PASSWORD),
        "consulta"
    )
]


con = conexion()

try:

    with con.cursor() as cur:

        for username, password_hash, rol in usuarios:

            cur.execute(
                """
                INSERT INTO usuarios
                    (username, password_hash, rol)
                VALUES
                    (%s, %s, %s)

                ON DUPLICATE KEY UPDATE
                    password_hash = %s,
                    rol = %s,
                    activo = TRUE
                """,
                (
                    username,
                    password_hash,
                    rol,
                    password_hash,
                    rol
                )
            )

    con.commit()

    print("Usuarios de laboratorio configurados.")

finally:
    con.close()
