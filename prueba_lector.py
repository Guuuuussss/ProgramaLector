import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

lector = SimpleMFRC522()

id=lector.read()
registro = str(id)

identificador = registro[1:13]
print(identificador)

GPIO.cleanup()
