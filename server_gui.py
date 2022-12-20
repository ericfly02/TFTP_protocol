# Importamos las librerias necesarias
from time import *
from socket import *
import struct
from tkinter import *
import math


############################## SEGMENTOS DE PAQUETE #########################################

# Gracias a la funcion struct, podremos crear el paquete

op_codes = {
    "WRQ" : struct.pack('BB', 0, 2),
    "DATA": struct.pack('BB', 0, 3),
    "ACK" : struct.pack('BB', 0, 4),
    "ERR" : struct.pack('BB', 0, 5),
    "OACK" : struct.pack('BB', 0, 6),
}


# Configuramos el socket IPv4
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Especificamos el puerto de recepcion del servidor i definimos variables
size = 512
numero_secuencia = 1 # Inicializamos el numero de secuencia a 1
numero_secuencia_ack =  0 # Inicializamos el numero de secuencia a 0

serverPort = 12000
serverSocket.bind(('', serverPort))
print('El servidor esta listo para recivir conexiones... \n')

mensaje, clientAddress = serverSocket.recvfrom(size)

# Decodificamos el primer paquete recivido para saber si se trata de un GET o un PUT, en funcion si se envia un RRQ o WRQ respectivamente. Tambien observamos si hay algun error
codigo = struct.pack('BB', 0, mensaje[0] + mensaje[1])

for x, y in op_codes.items():
        if codigo == y:
            codigo = x

if(codigo=="ERR"):
    print('ERROR: El MSS esta fuera de rango o bien no es potencia de 2!!')
else:
    print('Cliente CONNECTADO! {ip} , {op}'.format(ip = clientAddress, op = codigo))


############################## PUT #########################################

# Si el codigo se trat de un WRQ, realizamos un PUT

if(codigo == "WRQ"):
    # Decodificamos el paqeute WRQ
    modo = ""
    aux = 2
    
    # OBTENER EL MODO DEL BLOQUE RRQ
    for i in mensaje[aux:]:
        if(i == 0):
            break
        modo += chr(i)
        aux += 1
    print("MODO = ",modo)
    
    # OBTENER EL VALOR DEL BLOCKSIZE de la OPCION 1 DEL BLOQUE RRQ
    size_modo = len(modo)
    aux = +1+int(size_modo)+1+int(len("blocksize"))+1
    a=int.from_bytes(mensaje[aux:], "big")
    #desplazamos el int 8 posiciones porque esta cogiendo del [aux:] 2 bytes=8bits de mas
    size=a>>8
    print("SIZE BLOCK = ",size)
    
    # Generamos paquete OACK
    numero_secuencia=0
    oack = op_codes["OACK"] + bytes('blocksize', "utf-8") + struct.pack('B', 0) + struct.pack('>H', size)+ struct.pack('B', 0)
    # Enviamos paquete OACK
    serverSocket.sendto(oack, clientAddress)
    print("ENVIANDO OACK-> Blocksize = ",size)
    
    print('PUT --> Del cliente {ip}'.format( ip = clientAddress))
    
    #Esperando para recivir los datos del cliente
    datos, clientAddress = serverSocket.recvfrom(4+int(size))

    #Comprovacion de si el paquete de datos recivido no tiene como codigo 
    #de operacion el del paquete ERR
    codigo_err = struct.pack('BB', 0, datos[0] + datos[1])

    for x, y in op_codes.items():
            if codigo_err == y:
                codigo_err = x

    if(codigo_err == 'ERR'):
        print('ERROR: fichero no encontrado en el cliente')

    else:
        print("Esperando a recivir el archivo del cliente con dirección: ", clientAddress)
            #Moviendo 1 byte del paquete con posicion 3 o 2 conseguimos 
            #el valor del numero de sequencia 
        numero_secuencia = datos[3] | datos[2] << 8
        #Guardamos en datos_archivo los datos recividos en el paquete
        datos_archivo = datos[4:]
        print('Reciviendo DATOS: {nseq} --> {datos_archivo}'.format(nseq = numero_secuencia, datos_archivo = datos_archivo))

        # Generamos el paquete ACK
        ack = op_codes["ACK"] + struct.pack('>H', numero_secuencia)

        # Enviamos paquete ACK
        serverSocket.sendto(ack, clientAddress)
        print('Enviando ACK {seq}'.format(seq=numero_secuencia))
        try:
        # Creamos el fichero con el nombre del archivo "mensaje_usuario.txt" y guardamos el mensaje
            file = open("mensaje_usuario.txt", "wb")
            while(datos_archivo):
                #Escribimos en el archivo los datos recividos  
                file.write(datos_archivo)

                # En el caso de que la longitud del archivo sea igual al size maximo de paquetes, enviaremos un paquete
                if(len(datos_archivo) == int(size)):
                    if(numero_secuencia!=0):
                    #Volvemos a recivir mas datos 
                        datos, clientAddress = serverSocket.recvfrom(4 + int(size))
                        #Control de Error por si el codigo de operacion recibido  en el paquete es un ERR
                        codigo_err = struct.pack('BB', 0, datos[0] + datos[1])
                        for x, y in op_codes.items():
                                if codigo_err == y:
                                    codigo_err = x

                        if(codigo_err == 'ERR'):
                            print('ERROR: No definido')
                            break
                        #Moviendo 1 byte del paquete con posicion 3 o 2 conseguimos el valor del numero de sequencia 
                        numero_secuencia = datos[3] | datos[2] << 8
                        #Guardamos en datos_archivo los datos recividos en el paquete
                        datos_archivo = datos[4:]

                        if(numero_secuencia != 0):
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

        except KeyboardInterrupt:
            pass 

        finally:
            try:
                file.close()

                print("El mensaje se ha recivido correctamente!")
                print('\n--------------------------------------------------------------')
                print('                      MENSAJE RECIVIDO                          ')
                print('--------------------------------------------------------------\n')

                f = open("mensaje_usuario.txt", "r")
                line = f.read()
                print(line)
                f.close()          
            except:
                pass


