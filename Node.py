import socket
import threading
import time
import random

MIN_DELAY_OUT = 1
MAX_DELAY_OUT = 5
MIN_DELAY_IN = 1
MAX_DELAY_IN = 2


class Node(threading.Thread):

    ''' Constructeur'''
    def __init__(self,num_process,NB_NODES,LIST_PORTS,LIST_ADDR,barrier,gui):

        threading.Thread.__init__(self)

        ''' Une référence vers le GUI '''
        self.gui = gui
        self.barrier = barrier

        ''' Constantes '''
        self.NB_NODES = NB_NODES
        self.LIST_PORTS = LIST_PORTS
        self.LIST_ADDR = LIST_ADDR

        ''' Les variables vus en cours '''
        self.num_process = num_process
        self.osn = 0
        self.hsn = 0
        self.nb_rep_attendues = 0
        self.sc_demande = False
        self.dedans = False
        self.rep_differe = []
        for i in range(self.NB_NODES):
            self.rep_differe.append(False)

        ''' Les sockets '''
        self.server_socket = None  # la socket serveur
        self.client_socket = []  # liste des connexions socket établies avec les autres serveurs

    ''' Envoyer requête '''
    def send_request(self, num_server):
        request = f'req,{self.osn},{self.num_process}'
        self.client_socket[num_server].send(request.encode())
        print(f"{self.num_process + 1} envoie ({request}) à {num_server + 1}")

    ''' Envoyer réponse '''
    def send_reply(self, num_server):
        reply = 'rep'
        self.client_socket[num_server].send(reply.encode())
        print(f"{self.num_process + 1} envoie ({reply}) à {num_server + 1}")

    ''' Méthode à exécuter infiniment pour écouter les messages des clients '''
    def receive_message(self, conn_socket):
        while True:
            while self.gui.pause:
                time.sleep(0.01)
            donnee = conn_socket.recv(1024)
            if not donnee:
                continue
            message = donnee.decode().split(',')
            if(len(message) == 0):
                continue

            # Réception d'une requête
            if(message[0] == 'req'):
                k = int(message[1])
                j = int(message[2])
                self.hsn = max(self.hsn, k) + 1
                priorite = self.sc_demande and (k > self.osn or (k == self.osn and self.num_process < j))
                if priorite:
                    self.rep_differe[j] = True
                else:
                    self.send_reply(j)

            # Réception d'une réponse
            if(message[0] == 'rep'):
                self.nb_rep_attendues = self.nb_rep_attendues - 1

            self.gui.update(self.num_process)


    ''' Corps principal du processus '''
    def run(self):

        # Création de la socket serveur
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.LIST_ADDR[self.num_process], self.LIST_PORTS[self.num_process]))
        self.server_socket.listen(self.NB_NODES - 1)  # Nombre maximal de connexions en attente

        # Création des sockets clients et connexion avec les autres serveurs
        for i in range(self.NB_NODES):
            if (i != self.num_process):
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((self.LIST_ADDR[i], self.LIST_PORTS[i]))
                self.client_socket.append(conn)
            else:
                self.client_socket.append(None)

        # Création des sockets connexions avec les autres clients et des threads pour gérer chaque connexion
        for i in range (self.NB_NODES - 1):
            conn_socket, client_address = self.server_socket.accept()
            threading.Thread(target=self.receive_message, args=(conn_socket,)).start()

        # Patienter jusqu'à ce que toutes les connexions sockets sont établies
        self.barrier.wait()

        # Boucle principale
        while(True):

            # Patienter si le programme est en pause
            while self.gui.pause:
                time.sleep(0.01)

            # Attendre un délai avant de désirer entrer en section critique
            time_to_sleep = random.uniform(MIN_DELAY_OUT, MAX_DELAY_OUT)
            time_start = time.time()
            time.sleep(time_to_sleep)
            while self.gui.pause:
                time.sleep(0.01)
            while self.gui.date_pause > time_start:
                time_to_sleep = time_to_sleep - (self.gui.date_pause - time_start)
                time_start = time.time()
                time.sleep(time_to_sleep)
                while self.gui.pause:
                    time.sleep(0.01)


            self.sc_demande = True
            self.osn = self.hsn
            self.nb_rep_attendues = self.NB_NODES - 1

            # Mise à jour du GUI
            self.gui.update_color(self.num_process)
            self.gui.update(self.num_process)

            # Patienter si le programme est en pause
            while self.gui.pause:
                time.sleep(0.01)

            # envoyer une requêtes à tous les autres processus
            for process in range(self.NB_NODES):
                if (process != self.num_process):
                    self.send_request(process)
                # Patienter si le programme est en pause
                while self.gui.pause:
                    time.sleep(0.01)

            # attendre des réponses depuis tous les autres processus
            while (self.nb_rep_attendues != 0):
                time.sleep(0.01)

            # Patienter si le programme est en pause
            while self.gui.pause:
                time.sleep(0.01)

            # Entrée en section critique
            self.dedans = True

            # Mise à jour du GUI
            self.gui.update_color(self.num_process)
            self.gui.update_sc(str(self.num_process + 1))
            print(f"processus {self.num_process + 1} entre en section critique \n")

            # Attendre un délai dans la section critique
            time_to_sleep = random.uniform(MIN_DELAY_IN, MAX_DELAY_IN)
            time_start = time.time()
            time.sleep(time_to_sleep)
            while self.gui.pause:
                time.sleep(0.01)
            while self.gui.date_pause > time_start:
                time_to_sleep = time_to_sleep - (self.gui.date_pause - time_start)
                time_start = time.time()
                time.sleep(time_to_sleep)
                while self.gui.pause:
                    time.sleep(0.01)

            # Sortie de la section critique
            self.sc_demande = False
            self.dedans = False

            # Mise à jour du GUI
            self.gui.update_color(self.num_process)
            self.gui.update_sc('')
            print(f"processus {self.num_process + 1} sort de la section critique \n")

            # Patienter si le programme est en pause
            while self.gui.pause:
                time.sleep(0.01)

            # envoyer les réponses différées
            for process in range(self.NB_NODES):
                if self.rep_differe[process]:
                    self.rep_differe[process] = False
                    self.send_reply(process)
                # Patienter si le programme est en pause
                while self.gui.pause:
                    time.sleep(0.01)

            # Mise à jour du GUI
            self.gui.update(self.num_process)
