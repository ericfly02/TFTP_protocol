# Importamos las librerias necesarias
from time import *
from socket import *
import struct
from tkinter import *
import math
import random
import sys


############################## SEGMENTOS DE PAQUETE #########################################

try:
    # Gracias a la funcion struct, podremos crear el paquete
    op_codes = {
        "ACK" : struct.pack('BB', 0, 4),
        "OACK" : struct.pack('BB', 0, 6),
    }


    # Configuramos el socket IPv4
    serverSocket = socket(AF_INET, SOCK_DGRAM)

    # Especificamos el puerto de recepcion del servidor i definimos variables
    size = 512
    numero_secuencia = 1 # Inicializamos el numero de secuencia a 1
    numero_secuencia_ack =  1 # Inicializamos el numero de secuencia a 1

    probabilidad_fallo = 0

    serverPort = 12001
    serverSocket.bind(('', serverPort))
    print('El servidor esta listo para recivir conexiones... \n')

    mensaje, clientAddress = serverSocket.recvfrom(size)

    # Decodificamos el primer paquete recivido para saber que mss utilizamos
    codigo = struct.pack('BB', 0, mensaje[0] + mensaje[1])

    print('Cliente CONNECTADO! {ip}'.format(ip = clientAddress))


    ############################## PUT #########################################

    # Decodificamos el paqeute recivido 
    # se utiliza para calcular la posición inicial del tamaño del bloque en el primer paquete recibido del servidor. 
    # El tamaño del bloque se encuentra después de la cadena "blocksize" en el paquete. La función len() devuelve el 
    # tamaño de la cadena "blocksize" y se suma 1 para obtener la posición siguiente.
    aux = int(len("blocksize"))+1
    # Se utiliza para convertir los bytes de tamaño del bloque en un entero
    a = int.from_bytes(mensaje[aux:], "big")
    # Desplazamos el int 8 posiciones porque esta cogiendo del [aux:] 2 bytes=8bits de mas
    size=a>>8
    print("SIZE BLOCK = ",size)

    # Generamos paquete OACK
    numero_secuencia=0
    oack = op_codes["OACK"] + bytes('blocksize', "utf-8") + struct.pack('B', 0) + struct.pack('>H', size)+ struct.pack('B', 0)
    # Enviamos paquete OACK
    serverSocket.sendto(oack, clientAddress)
    print("ENVIANDO OACK-> Blocksize = ",size)

    print('SUBIENDO ARCHIVO DEL CLIENTE --> {ip}'.format( ip = clientAddress))

    #Esperando para recivir los datos del cliente
    datos, clientAddress = serverSocket.recvfrom(4+int(size))

    print("Esperando a recivir el archivo del cliente con dirección: ", clientAddress)
    # Moviendo 1 byte del paquete con posicion 3 o 2 conseguimos el valor del numero de sequencia 
    numero_secuencia = datos[3] | datos[2] << 8
    #Guardamos en datos_archivo los datos recividos en el paquete
    datos_archivo = datos[4:]
    print('Reciviendo DATOS: {nseq} --> {datos_archivo}'.format(nseq = numero_secuencia, datos_archivo = datos_archivo))

    # Generamos el paquete ACK
    ack = op_codes["ACK"] + struct.pack('>H', numero_secuencia)

    # Enviamos paquete ACK
    serverSocket.sendto(ack, clientAddress)
    print('Enviando ACK {seq}'.format(seq=numero_secuencia))

    # Creamos el fichero con el nombre del archivo "mensaje_usuario.txt" y guardamos el mensaje
    file = open("mensaje_usuario.txt", "wb")

    #Escribimos en el archivo los datos recividos  
    file.write(datos_archivo)

    while(datos_archivo):

        # En el caso de que la longitud del archivo sea igual al size maximo de paquetes, enviaremos un paquete
        if(len(datos_archivo) == int(size)):
            if(numero_secuencia!=0):
                #Volvemos a recivir mas datos 
                datos, clientAddress = serverSocket.recvfrom(4 + int(size))
                #Moviendo 1 byte del paquete con posicion 3 o 2 conseguimos el valor del numero de sequencia 
                numero_secuencia = datos[3] | datos[2] << 8
                if(numero_secuencia_ack < numero_secuencia):
                    #Guardamos en datos_archivo los datos recividos en el paquete
                    datos_archivo = datos[4:]
                    print('ACK --> {} es menor que {}'.format(numero_secuencia_ack, numero_secuencia))
                    numero_secuencia_ack += 1
                    #Escribimos en el archivo los datos recividos  
                    file.write(datos_archivo)
                    

                if(numero_secuencia != 0):
                    # Miramos mediante la libreria random, si un paquete se ha perdido
                    if (random.random() < probabilidad_fallo):
                        print(('PAQUETE ACK PERDIDO NUMERO: {}').format(numero_secuencia))
                    else:
                        print('Reciviendo DATOS: {nseq} --> {datos_archivo}'.format(nseq = numero_secuencia, datos_archivo = datos_archivo))
                        # Generamos el paquete ACK
                        ack = op_codes["ACK"] + struct.pack('>H', numero_secuencia)
                        # Enviamos paquete ACK
                        serverSocket.sendto(ack, clientAddress)
                        print('Enviando ACK {seq}'.format(seq=numero_secuencia))
                else:
                    #PONEMOS UNOS DATOS COMO BYTES PARA DECIR QUE EL FICHERO SE HA RECIBIDO CORRECTAMENTE
                    datos_archivo = bytes()	
        
        else:
            datos_archivo = bytes()


    file.close()

    print("El mensaje se ha recivido correctamente!")
    print('\n--------------------------------------------------------------')
    print('                      MENSAJE RECIVIDO                          ')
    print('--------------------------------------------------------------\n')

    f = open("mensaje_usuario.txt", "r")
    line = f.read()
    print(line)
    f.close()          


except KeyboardInterrupt:
    sys.exit() 