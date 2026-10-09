from flask import Flask
import pymysql

app = Flask(__name__)


def obtener_conexion():
    return pymysql.connect(
        host="mysql",
        user="minierp_user",
        password="minierp123",
        database="minierp",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route("/")
def inicio():
    return """
    <h1>MiniERP Escolar</h1>
    <p>Flask conectado al proyecto.</p>
    <p>Práctica 5: Flask + MySQL</p>
    """


@app.route("/alumnos")
def alumnos():

    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:

            cursor.execute("SELECT * FROM alumnos")

            datos = cursor.fetchall()

        html = "<h1>Alumnos</h1>"
        
        html += "<h2>Sistema de Control Escolar</h2>"
        
        html += "<p>Informacion obtenida desde MySQL mediante Flask</p>"
        
        html += "<table border='1'>"

        html += """
        <tr>
            <th>ID</th>
            <th>Nctrl</th>
            <th>Nombre</th>
            <th>Promedio</th>
            <th>Carrera</th>
            <th>Semestre</th>
            <th>Sexo</th>
        </tr>
        """

        for alumno in datos:

            html += f"""
            <tr>
                <td>{alumno['id']}</td>
                <td>{alumno['Nctrl']}</td>
                <td>{alumno['nombre']}</td>
                <td>{alumno['promedio']}</td>
                <td>{alumno['carrera']}</td>
                <td>{alumno['semestre']}</td>
                <td>{alumno['sexo']}</td>
            </tr>
            """

        html += "</table>"

        return html

    finally:
        conexion.close()

@app.route("/promedio")
def promedio():

	conexion = obtener_conexion()

	try:
		with conexion.cursor() as cursor:

			cursor.execute(
				"SELECT AVG(promedio) AS promedio_general FROM alumnos"
			)

			resultado = cursor.fetchone()

		return f"""
		<h1>Promedio general de los alumnos</h1>
		<p>{resultado['promedio_general']:.2f}</p>
		"""

	finally:
		conexion.close()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )


