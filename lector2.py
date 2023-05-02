#Autor: Gustavo Antonio Luna Maya
#Librerias necesarias para el funcionamiento del programa. 
'''
Este es un programa de Python que utiliza una Raspberry Pi para leer identificadores de credenciales RFID y verificar si el usuario tiene permiso para acceder a un salón específico. Aquí está una descripción general de lo que está sucediendo en el programa:

Primero, se importan las bibliotecas necesarias para el programa, incluyendo el conector de MySQL para Python, el módulo de lectura del lector RFID y el módulo de registro de eventos. Luego, se inicializa el lector RFID y se asigna un salón específico al módulo Raspberry.

La función conectar_bd() se utiliza para establecer una conexión a la base de datos MySQL. En el programa, se utiliza para conectarse a la base de datos que contiene la información del usuario y los horarios de clase.

La función registrar_acceso() se utiliza para registrar un acceso exitoso a la base de datos y abrir la puerta del salón correspondiente. Esta función verifica que el usuario tenga permiso para acceder al salón en el que se encuentra el lector RFID, y que esté dentro del horario permitido. Si se cumplen estas condiciones, se registra un acceso en la base de datos y se abre la puerta del salón.

El programa comienza con la lectura del identificador de la credencial RFID. Luego, se ejecuta un query para obtener el horario del profesor en el salón correspondiente en el momento en que intenta ingresar. Si se encuentra un horario válido, se guarda la información del usuario y del horario en variables. Si el usuario es un profesor, se llama a la función registrar_acceso() para registrar el acceso y abrir la puerta del salón. Si no se encuentra un horario válido o el usuario no es un profesor, se imprime un mensaje de error.
'''
import mysql.connector
from mysql.connector import Error
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import datetime
from gpiozero import AngularServo
from time import sleep

servo = AngularServo(18,min_pulse_width=0.0006,max_pulse_width=0.0023)

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
    bandera = True
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
            
            while(bandera):
                servo.angle= 0
                sleep(2)
                servo.angle= 90
                sleep(2)
                bandera = False
            
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
    print("Error durante la conexón.")
finally:
    if conexion.is_connected():
        conexion.close()
        GPIO.cleanup()
        print("La conexion ha finalizado")
