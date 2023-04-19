import mysql.connector
from mysql.connector import Error
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import pyodbc
import datetime

lector = SimpleMFRC522()

SALON = "G12"


def conectar_bd():
    # Conectar a la base de datos
        conexion = mysql.connector.connect(
            host='192.168.100.10',
            user='remote',
            password='Briza_3121',
            database='proyecto_accesos'
        )
    
        return conexion

def registrar_acceso():
    # Obtener la fecha y hora actual
    now = datetime.datetime.now()

    # Definir el rango de tiempo permitido como 20 minutos antes o después de la fecha y hora actual
    time_range = datetime.timedelta(minutes=20)

    if tipo_usuario == "P":
        if horario and now - time_range <= horario <= now + time_range and salon == SALON:
            cursor = conexion.cursor()
            query = "INSERT INTO proyecto_accesos.accesos (fecha_acceso, identificador) VALUES (CURRENT_TIMESTAMP(), %s)"
            valores = (identificador,)
            cursor.execute(query,valores)
            conexion.commit()
            cursor.close()
            print("Se registro el acceso de: ",identificador)
        elif not horario:
            print("El usuario no tiene horario asignado.")
        else:
            print("No se registrara el acceso ya que lo intenta realizar fuera del horario valido.")
    else:
        print("No se puede agregar un acceso para un usuario que no es profesor.")

try: 
    conexion = conectar_bd()

    if conexion.is_connected():
        print("Conexion exitosa.")
        while True:
            id=lector.read()
            registro = str(id)
            identificador = registro[1:13]
            cursor=conexion.cursor()
            query = "SELECT * FROM proyecto_accesos.usuarios LEFT JOIN clases ON usuarios.identificador = clases.id_profesor WHERE usuarios.identificador = %s;"
            
            try:
                cursor.execute(query, (identificador,))
                resultado = cursor.fetchone()
                identificador = resultado[0]
                nombre = resultado[1]
                apellido_p = resultado[2]
                apellido_m = resultado[3]
                matricula = resultado[4]
                tipo_usuario = resultado[5]
                contrasena = resultado[6]
                id_horario = resultado[7]
                nombre_materia = resultado[8]
                salon = resultado[9]
                clave_materia = resultado[10]
                grupo = resultado[11]
                horario = resultado[12]
                id_profesor = resultado[13]
                # aquí puedes hacer lo que quieras con las variables obtenidas

                # Supongamos que tienes una variable "fecha_hora" con un dato tipo DATETIME de MySQL
                '''horario_format = datetime.datetime.strptime(horario, '%Y-%m-%d %H:%M:%S')'''

               

                registrar_acceso()
                
                

            except Exception as e:
                print("Error", f"No se pudo ejecutar el query: {e} ya que el usuario no esta registrado en el sistema.")
            
            conexion.commit()
            cursor.close()
           
            

            
except Error as ex:
    print("Error durante la conexion.", ex)
finally:
    if conexion.is_connected():
        conexion.close()
        GPIO.cleanup()
        print("La conexion ha finalizado")





