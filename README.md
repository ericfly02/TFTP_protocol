## TO-DO LIST:
- [X] Se debe desarrollar una aplicación que envíe N paquetes numerados de 1 a N, y que asegure que llegan todos los paquetes sin duplicaciones. 
- [X] La aplicación debe utilizar UDP (un protocolo sin fiabilidad) como protocolo de transporte pero implementando el protocolo Stop & Wait para que la comunicación sea fiable y permita la retransmisión en caso de pérdida de un paquete.
- [X] En este protocolo se envía un paquete y se espera su confirmación (ACK), si no llega transcurrido un “time out” se realiza una retransmisión.
- [ ] Para comprobar el funcionamiento del sistema, se debe añadir un módulo a la aplicación que permita simular que un paquete se pierde (esto es con cierta probabilidad no se envía uno de los N paquetes), esto también se debe considerar en el otro extremo (es decir, también hay que considerar la posibilidad de que un ACK se pierda).
- [X] También hay que considerar como indicar el primer paquete del mensaje y el último paquete (o cuantos paquetes se enviaran)

# TFTP-Internet-assigment-
