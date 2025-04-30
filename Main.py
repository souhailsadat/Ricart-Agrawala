from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QStyleFactory,QLineEdit
from PyQt5 import Qt,QtGui
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from time import time,sleep
from threading import Barrier,Lock

if __name__ == "__main__":
    from Node import Node

''' variables globales '''
NB_NODES = 10
LIST_NODES = []
LIST_PORTS = []
LIST_ADDR = []
PORT_INIT = 4000


class GUI(QMainWindow):

    ''' Corps principal du GUI '''
    def __init__(self):
        super(GUI, self).__init__()
        loadUi("Gui.ui", self)
        self.setWindowTitle("Ricart & Agrawala 81")
        self.lineEdit.setReadOnly(True)
        self.actif.setReadOnly(True)
        self.attente.setReadOnly(True)
        self.critique.setReadOnly(True)
        self.lineEdit.setFocusPolicy(Qt.NoFocus)
        self.actif.setFocusPolicy(Qt.NoFocus)
        self.attente.setFocusPolicy(Qt.NoFocus)
        self.critique.setFocusPolicy(Qt.NoFocus)
        self.attente.setStyleSheet("QLineEdit { background: rgb(230, 205, 255);}")
        self.critique.setStyleSheet("QLineEdit { background: rgb(255, 238, 205);}")
        self.tableWidget.horizontalHeader().setFixedHeight(25)
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 100)
        self.tableWidget.setColumnWidth(2, 120)
        self.tableWidget.setColumnWidth(3, 120)
        self.tableWidget.setColumnWidth(4, 340)
        self.tableWidget.setColumnWidth(5, 70)
        self.tableWidget.setColumnWidth(6, 70)
        self.tableWidget.setFocusPolicy(Qt.NoFocus)
        self.pushButton.clicked.connect(self.clickButton)
        self.lock = Lock()
        self.create_nodes()
        self.init()
        self.pause = False  # variable pour indiquer si le programme est en pause
        self.date_pause = 0  # stocker la date de la dernière pause
        self.start_nodes()

    ''' Modifier le processus en section critique dans le GUI '''
    def update_sc(self,text):
        self.lock.acquire()
        sleep(0.1)
        self.lineEdit.setText(text)
        self.lock.release()

    ''' Modifier les couleurs des processus dans le GUI '''
    def update_color(self,num_process):
        scdemande = LIST_NODES[num_process].sc_demande
        dedans = LIST_NODES[num_process].dedans
        if dedans:
            color = QtGui.QColor(255,238,205)
        elif scdemande:
            color = QtGui.QColor(230,205,255)
        else:
            color = QtGui.QColor(255,255,255)
        for col in range(7):
            self.tableWidget.item(num_process, col).setBackground(color)
        self.tableWidget.setVisible(False)
        self.tableWidget.setVisible(True)
        self.tableWidget.setFocusPolicy(Qt.NoFocus)

    ''' Méthode à exécuter quand le bouton est appuyé '''
    def clickButton(self):
        if self.pushButton.text() == "Pause":
            self.pause = True
            self.date_pause = time()
            self.pushButton.setText("Reprendre")
        else:
            self.pause = False
            self.pushButton.setText("Pause")

    ''' Initialiser les valeurs du tableau '''
    def init(self):
        self.lineEdit.setText('')
        for i in range(NB_NODES):
            # num_process
            item = QTableWidgetItem(str(i + 1))
            item.setFlags(Qt.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignCenter)
            self.tableWidget.setItem(i,0,item)
            # sc_demande
            item = QTableWidgetItem(str(False))
            item.setFlags(Qt.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignCenter)
            self.tableWidget.setItem(i,1,item)
            # nb_rep_attendues
            item = QTableWidgetItem(str(0))
            item.setFlags(Qt.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignCenter)
            self.tableWidget.setItem(i,2,item)
            # nb_rep_differe
            item = QTableWidgetItem(str(0))
            item.setFlags(Qt.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignCenter)
            self.tableWidget.setItem(i,3,item)
            # tab_rep_differe
            item = QTableWidgetItem('Aucune')
            item.setFlags(Qt.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignCenter)
            self.tableWidget.setItem(i,4,item)
            # estampille
            item = QTableWidgetItem(str(0))
            item.setFlags(Qt.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignCenter)
            self.tableWidget.setItem(i,5,item)
            # horloge
            item = QTableWidgetItem(str(0))
            item.setFlags(Qt.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignCenter)
            self.tableWidget.setItem(i,6,item)

    ''' Modifier les valeurs dans le tableau '''
    def update(self,num_process):
        node = LIST_NODES[num_process]
        i = num_process
        # num_process
        self.tableWidget.item(i, 0).setText(str(i + 1))
        # sc_demande
        self.tableWidget.item(i, 1).setText(str(node.sc_demande))
        # nb_rep_attendues
        self.tableWidget.item(i, 2).setText(str(node.nb_rep_attendues))
        # rep différées
        nb_rep_diff = 0
        rep_diff = ''
        for rep in range(NB_NODES):
            if node.rep_differe[rep]:
                nb_rep_diff += 1
                rep_diff += str(rep + 1) + ", "
        if rep_diff == '':
            rep_diff = "Aucune"
        # nb_rep_differe
        self.tableWidget.item(i, 3).setText(str(nb_rep_diff))
        # tab_rep_differe
        self.tableWidget.item(i, 4).setText(rep_diff)
        # estampille
        self.tableWidget.item(i, 5).setText(str(node.osn))
        # horloge
        self.tableWidget.item(i, 6).setText(str(node.hsn))

        self.tableWidget.setVisible(False)
        self.tableWidget.setVisible(True)
        self.tableWidget.setFocusPolicy(Qt.NoFocus)


    ''' Créer les processus '''
    def create_nodes(self):

        # initialiser la liste des ports et des adresses IP
        for i in range(NB_NODES):
            port = PORT_INIT + i
            LIST_PORTS.append(port)
            LIST_ADDR.append('127.0.0.1')

        # instancier un thread pour chaque processus
        self.barrier = Barrier(NB_NODES)
        for num_process in range(NB_NODES):
            p = Node(num_process,NB_NODES,LIST_PORTS,LIST_ADDR,self.barrier,self)
            LIST_NODES.append(p)

    ''' Démarrer les threads des processus '''
    def start_nodes(self):

        for process in LIST_NODES:
            process.start()



if __name__ == "__main__":
    app = QApplication([])
    app.setStyle(QStyleFactory.create("Fusion"))
    widget = GUI()
    widget.show()
    app.exec()