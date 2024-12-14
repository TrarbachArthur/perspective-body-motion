import sys
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QPushButton,QGroupBox
from PyQt5.QtGui import QDoubleValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D, art3d
import numpy as np

from math import pi, cos, sin
from model import Model
from camera import Camera
###### Crie suas funções de translação, rotação, criação de referenciais, plotagem de setas e qualquer outra função que precisar

def set_axes_equal(ax):
        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()

        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = np.mean(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = np.mean(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = np.mean(z_limits)

        plot_radius = 0.5*max([x_range, y_range, z_range])

        ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
        ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
        ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])

def set_plot(ax=None,figure = None,lim=[-2,2]):
    if figure ==None:
        figure = plt.figure(figsize=(8,8))
    if ax==None:
        ax = plt.axes(projection='3d')

    ax.set_title("camera reference")
    ax.set_xlim(lim)
    ax.set_xlabel("x axis")
    ax.set_ylim(lim)
    ax.set_ylabel("y axis")
    ax.set_zlim(lim)
    ax.set_zlabel("z axis")
    return ax

#adding quivers to the plot
def draw_arrows(point,base,axis,length=1.5):
    # The object base is a matrix, where each column represents the vector
    # of one of the axis, written in homogeneous coordinates (ax,ay,az,0)

    quivers = []

    # Plot vector of x-axis
    quivers.append(axis.quiver(point[0],point[1],point[2],base[0,0],base[1,0],base[2,0],color='red',pivot='tail',  length=length))
    # Plot vector of y-axis
    quivers.append(axis.quiver(point[0],point[1],point[2],base[0,1],base[1,1],base[2,1],color='green',pivot='tail',  length=length))
    # Plot vector of z-axis
    quivers.append(axis.quiver(point[0],point[1],point[2],base[0,2],base[1,2],base[2,2],color='blue',pivot='tail',  length=length))

    return quivers


### Setting printing options
np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
np.set_printoptions(precision=3,suppress=True)

def z_rotate(angle):
    angle = np.deg2rad(angle)

    return np.array([[cos(angle), -sin(angle), 0, 0],
                    [sin(angle), cos(angle), 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1 ]])

def x_rotate(angle):
    angle = np.deg2rad(angle)

    return np.array([[1, 0, 0, 0],
                    [0, cos(angle), -sin(angle), 0],
                    [0, sin(angle), cos(angle), 0],
                    [0, 0, 0, 1 ]])

def y_rotate(angle):
    angle = np.deg2rad(angle)

    return np.array([[cos(angle), 0, sin(angle), 0],
                    [0, 1, 0, 0],
                    [-sin(angle), 0, cos(angle), 0],
                    [0, 0, 0, 1]])

def translate(dx, dy, dz):
    return np.array([[1, 0, 0, dx],
                    [0, 1, 0, dy],
                    [0, 0, 1, dz],
                    [0, 0, 0, 1]])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #definindo as variaveis
        self.set_variables()
        #Ajustando a tela    
        self.setWindowTitle("Grid Layout")
        self.setGeometry(100, 100,1280 , 720)
        self.setup_ui()

    def set_variables(self):
        self.model = Model("gengar.stl")
        self.cam_original = Camera()
        self.cam = Camera() 
        # self.px_base = 1280  #modificar
        # self.px_altura = 720 #modificar
        # self.dist_foc = 50 #modificar
        # self.stheta = 0 #modificar
        # self.ox = self.px_base/2 #modificar
        # self.oy = self.px_altura/2 #modificar
        # self.ccd = [36,24] #modificar
        # self.projection_matrix = [] #modificar
        
    def setup_ui(self):
        # Criar o layout de grade
        grid_layout = QGridLayout()

        # Criar os widgets
        line_edit_widget1 = self.create_world_widget("Ref mundo")
        line_edit_widget2  = self.create_cam_widget("Ref camera")
        line_edit_widget3  = self.create_intrinsic_widget("params instr")

        self.canvas = self.create_matplotlib_canvas()

        # Adicionar os widgets ao layout de grade
        grid_layout.addWidget(line_edit_widget1, 0, 0)
        grid_layout.addWidget(line_edit_widget2, 0, 1)
        grid_layout.addWidget(line_edit_widget3, 0, 2)
        grid_layout.addWidget(self.canvas, 1, 0, 1, 3)

          # Criar um widget para agrupar o botão de reset
        reset_widget = QWidget()
        reset_layout = QHBoxLayout()
        reset_widget.setLayout(reset_layout)

        # Criar o botão de reset vermelho
        reset_button = QPushButton("Reset")
        reset_button.setFixedSize(50, 30)  # Define um tamanho fixo para o botão (largura: 50 pixels, altura: 30 pixels)
        style_sheet = """
            QPushButton {
                color : white ;
                background: rgba(255, 127, 130,128);
                font: inherit;
                border-radius: 5px;
                line-height: 1;
            }
        """
        reset_button.setStyleSheet(style_sheet)
        reset_button.clicked.connect(self.reset_canvas)

        # Adicionar o botão de reset ao layout
        reset_layout.addWidget(reset_button)

        # Adicionar o widget de reset ao layout de grade
        grid_layout.addWidget(reset_widget, 2, 0, 1, 3)

        # Criar um widget central e definir o layout de grade como seu layout
        central_widget = QWidget()
        central_widget.setLayout(grid_layout)
        
        # Definir o widget central na janela principal
        self.setCentralWidget(central_widget)

    def create_intrinsic_widget(self, title):
        # Criar um widget para agrupar os QLineEdit
        line_edit_widget = QGroupBox(title)
        line_edit_layout = QVBoxLayout()
        line_edit_widget.setLayout(line_edit_layout)

        # Criar um layout de grade para dividir os QLineEdit em 3 colunas
        grid_layout = QGridLayout()

        line_edits = []
        labels = ['n_pixels_base:', 'n_pixels_altura:', 'ccd_x:', 'ccd_y:', 'dist_focal:', 'sθ:']  # Texto a ser exibido antes de cada QLineEdit

        # Adicionar widgets QLineEdit com caixa de texto ao layout de grade
        for i in range(1, 7):
            line_edit = QLineEdit()
            label = QLabel(labels[i-1])
            validator = QDoubleValidator()  # Validador numérico
            line_edit.setValidator(validator)  # Aplicar o validador ao QLineEdit
            grid_layout.addWidget(label, (i-1)//2, 2*((i-1)%2))
            grid_layout.addWidget(line_edit, (i-1)//2, 2*((i-1)%2) + 1)
            line_edits.append(line_edit)

        # Criar o botão de atualização
        update_button = QPushButton("Atualizar")

        ##### Você deverá criar, no espaço reservado ao final, a função self.update_params_intrinsc ou outra que você queira 
        # Conectar a função de atualização aos sinais de clique do botão
        update_button.clicked.connect(lambda: self.update_params_intrinsc(line_edits))

        # Adicionar os widgets ao layout do widget line_edit_widget
        line_edit_layout.addLayout(grid_layout)
        line_edit_layout.addWidget(update_button)

        # Retornar o widget e a lista de caixas de texto
        return line_edit_widget
    
    def create_world_widget(self, title):
        # Criar um widget para agrupar os QLineEdit
        line_edit_widget = QGroupBox(title)
        line_edit_layout = QVBoxLayout()
        line_edit_widget.setLayout(line_edit_layout)

        # Criar um layout de grade para dividir os QLineEdit em 3 colunas
        grid_layout = QGridLayout()

        line_edits = []
        labels = ['X(move):', 'X(angle):', 'Y(move):', 'Y(angle):', 'Z(move):', 'Z(angle):']  # Texto a ser exibido antes de cada QLineEdit

        # Adicionar widgets QLineEdit com caixa de texto ao layout de grade
        for i in range(1, 7):
            line_edit = QLineEdit()
            label = QLabel(labels[i-1])
            validator = QDoubleValidator()  # Validador numérico
            line_edit.setValidator(validator)  # Aplicar o validador ao QLineEdit
            grid_layout.addWidget(label, (i-1)//2, 2*((i-1)%2))
            grid_layout.addWidget(line_edit, (i-1)//2, 2*((i-1)%2) + 1)
            line_edits.append(line_edit)

        # Criar o botão de atualização
        update_button = QPushButton("Atualizar")

        ##### Você deverá criar, no espaço reservado ao final, a função self.update_world ou outra que você queira 
        # Conectar a função de atualização aos sinais de clique do botão
        update_button.clicked.connect(lambda: self.update_world(line_edits))

        # Adicionar os widgets ao layout do widget line_edit_widget
        line_edit_layout.addLayout(grid_layout)
        line_edit_layout.addWidget(update_button)

        # Retornar o widget e a lista de caixas de texto
        return line_edit_widget

    def create_cam_widget(self, title):
        # Criar um widget para agrupar os QLineEdit
        line_edit_widget = QGroupBox(title)
        line_edit_layout = QVBoxLayout()
        line_edit_widget.setLayout(line_edit_layout)

        # Criar um layout de grade para dividir os QLineEdit em 3 colunas
        grid_layout = QGridLayout()

        line_edits = []
        labels = ['X(move):', 'X(angle):', 'Y(move):', 'Y(angle):', 'Z(move):', 'Z(angle):']  # Texto a ser exibido antes de cada QLineEdit

        # Adicionar widgets QLineEdit com caixa de texto ao layout de grade
        for i in range(1, 7):
            line_edit = QLineEdit()
            label = QLabel(labels[i-1])
            validator = QDoubleValidator()  # Validador numérico
            line_edit.setValidator(validator)  # Aplicar o validador ao QLineEdit
            grid_layout.addWidget(label, (i-1)//2, 2*((i-1)%2))
            grid_layout.addWidget(line_edit, (i-1)//2, 2*((i-1)%2) + 1)
            line_edits.append(line_edit)

        # Criar o botão de atualização
        update_button = QPushButton("Atualizar")

        ##### Você deverá criar, no espaço reservado ao final, a função self.update_cam ou outra que você queira 
        # Conectar a função de atualização aos sinais de clique do botão
        update_button.clicked.connect(lambda: self.update_cam(line_edits))

        # Adicionar os widgets ao layout do widget line_edit_widget
        line_edit_layout.addLayout(grid_layout)
        line_edit_layout.addWidget(update_button)

        # Retornar o widget e a lista de caixas de texto
        return line_edit_widget

    def create_matplotlib_canvas(self):
        # Criar um widget para exibir os gráficos do Matplotlib
        canvas_widget = QWidget()
        canvas_layout = QHBoxLayout()
        canvas_widget.setLayout(canvas_layout)

        # Criar um objeto FigureCanvas para exibir o gráfico 2D
        self.fig1, self.ax1 = plt.subplots()
        self.ax1.set_title("Imagem")
        self.canvas1 = FigureCanvas(self.fig1)

        ##### Falta acertar os limites do eixo X
        self.ax1.set_xlim([0, self.cam.image[0]])
        self.ax1.xaxis.tick_top()

        ##### Falta acertar os limites do eixo Y
        self.ax1.set_ylim([self.cam.image[1], 0])

        ##### Você deverá criar a função de projeção 
        object_2d = self.projection_2d()

        ##### Falta plotar o object_2d que retornou da projeção
        self.projection = self.ax1.plot(object_2d[0, :], object_2d[1, :], color = 'r')

        self.ax1.grid('True')
        self.ax1.set_aspect('equal')  
        canvas_layout.addWidget(self.canvas1)

        # Criar um objeto FigureCanvas para exibir o gráfico 3D
        self.fig2 = plt.figure()
        self.ax2 = self.fig2.add_subplot(111, projection='3d')
        
        ##### Falta plotar o seu objeto 3D e os referenciais da câmera e do mundo
        
        #self.ax2.add_collection3d(art3d.Poly3DCollection(self.model.vectors))
        self.ax2.add_collection3d(art3d.Line3DCollection(self.model.vectors, colors='k', linewidths=0.2, linestyles='-'))

        self.ax2.auto_scale_xyz(self.model.model[0, :], self.model.model[1, :], self.model.model[2, :])
        set_axes_equal(self.ax2)
        self.ax2.view_init(elev=45, azim=35)
        self.ax2.dist = 10

        aux = np.eye(4)
        draw_arrows(aux[3, :], aux[0:3, :], self.ax2, length=10)

        plt.ion()

        self.canvas2 = FigureCanvas(self.fig2)
        canvas_layout.addWidget(self.canvas2)

        self.cam_quivers = draw_arrows(self.cam.M[:, 3], self.cam.M[:, :3], self.ax2, length=8)

        # Retornar o widget de canvas
        return canvas_widget


    ##### Você deverá criar as suas funções aqui
    
    def update_params_intrinsc(self, line_edits):
        width = float(line_edits[0].text()) if line_edits[0].text() != '' else self.cam.image[0]
        height = float(line_edits[1].text()) if line_edits[1].text() != '' else self.cam.image[1]
        x = float(line_edits[2].text()) if line_edits[2].text() != '' else self.cam.ccd[0]
        y = float(line_edits[3].text()) if line_edits[3].text() != '' else self.cam.ccd[1]
        focal_dist = float(line_edits[4].text()) if line_edits[4].text() != '' else self.cam.focal_dist
        stheta = float(line_edits[5].text()) if line_edits[5].text() != '' else self.cam.stheta

        self.cam.update_intrinsic(image=(width, height), ccd=(x,y), fd=focal_dist, stheta=stheta)

        self.update_canvas()

    def update_world(self,line_edits):
        for i in line_edits:
            print(i.text())
            i.setText('0' if i.text() == '' else i.text())
            print(i.text())


        Rx = x_rotate(float(line_edits[1].text()))
        Ry = y_rotate(float(line_edits[3].text()))
        Rz = z_rotate(float(line_edits[5].text()))

        T = translate(float(line_edits[0].text()), float(line_edits[2].text()), float(line_edits[4].text()))
        
        # Primeiro realiza a rotação nos eixos do mundo e depois a translação
        self.cam.M = T @ Rz @ Ry @ Rx @ self.cam.M

        self.update_canvas()

    def update_cam(self,line_edits):
        for i in line_edits:
            i.setText('0' if i.text() == '' else i.text())

        Rx = x_rotate(float(line_edits[1].text()))
        Ry = y_rotate(float(line_edits[3].text()))
        Rz = z_rotate(float(line_edits[5].text()))

        T = translate(float(line_edits[0].text()), float(line_edits[2].text()), float(line_edits[4].text()))

        # Primeiro realiza a rotação nos eixos da câmera e depois a translação
        self.cam.M = self.cam.M @ Rx @ Ry @ Rz @ T @self.cam_original.M

        self.update_canvas()

    def projection_2d(self):
        projection_matrix = np.array([[1, 0, 0, 0],
                                     [0, 1, 0, 0],
                                     [0, 0, 1, 0]]) 

        projection = self.cam.get_intrinsic_matrix() @ projection_matrix @ np.linalg.inv(self.cam.M) @ self.model.model

        projection = projection/projection[2]

        return projection

    def update_canvas(self):
        # Removing all plots from the 2d projection

        for i in self.projection:
            i.remove()
        
        # re-ploting the 2d projection, with updated values
        ##### Você deverá criar a função de projeção 
        object_2d = self.projection_2d()

        ##### Falta plotar o object_2d que retornou da projeção
        self.projection = self.ax1.plot(object_2d[0, :], object_2d[1, :], color = 'r', linewidth=0.5)

        # Updating 3d plot with new cam values
        
        for i in self.cam_quivers:
            i.remove()

        self.cam_quivers = draw_arrows(self.cam.M[:, 3], self.cam.M[:, :3], self.ax2, length=8)

        ##### Falta acertar os limites do eixo X
        self.ax1.set_xlim([0, self.cam.image[0]])
        self.ax1.xaxis.tick_top()

        ##### Falta acertar os limites do eixo Y
        self.ax1.set_ylim([self.cam.image[1], 0])

        return 
    
    def reset_canvas(self):
        self.cam.reset()
        self.update_canvas()
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
