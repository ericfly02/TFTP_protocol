import socket
import time
import random

# Dirección y puerto del servidor
HOST = 'localhost'
PORT = 1234

# Tamaño del buffer de envío y recepción
BUFFER_SIZE = 1024

# Tamaño del paquete a enviar
PACKET_SIZE = 10

# Tiempo máximo de espera por la confirmación (ACK)
TIMEOUT = 1

# Número de paquetes a enviar
N = 100

# Probabilidad de pérdida de paquetes
LOSS_PROBABILITY = 0.1

# Crear socket y establecer conexión con el servidor
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

# Establecer tiempo máximo de espera por la confirmación (ACK)
sock.settimeout(TIMEOUT)

# Contador de paquetes enviados
packet_count = 0

# Bucle para enviar los N paquetes
for i in range(1, N+1):
    # Incrementar contador de paquetes enviados
    packet_count += 1

    # Crear mensaje a enviar
    message = f'{i:0{PACKET_SIZE}}'

    # Enviar paquete
    sock.sendto(message.encode(), (HOST, PORT))

    # Esperar por la confirmación (ACK)
    try:
        data, address = sock.recvfrom(BUFFER_SIZE)
    except socket.timeout:
        # Si no se recibe la confirmación (ACK) en el tiempo esperado, volver a enviar el paquete
        sock.sendto(message.encode(), (HOST, PORT))

        # Esperar de nuevo por la confirmación (ACK)
        data, address = sock.recvfrom(BUFFER_SIZE)

    # Procesar confirmación (ACK)
    ack = int(data.decode())
    if ack == i:
        # Si la confirmación (ACK) es correcta, continuar con la siguiente iteración
        continue
    else:
        # Si la confirmación (ACK) es incorrecta, volver a enviar el paquete
        sock.sendto(message.encode(), (HOST, PORT))

# cerrar socket
sock.close()


"""
En este ejemplo, se utiliza el método `settimeout()` del socket para establecer un tiempo máximo de espera por la confirmación (ACK). Si no se recibe la confirmación (ACK) en el tiempo esperado, se vuelve a enviar el paquete utilizando el método `sendto()`.

También se ha incluido una probabilidad de pérdida de paquetes utilizando la función `random.random()`, que genera un número aleatorio entre 0 y 1. Si el número generado es menor que la probabilidad de pérdida de paquetes, se omite el envío del paquete en esa iteración del bucle.

Es importante tener en cuenta que este código es solo un ejemplo y puede ser necesario ajustarlo según las necesidades específicas de su aplicación.
"""
