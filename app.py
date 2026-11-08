import os
import io
import base64
import qrcode
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mail import Mail, Message

# Definir la ruta raíz absoluta para que Flask encuentre los archivos HTML y CSS sin error
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder=basedir, static_folder=basedir)
app.secret_key = os.environ.get('SECRET_KEY', 'doctora123')

# --- CONFIGURACIÓN DE FLASK-MAIL ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '00edrick00247@gmail.com')
# NOTA: Asegúrate de usar una Contraseña de Aplicación de 16 caracteres de Google aquí
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'namakzzxhyldwbnp')
app.config['MAIL_DEFAULT_SENDER'] = ('REDENT Odontología', os.environ.get('MAIL_USERNAME', '00edrick00247@gmail.com'))

mail = Mail(app)


# --- CONFIGURACIÓN DE CONEXIÓN A MYSQL ---
def conectar_bd():
    try:
        return mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'gateway01.us-east-1.prod.aws.tidbcloud.com'),
            user=os.environ.get('DB_USER', 'MhRDjVkQLPjvSzY.root'),
            password=os.environ.get('DB_PASSWORD', 'IrdXcviKCq5twvoz'),
            database=os.environ.get('DB_NAME', 'test'),
            port=int(os.environ.get('DB_PORT', 4000)),
            ssl_disabled=False,
            ssl_verify_identity=False,
            connect_timeout=5
        )
    except Exception as e:
        print(f"Error de conexión a la BD: {e}")
        raise e


# --- NAVEGACIÓN PRINCIPAL ---
@app.route('/')
def inicio():
    return render_template('index.html', titulo="REDENT")


@app.route('/servicios')
def servicios():
    return render_template('Nuestroservicios.html')


# ==========================================
# FLUJO 1: REGISTRO DE PACIENTES
# ==========================================
@app.route('/registro')
def registro():
    return render_template('registro.html')


@app.route('/guardar_paciente', methods=['POST'])
def guardar_paciente():
    conexion = None
    cursor = None
    try:
        nombre = request.form.get('nombre', '').strip()
        fecha_nacimiento = request.form.get('fecha_nacimiento', '')
        telefono = request.form.get('telefono', '').strip()
        correo = request.form.get('correo', '').strip()

        if not nombre or not fecha_nacimiento:
            return "<h3>Error: Por favor completa el nombre y la fecha de nacimiento.</h3>", 400

        conexion = conectar_bd()
        cursor = conexion.cursor()

        query_paciente = """
            INSERT INTO Pacientes (Nombre_completo, Fecha_nacimiento, Telefono, Correo)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query_paciente, (nombre, fecha_nacimiento, telefono, correo))
        conexion.commit()

        paciente_id = cursor.lastrowid
        codigo = f"PAC-{paciente_id}"

        qr_base64 = ""

        # --- GENERAR QR, MOSTRAR EN WEB Y ENVIAR AL CORREO DEL PACIENTE ---
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(codigo)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            qr_bytes = img_io.getvalue()

            qr_base64 = base64.b64encode(qr_bytes).decode('utf-8')

            if correo:
                msg = Message(
                    subject="¡Registro exitoso en REDENT - Tu Código QR de Paciente!",
                    recipients=[correo]
                )
                msg.body = f"Hola {nombre},\n\nGracias por registrarte en el Consultorio Odontológico REDENT.\nTu código de paciente es: {codigo}\n\nPuedes presentar el código QR adjunto en tus próximas citas."
                msg.html = f"""
                <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px;">
                    <h2>¡Bienvenido a REDENT Odontología!</h2>
                    <p>Hola <strong>{nombre}</strong>,</p>
                    <p>Gracias por registrarte en nuestro consultorio.</p>
                    <p>Tu código de paciente asignado es: <b style="font-size: 1.2em; color: #0056b3;">{codigo}</b></p>
                    <p>Presenta el siguiente código QR para agendar o confirmar tus citas rápidamente:</p>
                    <div style="text-align: center; margin: 20px 0;">
                        <img src="data:image/png;base64,{qr_base64}" alt="Código QR Paciente" style="width: 200px; height: 200px;" />
                    </div>
                    <p>¡Te esperamos!</p>
                </div>
                """
                msg.attach(
                    filename=f"codigo_qr_{codigo}.png",
                    content_type="image/png",
                    data=qr_bytes
                )

                mail.send(msg)
        except Exception as mail_error:
            print(f"[ERROR EMAIL PACIENTE]: {mail_error}")

        return render_template(
            'confirmacion.html',
            codigo=codigo,
            nombre=nombre,
            fecha_nacimiento=fecha_nacimiento,
            qr_code=qr_base64
        )

    except mysql.connector.Error as err:
        if conexion:
            conexion.rollback()
        return f"<h3>Error en la Base de Datos: {err}</h3>", 500
    except Exception as e:
        return f"<h3>Error inesperado: {e}</h3>", 500
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


# ==========================================
# FLUJO 2: AGENDAR CITA
# ==========================================
@app.route('/agendar_cita_form')
def agendar_cita_form():
    return render_template('Nuestroservicios.html')


@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if request.method == 'POST':
        codigo_raw = request.form.get('codigo_paciente', '').strip()
        servicio = request.form.get('servicio', '').strip()
        fecha = request.form.get('fecha_atencion', '')
        hora = request.form.get('hora_atencion', '')
        sintomas = request.form.get('sintomas', '').strip()

        try:
            paciente_id = int(codigo_raw.upper().replace('PAC-', '').strip())
        except ValueError:
            return "<h3>Error: El código de paciente no tiene un formato válido (ejemplo: PAC-1 o 1).</h3>", 400

        conexion = None
        cursor = None
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor(dictionary=True)

            # Verificar que el paciente exista
            cursor.execute("SELECT Codigo_registro, Nombre_completo, Correo FROM Pacientes WHERE Codigo_registro = %s", (paciente_id,))
            paciente = cursor.fetchone()
            if not paciente:
                return "<h3>Error: El código de paciente no está registrado en la base de datos.</h3>", 400

            # Verificar horario ocupado
            cursor.execute("SELECT id_citas FROM citas WHERE fecha_atencion = %s AND hora_atencion = %s", (fecha, hora))
            if cursor.fetchone():
                return "<h3>Error: Ese horario ya fue ocupado. Por favor elige otro.</h3>", 400

            # Guardar cita
            query_cita = """
                INSERT INTO citas (paciente_codigo, servicio_solicitado, fecha_atencion, hora_atencion, sintomas)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query_cita, (paciente_id, servicio, fecha, hora, sintomas))
            conexion.commit()

            cita_id = cursor.lastrowid
            codigo_cita = f"CITA-{cita_id}"

            qr_base64 = ""

            # --- GENERAR QR DE LA CITA Y ENVIAR POR CORREO ---
            try:
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(f"Cita: {codigo_cita} | Paciente: {paciente['Nombre_completo']} | Fecha: {fecha} {hora} | Servicio: {servicio}")
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                img_io = io.BytesIO()
                img.save(img_io, 'PNG')
                qr_bytes = img_io.getvalue()

                qr_base64 = base64.b64encode(qr_bytes).decode('utf-8')

                if paciente['Correo']:
                    msg = Message(
                        subject=f"¡Cita Agendada Exitosamente - Folio {codigo_cita}!",
                        recipients=[paciente['Correo']]
                    )
                    msg.body = f"Hola {paciente['Nombre_completo']},\n\nTu cita para {servicio} el día {fecha} a las {hora} ha sido agendada.\nFolio: {codigo_cita}"
                    msg.html = f"""
                    <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px;">
                        <h2>Confirmación de Cita - REDENT</h2>
                        <p>Hola <strong>{paciente['Nombre_completo']}</strong>,</p>
                        <p>Tu cita para el servicio de <strong>{servicio}</strong> ha sido agendada con éxito.</p>
                        <ul>
                            <li><b>Folio de Cita:</b> {codigo_cita}</li>
                            <li><b>Fecha:</b> {fecha}</li>
                            <li><b>Hora:</b> {hora}</li>
                        </ul>
                        <p>Adjunto y a continuación encontrarás tu código QR para presentar el día de tu consulta:</p>
                        <div style="text-align: center; margin: 20px 0;">
                            <img src="data:image/png;base64,{qr_base64}" alt="Código QR Cita" style="width: 200px; height: 200px;" />
                        </div>
                        <p>¡Te esperamos en REDENT Odontología!</p>
                    </div>
                    """
                    msg.attach(f"qr_{codigo_cita}.png", "image/png", qr_bytes)
                    mail.send(msg)
            except Exception as mail_err:
                print(f"[ERROR EMAIL CITA]: {mail_err}")

            return render_template(
                'confirmacion_cita.html',
                codigo_cita=codigo_cita,
                nombre=paciente['Nombre_completo'],
                servicio=servicio,
                fecha_atencion=fecha,
                hora_atencion=hora,
                sintomas=sintomas if sintomas else "Ninguno",
                qr_code=qr_base64
            )

        except mysql.connector.Error as err:
            if conexion:
                conexion.rollback()
            return f"<h3>Error en la Base de Datos: {err}</h3>", 500
        finally:
            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()

    return render_template('Nuestroservicios.html')


@app.route('/api/horarios_ocupados', methods=['GET'])
def obtener_horarios_ocupados():
    fecha_seleccionada = request.args.get('fecha')
    if not fecha_seleccionada:
        return jsonify([])

    conexion = None
    cursor = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute("SELECT TIME_FORMAT(hora_atencion, '%H:%i') FROM citas WHERE fecha_atencion = %s", (fecha_seleccionada,))
        filas = cursor.fetchall()
        ocupados = [f[0] for f in filas]
        return jsonify(ocupados)
    except Exception:
        return jsonify([])
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


# ==========================================
# PANEL DEL DENTISTA
# ==========================================
@app.route('/dentista', methods=['GET', 'POST'])
def dentista():
    PASSWORD_DENTISTA = os.environ.get('DENTISTA_PASSWORD', '1234')

    if request.method == 'POST':
        if 'login_password' in request.form:
            password_ingresada = request.form['login_password']
            if password_ingresada == PASSWORD_DENTISTA:
                session['dentista_logged_in'] = True
            else:
                return render_template('dentista.html', error="Contraseña incorrecta", logged_in=False)

    logged_in = session.get('dentista_logged_in', False)
    pacientes = []
    citas = []

    if logged_in:
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor(dictionary=True)

            cursor.execute("SELECT * FROM Pacientes ORDER BY Codigo_registro DESC")
            pacientes = cursor.fetchall()

            query_citas = """
                SELECT 
                    c.id_citas,
                    c.paciente_codigo,
                    p.Nombre_completo,
                    p.Telefono,
                    c.servicio_solicitado,
                    c.fecha_atencion,
                    c.hora_atencion,
                    c.sintomas
                FROM citas c
                LEFT JOIN Pacientes p ON c.paciente_codigo = p.Codigo_registro
                ORDER BY c.fecha_atencion DESC, c.hora_atencion ASC
            """
            cursor.execute(query_citas)
            citas = cursor.fetchall()

            cursor.close()
            conexion.close()
        except Exception as e:
            print(f"Error cargando panel del dentista: {e}")

    return render_template('dentista.html', logged_in=logged_in, pacientes=pacientes, citas=citas)


@app.route('/logout_dentista')
def logout_dentista():
    session.pop('dentista_logged_in', None)
    return redirect(url_for('dentista'))


@app.route('/editar_paciente', methods=['POST'])
def editar_paciente():
    if not session.get('dentista_logged_in'):
        return redirect(url_for('dentista'))

    codigo_registro = request.form['codigo_registro']
    nombre = request.form['nombre']
    fecha_nacimiento = request.form['fecha_nacimiento']
    telefono = request.form['telefono']
    correo = request.form['correo']

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        query = """
            UPDATE Pacientes 
            SET Nombre_completo = %s, Fecha_nacimiento = %s, Telefono = %s, Correo = %s
            WHERE Codigo_registro = %s
        """
        cursor.execute(query, (nombre, fecha_nacimiento, telefono, correo, codigo_registro))
        conexion.commit()
        cursor.close()
        conexion.close()
    except Exception as e:
        print(f"Error editando paciente: {e}")

    return redirect(url_for('dentista'))


@app.route('/eliminar_paciente/<int:codigo_registro>', methods=['POST'])
def eliminar_paciente(codigo_registro):
    if not session.get('dentista_logged_in'):
        return redirect(url_for('dentista'))

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        query = "DELETE FROM Pacientes WHERE Codigo_registro = %s"
        cursor.execute(query, (codigo_registro,))
        conexion.commit()
        cursor.close()
        conexion.close()
    except Exception as e:
        print(f"Error eliminando paciente: {e}")

    return redirect(url_for('dentista'))


@app.route('/eliminar_cita/<int:id_cita>', methods=['POST'])
def eliminar_cita(id_cita):
    if not session.get('dentista_logged_in'):
        return redirect(url_for('dentista'))

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        query = "DELETE FROM citas WHERE id_citas = %s"
        cursor.execute(query, (id_cita,))
        conexion.commit()
        cursor.close()
        conexion.close()
    except Exception as e:
        print(f"Error eliminando cita: {e}")

    return redirect(url_for('dentista'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)