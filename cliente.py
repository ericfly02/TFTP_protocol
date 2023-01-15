
# TEORIA: Estructura de los paquetes a enviar

# DATA:
#	| 2 bytes | 2 bytes | n bytes |
# 	----------------------------------
# 	| Opcode  | Block # |  Data   |
# 	----------------------------------

# WRQ:
#	| 2 bytes | string   | 1 byte | string | 1 byte |
# 	--------------------------------------------------
# 	| Opcode  | Filename |   0    |  Mode  |   0    |
# 	--------------------------------------------------

# ACK:
#	| 2 bytes | 2 bytes | 
# 	---------------------
# 	| Opcode  | Block # |  
# 	---------------------

# OACK:
#	| 2 bytes |  2 bytes  | 1 byte |  1 byte |
# 	-----------------------------------------
# 	| Opcode  |  Opcio 1  |   0    | Value 1 |
# 	-----------------------------------------

# Importamos las librerias necesarias
from functools import partial
from tkinter import *
import random
from socket import *
import time
import struct
import math
import sys


############################## FUNCIONES AUXILIARES #######################################

def Log2(x):
    return (math.log10(x) /
            math.log10(2))
 
# indica si el numero n es una potencia de 2^k siendo k un numero del 3 al 11
def es_potencia(n):
    return (math.ceil(Log2(n)) == math.floor(Log2(n)))


################################### PUT ###################################

def put(mss, mensaje, Timeout, ip, puerto, probabilidad_fallo):

    #Inicializamos el servername i el serverport
    serverName = 'localhost'
    serverPort = 12001
    numero_secuencia = 1 # Inicializamos el numero de secuencia a 1
    numero_secuencia_ack =  0 # Inicializamos el numero de secuencia a 0

    #Almacena los datos recogidos en la GUI en variables
    mss = int(mss.get("1.0", "end-1c"))
    mensaje = mensaje.get("1.0", "end-1c")
    timeout = int(Timeout.get("1.0", "end-1c"))
    serverName = ip.get("1.0", "end-1c")
    serverPort = int(puerto.get("1.0", "end-1c"))
    probabilidad_fallo = float(probabilidad_fallo.get("1.0", "end-1c"))*0.01

    # Guardamos el mensaje del usuario en un fichero txt
    fichero = open("mensaje_usuario.txt", "w")
    fichero.write(mensaje)
    fichero.close()

    # Crear socket  
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    # Gracias a la funcion struct, podremos crear el paquete
    op_codes = {
        "DATA": struct.pack('BB', 0, 3),
    }

    #Comprueba que el valor de mss sea correcto
    if(es_potencia(mss)):

        # Enviamos primer paquete indicando el blocksize
        primer_paquete = bytes('blocksize', "utf-8") + struct.pack('B', 0) + struct.pack('>H', mss)+ struct.pack('B', 0)

        # Enviamos el primer paquete indicando el mss i recivimos el OACK del servidor para confirmar la conexion.
        # Si el cliente no recive el OACK aplica un timeout i vuelve a enviar el primer paquete
 
        try:
            # Se envía el paquete WRQ al servidor especificando el nombre del servidor y el puerto de destino.              
            clientSocket.sendto(primer_paquete, (serverName, serverPort))
            print("Enviando siguiente paquete: (blocksize, {})".format(mss))
            # Se activa el temporizador de tiempo de espera para el socket del cliente, se divide el valor de timeout (en milisegundos) entre 1000 para convertirlo a segundos.
            clientSocket.settimeout(timeout/1000)
            # se recibe el paquete OACK del servidor, se guarda en la variable "oack" y se guarda la dirección del servidor en la variable "add"
            oack, add = clientSocket.recvfrom(1024)
            #  se desactiva el temporizador de tiempo de espera del socket del cliente.
            clientSocket.settimeout(None)
            # se utiliza la función index para obtener la posición de la cadena "blocksize" en el paquete OACK, se suma 9 para obtener la posición del tamaño de bloque, se utiliza int.from_bytes para convertir el tamaño de bloque en un entero y se desplaza 8 bits (>>8) para eliminar el byte adicional.
            size_block = int.from_bytes(oack[oack.index(b'blocksize')+9:], "big") >> 8
            print("Reciviendo OACK: {oack} -> blocksize = ",size_block)


        except IOError as e:
            #No se ha recivido el OACK por lo que salta el timeout
            print("TIMEOUT DE ",timeout," segundos ACTIVO!!")
            print(e)
    
        # Una vez recibido el  OACK, podemos enviar el archivo

        # Leemos texto del archivo
        f = open("mensaje_usuario.txt", "rb")
        line = f.read(mss)
        
        # Generamos datos
        # Crear un paquete de datos con el opcode "DATA" y el número de secuencia actual (numero_secuencia)
        # El opcode "DATA" indica al servidor que este paquete contiene datos para ser almacenados
        # El número de secuencia es utilizado para identificar cada bloque de datos y para asegurar que los 
        # datos son recibidos correctamente
        datos = op_codes["DATA"] + struct.pack('>H', numero_secuencia)

        # Comprueba si los datos son una cadena de caracteres.
        if(isinstance(datos, str)):
            # Si los datos son una cadena de caracteres se convierten a bytes utilizando la función bytes y 
            # se añaden al paquete de datos
            datos = datos + bytes(line, "utf-8")
        else:
            # Si los datos no son una cadena de caracteres se añaden directamente al paquete de datos
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
                        # Miramos mediante la libreria random, si un paquete se ha perdido
                        if (random.random() < probabilidad_fallo):
                            print(('PAQUETE DATOS PERDIDO NUMERO: {}').format(numero_secuencia))
                        else:
                            try:
                                # Envia el paquete de datos
                                clientSocket.sendto(datos, (serverName, serverPort))
                                # Activa el tiempo del timeout
                                clientSocket.settimeout(timeout/1000)
                                print("Enviando DATOS: {nseq} --> {size_file}".format(nseq = numero_secuencia, size_file = len(line)))
                                # Recive el ack del dato enviado
                                ack, add = clientSocket.recvfrom(4)
                                # Desactiva el tiempo del timeout
                                clientSocket.settimeout(None)
                                # Una vez recivido el ACK se pone la condicion a False i sale del bucle
                                recive_ack=False
                                # Utilizamos operadores de bits para extraer el número de secuencia del paquete de confirmación (ACK) recibido. 
                                # El número de secuencia se encuentra en los bytes 2 y 3 del paquete. La operación "ack[2] << 8" desplaza el byte 2 8 bits a 
                                # la izquierda y "ack[3] | ack[2] << 8" combina los dos bytes para obtener el número de secuencia completo.
                                numero_ack = ack[3] | ack[2] << 8
                                print("Reciviendo ACK: {ack}".format(ack = numero_ack))

                            except ConnectionResetError as e:
                                print("Se ha enviado un ultimo paquete de datos con mss = {mss} i numero de sequencia = {seq}".format(mss = len(line), seq=numero_secuencia))
                                print("Fichero enviado correctamente!")
                                sys.exit()    

                    except IOError as e:
                        print("TIMEOUT DE ",timeout," segundos ACTIVO!!")
                        time.sleep(timeout/1000)
                        print(e)
                    
            # Ampliamos numero de secuencia i hacemos modulo para que no sea mas grande que 2^15
            numero_secuencia += 1
            numero_secuencia = numero_secuencia % 65535

            # Si el numero de sequencia es igual a 0, lo cambiamos a 1 ya que
            # implica que no ha acabado de enviar pero el numero de seqüencia 
            # ha llegado a 0 por el modulo de 65535
            if(len(line)!=0):
                if(numero_secuencia == 0):
                    numero_secuencia = 1

            # Si la longitud de los datos leidos es igual a la longitud de los paquetes
            # Vuelve a leer ya que implica que no ha acabado de leer.
            # Si la siguiente linea que lee esta vacia implicara que el tamaño del paquete
            # es modulo del mss
            if(len(line) == mss):
                line = f.read(mss)
                
               # Generamos datos
               # Crear un paquete de datos con el opcode "DATA" y el número de secuencia actual (numero_secuencia)
               # El opcode "DATA" indica al servidor que este paquete contiene datos para ser almacenados
               # El número de secuencia es utilizado para identificar cada bloque de datos y para asegurar que los 
               # datos son recibidos correctamente
                datos = op_codes["DATA"] + struct.pack('>H', numero_secuencia)

                # Comprueba si los datos son una cadena de caracteres.
                if(isinstance(datos, str)):
                    # Si los datos son una cadena de caracteres se convierten a bytes utilizando la función bytes y 
                    # se añaden al paquete de datos
                    datos = datos + bytes(line, "utf-8")
                else:
                    # Si los datos no son una cadena de caracteres se añaden directamente al paquete de datos
                    datos = datos + line

                # Si la longitud del fichero es igual a 0 --> final de lectura del fichero
                if(len(line) == 0):
                    line = bytes()
            
            # Si la longitud de los datos leido no es igual a la longitud del mss, indica que es el ultimo paquete i 
            # que el fichero no es modulo del mss
            else:
                print("Se ha enviado un ultimo paquete de datos con mss = {mss} i numero de sequencia = {seq}".format(mss = len(line), seq=numero_secuencia))
                print("Fichero enviado correctamente!")
                sys.exit()    

        try:
            f.close()
        except:
            pass

        clientSocket.close()

    else:
        print("\n")
        print('ERROR: El MSS debe ser potencia de 2')
        print("\n")



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
tablero.create_text(190, 226, text="Introduce Mensaje a enviar", fill="black", font=('Meiryo 10 bold'))
tablero.create_text(192, 262, text="Introduce TimeOut en mseg", fill="black", font=('Meiryo 10 bold'))
tablero.create_text(215, 298, text="Introduce probabilidad de fallo (50)", fill="black", font=('Meiryo 10 bold'))
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


# Input de la probabilidad de fallo
probabilidad = Text(root, height = 1, width = 20)
probabilidad.place(x = 340, y = 288)

# Input de la IP
ip = Text(root, height = 1, width = 20)
ip.place(x = 340, y = 324)

# Input del puerto
puerto = Text(root, height = 1, width = 20)
puerto.place(x = 340, y = 360)




# Creamos boton de enviar
boton_get = Button(root, text = 'ENVIAR', height = 3, width = 20, command = partial(put, mss, mensaje, Timeout, ip, puerto, probabilidad))
boton_get.place(x = 220, y = 420)


# Boton para cerrar
exit = Button(root, text="Exit", height= 1, width= 10, command=root.destroy)
exit.place(x = 450, y = 492)

root.mainloop()

