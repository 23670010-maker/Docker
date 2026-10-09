from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import os
import json
import redis
import socket

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


APP_INSTANCE = os.getenv(
    "APP_INSTANCE",
    "flask-dev"
)


app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
    minutes=30
)

jwt = JWTManager(app)


redis_client = redis.Redis(

    host=os.getenv(
        "REDIS_HOST",
        "redis"
    ),

    port=int(
        os.getenv(
            "REDIS_PORT",
            "6379"
        )
    ),

    decode_responses=True,

    socket_connect_timeout=2,

    socket_timeout=2

)

CACHE_TTL = 60


CACHE_MATERIAS = "minierp:materias:activas"
CACHE_CALIFICACIONES ="minierp:calificaciones:todas"
CACHE_CALIFICACIONES_ALUMNO ="minierp:calificaciones:alumno:"
CACHE_ALUMNOS = "minierp:alumnos"


def normalizar_calificaciones(datos):

    for fila in datos:

        if "calificacion" in fila:

            fila["calificacion"] = float(
                fila["calificacion"]
            )

    return datos



def cache_obtener(clave):

    try:

        valor = redis_client.get(clave)

        if valor is None:
            return None

        return json.loads(valor)

    except redis.RedisError as e:

        app.logger.warning(
            f"Redis no disponible: {e}"
        )

        return None


def cache_guardar(
    clave,
    datos,
    ttl=CACHE_TTL
):

    try:

        redis_client.setex(

            clave,

            ttl,

            json.dumps(
                datos,
                default=float
            )

        )

    except redis.RedisError as e:

        app.logger.warning(
            f"No fue posible guardar en Redis: {e}"
        )


def cache_eliminar(*claves):

    try:

        redis_client.delete(
            *claves
        )

    except redis.RedisError as e:

        app.logger.warning(
            f"No fue posible eliminar caché: {e}"
        )



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

        host=os.getenv(
            "DB_HOST",
            "mysql"
        ),

        user=os.getenv(
            "DB_USER",
            "minierp_user"
        ),

        password=os.getenv(
            "DB_PASSWORD",
            "minierp123"
        ),

        database=os.getenv(
            "DB_NAME",
            "minierp"
        ),

        port=int(
            os.getenv(
                "DB_PORT",
                "3306"
            )
        ),

        cursorclass=
            pymysql.cursors.DictCursor
    )

@app.get("/")
def inicio():
    return jsonify({
        "mensaje": "API Flask funcionando Correctamente"
    })


@app.get("/api/alumnos")
@jwt_required()
def listar_alumnos():

    clave = CACHE_ALUMNOS

    datos_cache = cache_obtener(clave)

    if datos_cache is not None:

        app.logger.info(
            "CACHE HIT: alumnos"
        )

        return jsonify(datos_cache)

    app.logger.info(
        "CACHE MISS: alumnos"
    )

    con = conexion()

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                SELECT *
                FROM alumnos
                ORDER BY nombre
                """
            )

            datos = cur.fetchall()

            cache_guardar(
                clave,
                datos
            )

            return jsonify(datos)

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

            cache_eliminar(
               CACHE_ALUMNOS
            )

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

            cache_eliminar(
               CACHE_ALUMNOS
            )

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

            cache_eliminar(
                CACHE_ALUMNOS
            )

            if cur.rowcount == 0:
                return jsonify({
                    "error": "Alumno no encontrado"
                }), 404

            return jsonify({
                "mensaje": "Alumno eliminado"
            })

    finally:
        con.close()


@app.delete("/api/materias/<int:id>")
@rol_requerido("admin")
def eliminar_materia(id):

    con = conexion()

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                UPDATE materias
                SET activo = FALSE
                WHERE id=%s
                """,
                (id,)
            )

            con.commit()
            cache_eliminar(
                CACHE_MATERIAS,
                CACHE_CALIFICACIONES
            )

            if cur.rowcount == 0:

                return jsonify({
                    "error":
                    "Materia no encontrada"
                }), 404

            return jsonify({
                "mensaje":
                "Materia desactivada"
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



@app.post("/api/materias")
@rol_requerido("admin")
def crear_materia():

    datos = request.get_json(
        silent=True
    ) or {}

    campos = [
        "clave",
        "nombre",
        "semestre",
        "creditos"
    ]

    if not all(
        campo in datos
        for campo in campos
    ):

        return jsonify({
            "error":
            "Faltan campos obligatorios"
        }), 400

    con = conexion()

    try:

        with con.cursor() as cur:

            sql = """
            INSERT INTO materias
            (
                clave,
                nombre,
                semestre,
                creditos
            )
            VALUES
            (%s, %s, %s, %s)
            """

            cur.execute(
                sql,
                (
                    datos["clave"],
                    datos["nombre"],
                    datos["semestre"],
                    datos["creditos"]
                )
            )

            con.commit()

            cache_eliminar(
               CACHE_MATERIAS,
               CACHE_CALIFICACIONES
            )

            return jsonify({

                "mensaje":
                    "Materia creada",

                "id":
                    cur.lastrowid

            }), 201

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


@app.put("/api/materias/<int:id>")
@rol_requerido("admin")
def actualizar_materia(id):

    datos = request.get_json(
        silent=True
    ) or {}

    con = conexion()

    try:
       with con.cursor() as cur:

            cur.execute(
                """
                UPDATE materias
                SET
                    clave=%s,
                    nombre=%s,
                    semestre=%s,
                    creditos=%s
                WHERE id=%s
                """,
                (
                    datos["clave"],
                    datos["nombre"],
                    datos["semestre"],
                    datos["creditos"],
                    id
                )
            )

            con.commit()

            cache_eliminar(
               CACHE_MATERIAS,
               CACHE_CALIFICACIONES
            )

            if cur.rowcount == 0:

               return jsonify({
                   "error":
                   "Materia no encontrada"
               }), 404

            return jsonify({
               "mensaje":
               "Materia actualizada"
            })

    finally:

       con.close()

@app.get("/api/calificaciones")
@jwt_required()
def listar_calificaciones():

    clave = CACHE_CALIFICACIONES

    datos_cache = cache_obtener(clave)

    if datos_cache is not None:

        app.logger.info(
            "CACHE HIT: calificaciones"
        )

        return jsonify(datos_cache)

    app.logger.info(
        "CACHE MISS: calificaciones"
    )

    con = conexion()

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                SELECT
                    c.id,
                    a.id AS alumno_id,
                    a.Nctrl,
                    a.nombre AS alumno,
                    m.id AS materia_id,
                    m.clave,
                    m.nombre AS materia,
                    c.periodo,
                    c.calificacion

                FROM calificaciones c

                INNER JOIN alumnos a
                    ON c.alumno_id = a.id

                INNER JOIN materias m
                    ON c.materia_id = m.id

                ORDER BY
                    a.nombre,
                    m.nombre
                """
            )

            datos = cur.fetchall()

            datos = normalizar_calificaciones(
                datos
            )

            cache_guardar(
                clave,
                datos
            )

            return jsonify(datos)

    finally:

        con.close()



@app.get("/api/calificaciones/alumno/<int:id>")
@jwt_required()
def calificaciones_alumno(id):

    clave = (
        f"minierp:calificaciones:alumno:{id}"
    )

    datos_cache = cache_obtener(clave)

    if datos_cache is not None:

        app.logger.info(
            f"CACHE HIT: alumno {id}"
        )

        return jsonify(datos_cache)

    app.logger.info(
        f"CACHE MISS: alumno {id}"
    )

    con = conexion()

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                SELECT
                    c.id,
                    m.id AS materia_id,
                    m.clave,
                    m.nombre AS materia,
                    c.periodo,
                    c.calificacion

                FROM calificaciones c

                INNER JOIN materias m
                    ON c.materia_id = m.id

                WHERE c.alumno_id=%s

                ORDER BY
                    c.periodo DESC,
                    m.nombre
                """,
                (id,)
            )

            datos = cur.fetchall()

            datos = normalizar_calificaciones(
                datos
            )

            cache_guardar(
                clave,
                datos
            )

            return jsonify(datos)

    finally:

        con.close()



@app.put("/api/calificaciones/<int:id>")
@rol_requerido("admin")
def actualizar_calificacion(id):

    datos = request.get_json(
        silent=True
    ) or {}

    calificacion = float(
        datos["calificacion"]
    )

    if not (
        0 <= calificacion <= 10
    ):

        return jsonify({
            "error":
            "La calificación debe estar entre 0 y 10"
        }), 400

    con = conexion()

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                UPDATE calificaciones

                SET
                    alumno_id=%s,
                    materia_id=%s,
                    periodo=%s,
                    calificacion=%s

                WHERE id=%s
                """,
                (
                    datos["alumno_id"],
                    datos["materia_id"],
                    datos["periodo"],
                    calificacion,
                    id
                )
            )

            con.commit()
            cache_eliminar(
               CACHE_CALIFICACIONES
            )

            cache_eliminar(
                f"minierp:calificaciones:alumno:{datos['alumno_id']}"
            )

            if cur.rowcount == 0:

                return jsonify({
                    "error":
                    "Calificación no encontrada"
                }), 404

            return jsonify({
                "mensaje":
                "Calificación actualizada"
            })

    finally:

        con.close()


@app.delete("/api/calificaciones/<int:id>")
@rol_requerido("admin")
def eliminar_calificacion(id):

    con = conexion()

    try:

      with con.cursor() as cur:

           cur.execute(
               """
               SELECT alumno_id
               FROM calificaciones
               WHERE id=%s
               """,
               (id,)
           )

           registro = cur.fetchone()

           if not registro:

              return jsonify({
                 "error":
                 "Calificación no encontrada"
              }), 404

           alumno_id = registro["alumno_id"]

           cur.execute(
               """
               DELETE FROM calificaciones
               WHERE id=%s
               """,
               (id,)
           )

           con.commit()

           cache_eliminar(
               CACHE_CALIFICACIONES,
               f"minierp:calificaciones:alumno:{alumno_id}"
           )

           return jsonify({
              "mensaje":
              "Calificación eliminada"
           })


    finally:

        con.close()


@app.get("/api/materias")
@jwt_required()
def listar_materias():
    clave = CACHE_MATERIAS
    datos_cache = cache_obtener(clave)
    if datos_cache is not None:

        app.logger.info(
            "CACHE HIT: materias"
        )

        return jsonify(datos_cache)

    app.logger.info(
        "CACHE MISS: materias"
    )

    con = conexion()

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    clave,
                    nombre,
                    semestre,
                    creditos,
                    activo
                FROM materias
                WHERE activo = TRUE
                ORDER BY semestre, nombre
                """
            )

            datos = cur.fetchall()

            cache_guardar(
                clave,
                datos
            )

            return jsonify(datos)
    finally:
        con.close()



@app.post("/api/calificaciones")
@rol_requerido("admin")
def crear_calificacion():

    datos = request.get_json(
        silent=True
    ) or {}

    campos = [
        "alumno_id",
        "materia_id",
        "periodo",
        "calificacion"
    ]

    if not all(
        campo in datos
        for campo in campos
    ):

        return jsonify({
            "error":
            "Faltan campos obligatorios"
        }), 400

    calificacion = float(
        datos["calificacion"]
    )

    if not (
        0 <= calificacion <= 10
    ):

        return jsonify({
            "error":
            "La calificación debe estar entre 0 y 10"
        }), 400

    con = conexion()

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                INSERT INTO calificaciones
                (
                    alumno_id,
                    materia_id,
                    periodo,
                    calificacion
                )
                VALUES
                (%s, %s, %s, %s)
                """,
                (
                    datos["alumno_id"],
                    datos["materia_id"],
                    datos["periodo"],
                    calificacion
                )
            )

            con.commit()

            cache_eliminar(
                CACHE_CALIFICACIONES
            )

            cache_eliminar(
                f"minierp:calificaciones:alumno:{datos['alumno_id']}"
            )

            return jsonify({

                "mensaje":
                    "Calificacion creada",

                "id":
                    cur.lastrowid

            }), 201

    finally:

        con.close()


@app.get("/api/calificaciones/promedio")
@jwt_required()
def promedio_general():

    con = conexion()

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                SELECT
                    AVG(calificacion)
                    AS promedio_general
                FROM calificaciones
                """
            )

            return jsonify(
                cur.fetchone()
            )

    finally:

        con.close()



@app.get("/api/materias/total")
@jwt_required()
def total_materias():

    con = conexion()

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                SELECT COUNT(*) AS total_materias
                FROM materias
                WHERE activo = TRUE
                """
            )

            return jsonify(
                cur.fetchone()
            )

    finally:

        con.close()


@app.get("/api/cache/estado")
@jwt_required()
def estado_cache():

    try:

        info = redis_client.info("stats")

        hits = int(
            info.get(
                "keyspace_hits",
                0
            )
        )

        misses = int(
            info.get(
                "keyspace_misses",
                0
            )
        )

        total = hits + misses

        tasa = (
            (hits / total) * 100
            if total > 0
            else 0
        )

        return jsonify({

            "redis": "disponible",

            "hits": hits,

            "misses": misses,

            "hit_rate": round(
                tasa,
                2
            ),

            "claves": redis_client.dbsize()

        })

    except redis.RedisError as e:

        return jsonify({

            "redis":
                "no disponible",

            "error":
                str(e)

        }), 503


@app.post("/api/cache/limpiar")
@rol_requerido("admin")
def limpiar_cache():

    try:

        redis_client.flushdb()

        return jsonify({
            "mensaje":
            "Cache eliminada correctamente"
        })

    except redis.RedisError as e:

        return jsonify({
            "error":
            str(e)
        }), 503



@app.get("/api/health")
def health():

    mysql_ok = False
    redis_ok = False

    try:

        con = conexion()

        with con.cursor() as cur:

            cur.execute(
                "SELECT 1"
            )

        con.close()

        mysql_ok = True

    except Exception as e:

        app.logger.warning(
            f"MySQL no disponible: {e}"
        )

    try:

        redis_client.ping()

        redis_ok = True

    except Exception as e:

        app.logger.warning(
            f"Redis no disponible: {e}"
        )

    return jsonify({

        "api": "ok",

        "mysql":
            "ok" if mysql_ok
            else "error",

        "redis":
            "ok" if redis_ok
            else "error",

        "version": "1.0"
    })



@app.get("/api/estadisticas")
@jwt_required()
def estadisticas():

    con = conexion()

    try:

        with con.cursor() as cur:

            cur.execute(
                "SELECT COUNT(*) AS total FROM alumnos"
            )

            alumnos = cur.fetchone()["total"]

            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM materias
                WHERE activo = TRUE
                """
            )

            materias = cur.fetchone()["total"]

            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM calificaciones
                """
            )

            calificaciones = cur.fetchone()["total"]

            return jsonify({

                "alumnos": alumnos,

                "materias_activas": materias,

                "calificaciones": calificaciones

            })

    finally:

        con.close()


@app.get("/api/instance")
def instance():
    return jsonify({
        "instance": APP_INSTANCE,
        "hostname": socket.gethostname(),
        "mensaje": "Solicitud atendida correctamente"
    })




if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
