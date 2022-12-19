
# TEORIA: Estructura de los paquetes a enviar

# DATA:
#	| 2 bytes | 2 bytes | n bytes |
# 	----------------------------------
# 	| Opcode  | Block # |  Data   |
# 	----------------------------------

# RRQ / WRQ:
#	| 2 bytes | string   | 1 byte | string | 1 byte |
# 	--------------------------------------------------
# 	| Opcode  | Filename |   0    |  Mode  |   0    |
# 	--------------------------------------------------

# ACK:
#	| 2 bytes | 2 bytes | 
# 	---------------------
# 	| Opcode  | Block # |  
# 	---------------------

# ERROR:
#	| 2 bytes | 2 bytes   | string | 1 byte |
# 	-----------------------------------------
# 	| Opcode  | ErrorCode | ErrMsg |   0    |
# 	-----------------------------------------

# OACK:
#	| 2 bytes |  2 bytes  | 1 byte |  1 byte |
# 	-----------------------------------------
# 	| Opcode  |  Opcio 1  |   0    | Value 1 |
# 	-----------------------------------------

# Importamos las librerias necesarias
from functools import partial
from tkinter import *
from random import random, randrange
from socket import *
import time
import struct
import math


############################## FUNCIONES AUXILIARES #######################################

def Log2(x):
    return (math.log10(x) /
            math.log10(2))
 
# indica si el numero n es una potencia de 2^k siendo k un numero del 3 al 11
def es_potencia(n):
    return (math.ceil(Log2(n)) == math.floor(Log2(n)))


################################### PUT ###################################

def put(mss, mensaje, modo, Timeout, ip, puerto):

    #Inicializamos el servername i el serverport
    serverName = 'localhost'
    serverPort = 12001
    numero_secuencia = 1 # Inicializamos el numero de secuencia a 1
    numero_secuencia_ack =  0 # Inicializamos el numero de secuencia a 0

    #Almacena los datos recogidos en la GUI en variables
    mss = int(mss.get("1.0", "end-1c"))
    mensaje = mensaje.get("1.0", "end-1c")
    timeout = int(Timeout.get("1.0", "end-1c"))
    mode = modo.get("1.0", "end-1c")
    serverName = ip.get("1.0", "end-1c")
    serverPort = int(puerto.get("1.0", "end-1c"))

    # Guardamos el mensaje del usuario en un fichero txt
    fichero = open("mensaje_usuario.txt", "w")
    fichero.write(mensaje)
    fichero.close()

    # Crear socket  
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    # Gracias a la funcion struct, podremos crear el paquete
    op_codes = {
        "RRQ" : struct.pack('BB', 0, 1),
        "WRQ" : struct.pack('BB', 0, 2),
        "DATA": struct.pack('BB', 0, 3),
        "ACK" : struct.pack('BB', 0, 4),
        "ERR" : struct.pack('BB', 0, 5),
    }

    # Añadimos los tipos de error que nos puede otorgar el paquete ERR
    err_codes = {
        "NotDefined"        : struct.pack('BB', 0, 1),
        "IllegalOperation"  : struct.pack('BB', 0, 2), 
    }


    #Comprueba que el valor de mss sea correcto
    if(es_potencia(mss)):

        # Enviamos primer paquete WRQ
        wrq = op_codes["WRQ"] + bytes(mode, "utf-8") + struct.pack('B', 0) + bytes('blocksize', "utf-8") + struct.pack('B', 0) + struct.pack('>H', mss)+ struct.pack('B', 0)
        recive_oack=True
        #Hacemos un bucle para enviar la instruccion WRQ i
        #recivir el OACK del servidor para confirmar la conexion WRQ.
        #Si el cliente no recive el OACK aplica un timeout i vuelve a enviar el WRQ
        while recive_oack:
            try:
            	#Envia el paquete WRQ
                clientSocket.sendto(wrq, (serverName,serverPort))
                print("Enviando siguiente paquete: (WRQ, {mode}, blocksize, {mss})".format(mode=mode, mss=mss))
                #Activa el tiempo del Timeout
                clientSocket.settimeout(timeout/1000)
                #Recive el OACK
                oack, add = clientSocket.recvfrom(2+9+3+1+2+1)
                #Desactiva el tiempo del Timeout si ha recivido el OACK
                clientSocket.settimeout(None)
                #Utilizamos una variable aux con valores de bytes.
                # 2bytes para el opcode + 9 bytes porque la palabra blocksize tiene 9
                # caracteres (1bytes/char) + 1 (byte 0)
                aux = 2 + 9 + 3 + 1
                #OACK[aux:] = el tamaño del blocksize que envia el server
                a=int.from_bytes(oack[aux:], "big")
                #El tamaño se desplaza 8 bits porque sobra 1 byte i asi podemos utilizar la variable como blocksize
                size_block=a>>8
                print("Reciviendo OACK: {oack} -> blocksize = ",size_block)
                #Una vez recivido el OACK se pone la condicion a False i sale del bucle
                recive_oack=False
            except IOError as e:
            	#No se ha recivido el OACK por lo que salta el timeout
                print("TIMEOUT DE ",timeout," segundos ACTIVO!!")
                print(e)
        
        # Una vez recibido el  OACK, podemos enviar el archivo
        try:
            # Leemos texto del archivo
            f = open("mensaje_usuario.txt", "rb")
            line = f.read(mss)
            
            # Generamos datos
            datos = op_codes["DATA"] + struct.pack('>H', numero_secuencia)
            if(isinstance(line, str)):
                datos = datos + bytes(line, "utf-8")
            else:
                datos = datos + line

            # Mientras aun haya datos en el fichero, los enviamos
            while(len(line)>0):
                # Mientras el nuemro de sequencia de los datos sea diferente al numero de sequencia de ACK, enviamos datos
                if(numero_secuencia != numero_secuencia_ack):
                    recive_ack=True
                    #Hacemos un bucle para enviar el paquete de datos i recivir el ACK 
                    #del servidor para confirmar la recepcion de los datos.Si el cliente 
                    #no recive el ACK aplica un timeout i vuelve a enviar el dato
                    while recive_ack:
                        try:
                            #Envia el paquete de datos
                            clientSocket.sendto(datos, (serverName, serverPort))
                            #Activa el tiempo del timeout
                            clientSocket.settimeout(timeout/1000)
                            print("Enviando DATOS: {nseq} --> {size_file}".format(nseq = numero_secuencia, size_file = len(line)))
                            #Recive el ack del dato enviado
                            ack, add = clientSocket.recvfrom(4)
                            #Desactiva el tiempo del timeout
                            clientSocket.settimeout(None)
                             #Una vez recivido el ACK se pone la condicion a False i sale del bucle
                            recive_ack=False
                            numero_ack = ack[3] | ack[2] << 8
                            print("Reciviendo ACK: {ack}".format(ack = numero_ack))
                        except IOError as e:
                            print("TIMEOUT DE ",timeout," segundos ACTIVO!!")
                            print(e)
                        
                # Ampliamos numero de secuencia i hacemos modulo para que no sea mas grande que 2^15
                numero_secuencia += 1
                numero_secuencia = numero_secuencia % 65535

                # si el numero de sequencia es igual a 0, lo cambiamos a 1 ya que
                # implica que no ha acabado de enviar pero el numero de seqüencia 
                #ha llegado a 0 por el modulo de 65535
                if(len(line)!=0):
                    if(numero_secuencia == 0):
                        numero_secuencia = 1

                # Si la longitud de los datos leidos es igual a la longitud de los paquetes
                #Vuelve a leer ya que implica que no ha acabado de leer.
                #Si la siguiente linea que lee esta vacia implicara que el tamaño del paquete
                # es modulo del mss
                if(len(line) == mss):
                    line = f.read(mss)
                    
                    # Generamos datos
                    datos = op_codes["DATA"] + struct.pack('>H', numero_secuencia)
                    if(isinstance(datos, str)):
                        datos = datos + bytes(line, "utf-8")
                    else:
                        datos = datos + line

                    # Si la longitud del fichero es igual a 0 --> final de lectura del fichero
                    if(len(line) == 0):
                        line = bytes()
                
                # Si la longitud de los datos leido no es igual a la longitud del mss, indica que es el ultimo paquete i que el fichero no es modulo del mss
                else:
                    print("Se ha enviado un ultimo paquete de datos con mss = {mss} i numero de sqquencia = {seq}".format(mss = len(line), seq=numero_secuencia))
                    line = f.read(len(line))
                    # Generamos datos
                    datos = op_codes["DATA"] + struct.pack('>H', numero_secuencia)
                    if(isinstance(datos, str)):
                        datos = datos + bytes(line, "utf-8")
                    else:
                        datos = datos + line
                    # Si la longitud del fichero es igual a 0
                    if(len(line) == 0):
                        line = bytes()
            
            print("Fichero enviado correctamente!")
    
        except KeyboardInterrupt:
            err = op_codes['ERR'] + err_codes['NotDefined'] + bytes('Not Defined', 'utf-8') + struct.pack('B', 0)
            clientSocket.sendto(err, (serverName, serverPort))
            print('Enviando ERROR: 1') 

        finally:
            try:
                f.close()
            except:
                pass

        clientSocket.close()

    else:
        print("\n")
        print('El MSS debe  ser potencia de 2')
        print("\n")
        err = op_codes['ERR'] + err_codes['IllegalOperation'] + bytes('MSS OUT OF RANGE', 'utf-8') + struct.pack('B', 0)
        clientSocket.sendto(err, (serverName, serverPort))
        print('Enviando ERROR: 5')


################################### PROGRAMA PRINCIPAL ###################################


# El usuario define la IP y el puerto
# Creamos la ventana emergente
root = Tk()
root.geometry("600x550")

# Titulo de la ventana
root.title('CLIENT')

# Color fondo
root['bg'] = '#03fcf0'


# Titulo TFTP
tablero = Canvas(root, width= 1000, height= 750, bg="#03fcf0")
tablero.create_text(300, 90, text="Aplicacion Fiable sobre UDP - Client", fill="black", font=('Meiryo 22 bold'))
tablero.create_text(300, 150, text="Eric Gonzalez y Jaume Perez - RETO INTERNET 2022 - 2023", fill="black", font=('Meiryo 10'))
tablero.create_text(150, 190, text="Introduce MSS", fill="black", font=('Meiryo 10 bold'))
tablero.create_text(187, 226, text="Introduce Mensaje a enviar", fill="black", font=('Meiryo 10 bold'))
tablero.create_text(192, 262, text="Introduce TimeOut en mseg", fill="black", font=('Meiryo 10 bold'))
tablero.create_text(210, 298, text="Introduce modo (octet / netaascii)", fill="black", font=('Meiryo 10 bold'))
tablero.create_text(183, 334, text="Introduce la IP (127.0.0.1)", fill="black", font=('Meiryo 10 bold'))
tablero.create_text(188, 370, text="Introduce el puerto (12001)", fill="black", font=('Meiryo 10 bold'))
tablero.pack()


# Input del MSS
mss = Text(root, height = 1, width = 20)
mss.place(x = 340, y = 180)


# Input del nombre_fichero
mensaje = Text(root, height = 1, width = 20)
mensaje.place(x = 340, y = 216)


# Input del TimeOut
Timeout = Text(root, height = 1, width = 20)
Timeout.place(x = 340, y = 252)


# Input del modo
modo = Text(root, height = 1, width = 20)
modo.place(x = 340, y = 288)

# Input de la IP
ip = Text(root, height = 1, width = 20)
ip.place(x = 340, y = 324)

# Input del puerto
puerto = Text(root, height = 1, width = 20)
puerto.place(x = 340, y = 360)



# Creamos boton de enviar
boton_get = Button(root, text = 'ENVIAR', height = 3, width = 20, command = partial(put, mss, mensaje, modo, Timeout, ip, puerto))
boton_get.place(x = 220, y = 420)


# Boton para cerrar
exit = Button(root, text="Exit", height= 1, width= 10, command=root.destroy)
exit.place(x = 450, y = 492)

root.mainloop()

