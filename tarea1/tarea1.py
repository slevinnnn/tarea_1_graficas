import os
import sys

import numpy as np
from pyglet import clock
from pyglet.app import run
from pyglet.gl import *
from pyglet.window import Window, key

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from terrain import *

import grafica.transformations as tr
from utils.helpers import init_axis, init_pipeline

# Clase Controller: gestiona la ventana y almacena las variables globales del programa
class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Variables para los shaders
        self.sky_color = np.array([96/255, 194/255, 224/255])
        self.intensity = 0.9
        self.wireframe = False


        #======== Variables para la generación de terreno =======
        # Variable que almacena los índices de los chunks
        self.currentChunks = []
        # Variable que almacena los indices del chunk central actual
        self.centerChunk = (None, None)
        # Variable que almacena una lista con los objetos de gpu
        # de cada chunk
        self.gpu_chunks = []


# ===== Programa Principal =====
if __name__ == "__main__":

    # Se declara el Controller
    controller = Controller(1000,1000,"Tarea 1")
    controller.set_exclusive_mouse(True)

    # Se crea un pipeline, aquí root es la dirección a la carpeta actual
    root = os.path.dirname(__file__)
    # Se utilizarán los shaders tarea1.vert y tarea1.frag
    pipeline = init_pipeline(root + "/tarea1.vert", root + "/tarea1.frag")
    # pipeline para el sol
    pipeline_sol = init_pipeline(root + "/tarea1_sol.vert", root + "/tarea1_sol.frag")
    # Se determina n la resolución de los chunks
    # Cada chunk se compondrá de n x n cuadrados
    n = 25

    # Se declara un objeto cámara, este objeto contiene la lógica que simula una cámara
    cam = MyCam([n/2, n/2, n/2])

    # Se declara un axis, este objeto permite mostrar en pantalla un objeto que simula 3 ejes
    # Mostrando con claridad cual es el eje X, Y, Z
    # Se puede remover o dejar.
    #axis = init_axis(cam)

    # ====== COMPLETAR: Aqui hacer la geometría y el vertex_list del sol ========
    DEFINITION = 100
    sun_vertices = createSunVertices(0.0, 0.0, 1.5, DEFINITION)
    sun_indices = createSunIndices(DEFINITION)
    sun_gpu = pipeline_sol.vertex_list_indexed(DEFINITION + 1, GL_TRIANGLES, sun_indices)
    sun_gpu.position[:] = sun_vertices
    elapsed_time = [0.0]

    # ===== Función draw =====
    # Esta función contiene la lógica que se realiza cada vez que se dibuja un nuevo frame
    # Aquí tendrán que declarar qué objetos dibujar en pantalla
    # Además tendrán que declarar la configuración de OpenGL usarán
    @controller.event
    def on_draw():

        # Esta instrucción limpia lo que había antes en pantalla
        controller.clear()

        # ===== Las siguientes son configuraciones de OpenGL =====
        # Color de fondo, se rescata de las variables globales
        glClearColor(*(controller.sky_color * controller.intensity),1)
        # Activa la profundidad
        glEnable(GL_DEPTH_TEST)
        # Esta configuración determina si se rellenan o no las caras
        if controller.wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


        # ==== Objetos dibujables =====
        # Esta instrucción activa el pipeline del sol
        pipeline_sol.use()
        # ===== COMPLETAR CON LOS UNIFORMS DEL SOL y EL OBJETO EN SI======
        pipeline_sol["u_view"] = cam.get_view()
        pipeline_sol["u_projection"] = cam.get_projection()
        sun_transform = tr.translate(0.0, 5.0 + np.sin(elapsed_time[0]), 0.0)
        pipeline_sol["u_transform"] = np.reshape(sun_transform, (16, 1), order="F")
        sun_gpu.draw(GL_TRIANGLES)


        # Esta instrucción activa el pipeline de los chunks
        pipeline.use()

        # ===== COMPLETAR CON LOS OBJETOS A DIBUJAR Y UNIFORMS ======
        pipeline["u_view"] = cam.get_view()
        pipeline["u_projection"] = cam.get_projection()
        for gpu_chunk in controller.gpu_chunks:
            gpu_chunk.draw(GL_TRIANGLES)

        # Opcionalmente se dibujan los ejes
        #axis.draw()

    # ====== Función Update =======
    # Esta función es similar a draw(), pero se encarga de actualizar los estados de los objetos
    # Objetos como la cámara u objetos en movimiento se actualizarán aquí
    def update(dt):

        elapsed_time[0] += dt

        # Esta función actualiza la lista de chunks que es visible actualmente
        # En caso de que sea necesario crear nuevos chunks
        # ===== COMPLETAR: Esta función deben implementarla en el modulo terrain.py ======
        updateChunks(n, cam, controller, pipeline)

        # Esta función actualiza los ejes, de no existir ejes, no es necesario llamarla
        #axis.update()

        # Esta función actualiza la cámara en función del input del teclado
        cam.time_update(dt)

    # ===== Lógica que controla la cámara ======
    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == key.W:
            cam.direction[0] = 1
        if symbol == key.S:
            cam.direction[0] = -1
        if symbol == key.A:
            cam.direction[1] = 1
        if symbol == key.D:
            cam.direction[1] = -1
        if symbol == key._1:  # tecla 1
            controller.wireframe = not controller.wireframe

    @controller.event
    def on_key_release(symbol, modifiers):
        if symbol == key.W or symbol == key.S:
            cam.direction[0] = 0

        if symbol == key.A or symbol == key.D:
            cam.direction[1] = 0

    @controller.event
    def on_mouse_motion(x, y, dx, dy):
        cam.yaw += dx * .001
        cam.pitch += dy * .001
        cam.pitch = max(-(np.pi/2 - 0.01), min(cam.pitch, np.pi/2 - 0.01))

    # ====== Fin del control de la cámara ======


    # ==== Llamado a ejecutar todo el programa =====
    # Aquí clock gestiona el llamado periodico a draw() y update()
    clock.schedule_interval(update,1/60)
    # run() llama a ejecutar todo lo configurado
    run()
