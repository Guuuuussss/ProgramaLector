#Autor: Gustavo Antonio Luna Maya
#Librerias necesarias para el funcionamiento del programa. 
import mysql.connector
from mysql.connector import Error
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import pyodbc
import datetime
import logging

#Se inicializa el lector RFID
lector = SimpleMFRC522()

#Se asigna un salón a un modulo Raspberry
SALON = "A-101"


#La función conectar_bd() se encarga de establecer una conexión a una base de datos utilizando el módulo mysql.connector de Python.
def conectar_bd():
    # Conectar a la base de datos
    conexion = mysql.connector.connect(
        host='192.168.100.9',
        user='remote',
        password='Briza_3121',
        database='proyecto_accesos'
    )

    return conexion


#La función registrar_acceso valida la fecha actual y si se cumplen las condiciones relaliza el query para registrar el acceso del profesor y abre la puerta del salón.
def registrar_acceso():
    # Obtener la fecha y hora actual
    now = datetime.datetime.now()

    # Definir el rango de tiempo permitido como 20 minutos antes o después de la fecha y hora actual
    time_range = datetime.timedelta(minutes=30)

    if tipo_usuario == "P":
        if horario and now - time_range <= horario <= now + time_range and salon == SALON:
            cursor = conexion.cursor()
            query = "INSERT INTO proyecto_accesos.accesos (fecha_acceso, identificador) VALUES (CURRENT_TIMESTAMP(), %s);"
            valores = (identificador,)
            cursor.execute(query, valores)
            conexion.commit()
            cursor.close()
            print("Se abrira la puerta del salón, Se registro el acceso de: ", identificador)
        elif not horario:
            print("El usuario no tiene horario asignado.")
        elif salon != SALON:
            print("El salon al que intenta ingresar no es el correcto.")
        elif tipo_usuario == 'E':
            print("Por el momento no podemos registrar el acceso de los estudiantes.")
        else:
            print(
                "No se registrara el acceso ya que lo intenta realizar fuera del horario valido.")
    else:
        print("No se puede agregar un acceso para un usuario que no es profesor.")


#Inicio del programa
#Se lee el identificador de la credencial y se guarda en la variable identificador,
#el query obtiene los horario del profesor que tienen en este salón y las ordena segun la fecha tomando como referencia la fecha actual.
try:
    conexion = conectar_bd()

    if conexion.is_connected():
        print("Conexion exitosa.")
        while True:
            id = lector.read()
            registro = str(id)
            identificador = registro[1:13]
            cursor = conexion.cursor()
            
            query = "SELECT * FROM proyecto_accesos.usuarios LEFT JOIN clases ON usuarios.identificador = clases.id_profesor WHERE usuarios.identificador = %s AND clases.salon = %s ORDER BY ABS(TIMESTAMPDIFF(SECOND, NOW(), clases.horario));"
            
            try:
                
                cursor.execute(query, (identificador,SALON,))
                resultado = cursor.fetchall()
                #Guardamos el primer resultado del query ya que es la clase o horario que tiene en este salón al momento de intentar el acceso.
                if len(resultado) > 0:
                    primer_fila = resultado[0]

                    identificador = primer_fila[0]
                    nombre = primer_fila[1]
                    apellido_p = primer_fila[2]
                    apellido_m = primer_fila[3]
                    matricula = primer_fila[4]
                    tipo_usuario = primer_fila[5]
                    contrasena = primer_fila[6]
                    id_horario = primer_fila[7]
                    nombre_materia = primer_fila[8]
                    salon = primer_fila[9]
                    clave_materia = primer_fila[10]
                    grupo = primer_fila[11]
                    horario = primer_fila[12]
                    id_profesor = primer_fila[13]
                else:
                    primer_fila = resultado[0]
                    identificador = primer_fila[0]
                    nombre = primer_fila[1]
                    apellido_p = primer_fila[2]
                    apellido_m = primer_fila[3]
                    matricula = primer_fila[4]
                    tipo_usuario = primer_fila[5]
                    contrasena = primer_fila[6]
                    id_horario = primer_fila[7]
                    nombre_materia = primer_fila[8]
                    salon = primer_fila[9]
                    clave_materia = primer_fila[10]
                    grupo = primer_fila[11]
                    horario = primer_fila[12]
                    id_profesor = primer_fila[13]
                
                #Si el profesor esta dado de alta, por lo tanto el query trajo registros de la base de datos se manda llamar la función registrar_acceso. 
                #Si el profesor no esta registrado o intenta acceder en un salón incorrecto se imprime un mensaje de error. 
                registrar_acceso()

            except Exception as e:
                print("Error, el usuario no esta registrado en el sistema o esta intentando ingresar en el salón incorrecto.")

            conexion.commit()
            cursor.close()

#Si no existe o se realiza la conexón con la base de datos, lanzamos el siguiente error. 
except Error as ex:
    logger = logging.getLogger(__name__)
    logger.error("Error durante la conexion.", exc_info=True)
finally:
    if conexion.is_connected():
        conexion.close()
        GPIO.cleanup()
        print("La conexion ha finalizado")
