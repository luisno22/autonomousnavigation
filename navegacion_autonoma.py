# Luis Nolasco Ramirez
#
# Codigo que permite a un robot avanzar de forma autonoma por una sala evitando objetos
# Utilizado para diferentes tecnicas de mapeado de salas o patrullaje de zonas
# 


import rospy
import numpy as np
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Point
from geometry_msgs.msg import PoseWithCovariance
from geometry_msgs.msg import Pose
from nav_msgs.msg import Odometry
import sys


def callback(msg): 
    # El mensaje es del tipo LaseScan que contiene un campo llamado ranges el cual almacena las mediciones del sensor laser
    # Se trata de un laser que capta la distancia a la que encuentra un objeto en linea recta, dicho laser se encuentra girando
    # alrededor del mismo punto, recibiendo de esta forma una lectura de las mediciones de distancia en los 360 grados
    # Su rango maximo es de 1 metro, para lecturas superiores devuelve un valor infinito
    cmd = Twist()

    media_fr = 0.0
    media_fl = 0.0

    k = 0
    c = 0
    # Se emplean solo los valores correspondientes a las lecturas de la zona delantera
    # Hayandose estas en los primeros y los ultimos valores de medicion del laser
    # En este caso se utiliza la primera sexta parte y la ultima sexta parte de los valores
    # Se hace la media de ambos tramos obteniendo asi la media de la parte delantera derecha (media_fr)
    # y de la parte delantera izquierda (media_fl)
    # Si alguna laectura == nan, se sustituye por 0
    lecturas = len(msg.ranges)
    for i in msg.ranges:     
        if k < lecturas/6:
            if np.isinf(i):
                i = 1.0
            media_fl += i
        elif k > lecturas/1.2:
            if np.isinf(i):
                i = 1.0
            media_fr += i
        
        k += 1
    
    media_fr = media_fr/(lecturas/6)
    media_fl = media_fl/(lecturas/6)

    shortest_f = min(media_fr,media_fl)

    cmd.linear.x = 0.5

    # Si la distancia es inferior a 0.5 metros gira rapidamente en la direccion correspondiente para evitar el choque y pone la velocidad a 0
    if shortest_f < 0.5:
        cmd.linear.x = 0.0
        if shortest_f == media_fr:
            cmd.angular.z = 0.3
        else:
            cmd.angular.z = -0.3
    # Si la distancia es inferior a 1 metro gira lentamente en la direccion correspondiente para evitar el choque y pone la velocidad a 0.2
    elif shortest_f < 1.0:
        cmd.linear.x = 0.2
        if media_fr < media_fl:
            cmd.angular.z = 0.1
        else:
            cmd.angular.z = -0.1
    
    
    print('media dcha: ',media_fr)
    print('media izq: ',  media_fl)
    print('Mas pequeño: ',shortest_f)
    print("Vel (v,w): ", cmd.linear.x, cmd.angular.z)
    print('----------------------------------------')

    pub.publish(cmd)

    cmd.linear.x = 0.0
    cmd.angular.z = 0.0
    

if __name__ == "__main__":

    publisher_topic = '/tb3/cmd_vel'
    subscriber_topic =' /tb3/scan'
    rospy.init_node('algoritmo_control_tb3_0')
    pub = rospy.Publisher(publisher_topic,Twist,queue_size = 5)
    sub = rospy.Subscriber(subscriber_topic, LaserScan, callback)

    rospy.spin()
