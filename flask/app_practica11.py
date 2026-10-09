from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import os

from functools import wraps
from datetime import timedelta

from flask_jwt_extended import(
    JWTManager,
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required
)

from werkzeug.security import check_password_hash

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
    minutes=30
)

jwt = JWTManager(app)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "http://localhost:4200"
        }
    },
   allow_headers=[
        "Content-Type",
        "Authorization"
    ]
)


def rol_requerido(*roles):

    def decorador(funcion):

        @wraps(funcion)

        @jwt_required()
        def envoltura(*args, **kwargs):

            claims = get_jwt()

            rol_actual = claims.get("rol")

            if rol_actual not in roles:

                return jsonify({
                    "error":
                    "Permisos insuficientes"
                }), 403

            return funcion(*args, **kwargs)

        return envoltura

    return decorador


def conexion():
    return pymysql.connect(
        host="mysql",
        user="minierp_user",
        password="minierp123",
        database="minierp",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )


@app.get("/")
def inicio():
    return jsonify({
        "mensaje": "API Flask funcionando Correctamente"
    })


@app.get("/api/alumnos")
@jwt_required()
def listar_alumnos():
    con = conexion()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT * FROM alumnos")
            alumnos = cur.fetchall()

        return jsonify(alumnos)

    finally:
        con.close()


@app.get("/api/alumnos/<int:id>")
@jwt_required()
def obtener_alumno(id):
    con = conexion()
    try:
        with con.cursor() as cur:
            cur.execute(
                "SELECT * FROM alumnos WHERE id=%s",
                (id,)
            )
            alumno = cur.fetchone()

            if not alumno:
                return jsonify({
                    "error": "Alumno no encontrado"
                }), 404

            return jsonify(alumno)

    finally:
        con.close()


@app.post("/api/alumnos")
@rol_requerido("admin", "captura")
def crear_alumno():
    datos = request.get_json()

    campos = [
        "Nctrl",
        "nombre",
        "promedio",
        "carrera",
        "semestre",
        "sexo"
    ]

    if not datos or not all(campo in datos for campo in campos):
        return jsonify({
            "error": "Faltan campos obligatorios"
        }), 400

    con = conexion()

    try:
        with con.cursor() as cur:
            sql = """INSERT INTO alumnos
            (Nctrl, nombre, promedio, carrera, semestre, sexo)
            VALUES (%s, %s, %s, %s, %s, %s)"""

            valores = tuple(datos[campo] for campo in campos)

            cur.execute(sql, valores)
            con.commit()

            return jsonify({
                "mensaje": "Alumno creado",
                "id": cur.lastrowid
            }), 201

    finally:
        con.close()


@app.put("/api/alumnos/<int:id>")
@rol_requerido("admin")
def actualizar_alumno(id):
    datos = request.get_json()

    campos = [
        "Nctrl",
        "nombre",
        "promedio",
        "carrera",
        "semestre",
        "sexo"
    ]

    if not datos or not all(campo in datos for campo in campos):
        return jsonify({
            "error": "Faltan campos obligatorios"
        }), 400

    con = conexion()

    try:
        with con.cursor() as cur:
            sql = """UPDATE alumnos
            SET Nctrl=%s,
                nombre=%s,
                promedio=%s,
                carrera=%s,
                semestre=%s,
                sexo=%s
            WHERE id=%s"""

            valores = (
                datos["Nctrl"],
                datos["nombre"],
                datos["promedio"],
                datos["carrera"],
                datos["semestre"],
                datos["sexo"],
                id
            )

            cur.execute(sql, valores)
            con.commit()

            if cur.rowcount == 0:
                return jsonify({
                    "error": "Alumno no encontrado"
                }), 404

            return jsonify({
                "mensaje": "Alumno actualizado"
            })

    finally:
        con.close()


@app.delete("/api/alumnos/<int:id>")
@rol_requerido("admin")
def eliminar_alumno(id):
    con = conexion()

    try:
        with con.cursor() as cur:
            cur.execute(
                "DELETE FROM alumnos WHERE id=%s",
                (id,)
            )

            con.commit()

            if cur.rowcount == 0:
                return jsonify({
                    "error": "Alumno no encontrado"
                }), 404

            return jsonify({
                "mensaje": "Alumno eliminado"
            })

    finally:
        con.close()


@app.get("/api/alumnos/carrera/<nombre>")
def alumnos_por_carrera(nombre):

    con = conexion()

    try:
        with con.cursor() as cur:

            cur.execute(
                "SELECT * FROM alumnos WHERE carrera = %s",
                (nombre,)
            )

            alumnos = cur.fetchall()

        return jsonify(alumnos)

    finally:
        con.close()


@app.get("/api/alumnos/promedio/<float:valor>")
def alumnos_por_promedio(valor):

    con = conexion()

    try:
        with con.cursor() as cur:

            cur.execute(
                "SELECT * FROM alumnos WHERE promedio >= %s",
                (valor,)
            )

            alumnos = cur.fetchall()

        return jsonify(alumnos)

    finally:
        con.close()


@app.post("/api/auth/login")
def login():

    datos = request.get_json(silent=True) or {}

    username = datos.get("username", "").strip()

    password = datos.get("password", "")

    if not username or not password:

        return jsonify({
            "error":
            "Usuario y contraseña son obligatorios"
        }), 400


    con = conexion()

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    username,
                    password_hash,
                    rol
                FROM usuarios
                WHERE username=%s
                  AND activo=TRUE
                """,
                (username,)
            )

            usuario = cur.fetchone()


        if not usuario:

            return jsonify({
                "error":
                "Credenciales incorrectas"
            }), 401


        if not check_password_hash(
            usuario["password_hash"],
            password
        ):

            return jsonify({
                "error":
                "Credenciales incorrectas"
            }), 401


        token = create_access_token(
            identity=str(usuario["id"]),

            additional_claims={
                "username":
                    usuario["username"],

                "rol":
                    usuario["rol"]
            }
        )


        return jsonify({

            "access_token":
                token,

            "usuario":
                usuario["username"],

            "rol":
                usuario["rol"]

        }), 200


    finally:

        con.close()


@app.get("/api/auth/me")
@jwt_required()
def me():

    claims = get_jwt()

    return jsonify({

        "id":
            get_jwt_identity(),

        "username":
            claims.get("username"),

        "rol":
            claims.get("rol")

    })



if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
