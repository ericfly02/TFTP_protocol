import random
import socket
import time
from math import *
import struct

# Configuracion
#num_paquetes = 1
tamaño_paquete = 1
probabilidad_perdida = 0.1
timeout = 0.1

# Crear socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Creamos timeout para el socket
sock.settimeout(timeout)

# Mensaje a enviar
mensaje = "HELLO WORLD"

# calcular numero de paquetes
num_paquetes = ceil(len(mensaje) / tamaño_paquete)
print("Numero de paquetes: {numero}".format(numero = num_paquetes))

# Creamos array de datos
datos = []

# Añadir primer paquete con el numero de paquetes
datos.append(str(num_paquetes))

# dividir el mensaje en N paquetes
for i in range(0, len(mensaje), tamaño_paquete):
    datos.append(mensaje[i:i+tamaño_paquete])
    print("Enviando paquete --> {numero}".format(numero = i/tamaño_paquete))

# Creamos array de paquetes
paquetes = []

# Añadir cabecera a cada paquete con el numero de paquete
for i in range(len(datos)):
    # preparamos el numero de paquete
    i_num = i.to_bytes(10, byteorder='big')
    # preparamos los datos del paquete
    i_datos = datos[i].encode('utf-8')

    # juntamos el numero de paquete y los datos
    paquetes.append(i_num + i_datos)
    












    

