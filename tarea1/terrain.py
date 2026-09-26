import numpy as np
import trimesh as tm
from pyglet.gl import GL_TRIANGLES

from perlin_noise import PerlinNoise
from utils.camera import FreeCamera

# calculateNormals: genera las normales para la geometria indicada usando Trimesh
# vertices: lista de vertices [x, y, z, x, y, z, ...]
# indices: lista de indices para los vertices dados
def calculateNormals(vertices, indices):
    # Creamos un trimesh object con la geometria
    tri = tm.Trimesh(vertices=np.array(vertices).reshape(len(vertices)//3, 3), faces=np.array(indices).reshape(len(indices)//3, 3), process=False)
    # Devolvemos solo las normales
    return np.array(tri.vertex_normals, dtype=np.float32).flatten()


# ====== COMPLETAR A CONTINUACIÓN funciones createSunVertices, createSunIndices, generateChunkVertices, makeChunks y updateChunks ========

# createSunVertices: Genera las posiciones de un circulo en el plano XY dado su centro y su radio
# x: valor en el eje X del centro del circulo
# y: valor en el eje Y del centro del circulo
# radius: radio del circulo
def createSunVertices(x, y, radius, DEFINITION):
    positions = np.zeros((DEFINITION + 1)*3, dtype=np.float32) 
    colors = np.zeros((DEFINITION + 1) * 3, dtype=np.float32)
    dtheta = 2*np.pi / DEFINITION

    for i in range(DEFINITION):
        theta = i*dtheta
        positions[i*3:(i+1)*3] = [x + np.cos(theta)*radius, y + np.sin(theta)*radius, 0.0]

    # Finalmente agregamos el centro
    positions[3*DEFINITION:] = [x, y, 0.0]

    return positions

# createSunIndices: genera los indices para un circulo, dada la definición de este
def createSunIndices(DEFINITION):
    indices = np.zeros(3*( DEFINITION + 1 ), dtype=np.int32)
    for i in range(DEFINITION):
        # Cada triangulo se forma por el centro, el punto actual y el siguiente
        indices[3*i: 3*(i+1)] = [DEFINITION, i, i+1]
   
    # Completamos el circulo (pueden borrar esta linea y ver que pasa)
    indices[3*DEFINITION:] = [DEFINITION, DEFINITION - 1, 0]
    return indices

# generateChunkVertices: genera la lista de vertices y la de indices para el chunk
# de tamaño <n> e indices <chunk_x> y <chunk_y>
# n: resolución de la grilla
# chunk_x: indice del chunk en el eje x
# chunk_z: indice del chunk en el eje z
def generateChunkVertices(n, chunk_x, chunk_z):
    noise = PerlinNoise(octaves=4, seed=12)

    vertices = []
    indices = []
    posiciones = []


    chunk_origin_x = chunk_x * n
    chunk_origin_z = chunk_z * n

    for z in range(n + 1):
        for x in range(n + 1):
            world_x = chunk_origin_x + x
            world_z = chunk_origin_z + z
            height = noise([world_x / 10.0, world_z / 10.0]) * 2.0
            posiciones.extend([world_x, height, world_z])

    row_size = n + 1
    for z in range(n):
        for x in range(n):
            current = z * row_size + x
            next_row = current + row_size
            indices.extend([
                current, current + 1, next_row + 1,
                next_row + 1, next_row, current,
            ])

    normals = calculateNormals(posiciones, indices)
    for vertex_index in range((n + 1) * (n + 1)):
        position_start = vertex_index * 3
        normal_start = vertex_index * 3
        vertices.extend(posiciones[position_start:position_start + 3])
        vertices.extend(normals[normal_start:normal_start + 3])

    return (vertices, indices)

# makeChunks: Construye los vertex_list para cada chunk en la lista de chunks y los guarda en la variable controller.gpu_chunks
# resolución: resolución de los chunks, es decir cuadrados por lado del chunk
# controller: objeto controller de la aplicación principal que almacena las variables globales
# pipeline: pipeline donde declarar los vertex_list u objetos de gpu
def makeChunks(resolucion, controller, pipeline):
    controller.gpu_chunks.clear()

    for chunk_x, chunk_z in controller.currentChunks:
        vertices, indices = generateChunkVertices(resolucion, chunk_x, chunk_z)
        posiciones = []
        normales = []

        for vertex_start in range(0, len(vertices), 6):
            posiciones.extend(vertices[vertex_start:vertex_start + 3])
            normales.extend(vertices[vertex_start + 3:vertex_start + 6])

        gpu_chunk = pipeline.vertex_list_indexed(
            len(posiciones) // 3,
            GL_TRIANGLES,
            indices,
        )
        gpu_chunk.position[:] = posiciones
        gpu_chunk.normal[:] = normales
        controller.gpu_chunks.append(gpu_chunk)



# updateChunks: Actualiza la lista de indices de chunks en controller.currentChunks
# resolución: resolución de los chunks, es decir cuadrados por lado del chunk
# camara: objeto camara para obtener la posicion actual
# controller: objeto controller de la aplicación principal que almacena las variables globales
# pipeline: pipeline donde declarar los vertex_list u objetos de gpu
def updateChunks(resolucion, camara, controller, pipeline):

    # completar...

    # a continuación se muestra cómo obtener la posicion de la camara en x y z
    x_pos = camara.position[0]
    z_pos = camara.position[2]

    current_center = (
        int(np.floor(x_pos / resolucion)),
        int(np.floor(z_pos / resolucion)),
    )

    if current_center != controller.centerChunk:
        center_x, center_z = current_center
        controller.currentChunks = [
            (center_x + offset_x, center_z + offset_z)
            for offset_z in (-1, 0, 1)
            for offset_x in (-1, 0, 1)
        ]
        controller.centerChunk = current_center

        # tendrán que utilizar la función anterior para
        # generar los vertex_list de los chunks cuando corresponda:
        # makeChunks(resolucion, controller, pipeline)
        makeChunks(resolucion, controller, pipeline)




# La siguiente clase gestiona la cámara y no deben modificarla :)
class MyCam(FreeCamera):
    def __init__(self, position=np.array([0, 0, 0]), camera_type="perspective"):
        super().__init__(position, camera_type)
        self.direction = np.array([0,0,0])
        self.speed = 10

    def time_update(self, dt):
        self.update()
        old_forward = np.array([self.forward[0], 0, self.forward[2]])
        dir = self.direction[0]*old_forward + self.direction[1]*self.right
        dir_norm = np.linalg.norm(dir)
        if dir_norm:
            dir /= dir_norm

        self.position += dir*self.speed*dt
        self.focus = self.position + self.forward
