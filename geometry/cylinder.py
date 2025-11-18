from OpenGL.GL import *
from shape import Shape
import numpy as np
import math

class Cylinder(Shape):
    def __init__(self, radius=0.5, height=1.0, sectors=64):
        self.sectors = sectors
        self.nind = 6 * sectors + 6 * sectors  # 2 triângulos por lateral + tampas
        self.radius = radius
        self.height = height

        coords = []
        normals = []
        texcoords = []
        tangents = []
        indices = []

        half_height = height / 2

        sector_step = 2 * math.pi / sectors
        for i in range(sectors):
            theta = i * sector_step
            x = radius * math.cos(theta)
            z = radius * math.sin(theta)

            coords.extend([x, half_height, z])
            coords.extend([x, -half_height, z])

            normals.extend([x, 0.0, z])
            normals.extend([x, 0.0, z])

            tangents.extend([-math.sin(theta), 0.0, math.cos(theta)])  # Topo
            tangents.extend([-math.sin(theta), 0.0, math.cos(theta)])  # Base

            texcoords.extend([i / sectors, 1.0])  # Topo
            texcoords.extend([i / sectors, 0.0])  # Base

            next_i = (i + 1) % sectors
            indices.extend([2 * i, 2 * next_i, 2 * i + 1])
            indices.extend([2 * next_i, 2 * next_i + 1, 2 * i + 1])

        center_top = len(coords) // 3
        coords.extend([0.0, half_height, 0.0])
        normals.extend([0.0, 1.0, 0.0])
        texcoords.extend([0.5, 0.5])

        for i in range(sectors):
            theta = i * sector_step
            x = radius * math.cos(theta)
            z = radius * math.sin(theta)

            next_i = (i + 1) % sectors
            indices.extend([center_top, 2 * next_i, 2 * i])

        center_bottom = len(coords) // 3
        coords.extend([0.0, -half_height, 0.0])
        normals.extend([0.0, -1.0, 0.0])
        texcoords.extend([0.5, 0.5])

        for i in range(sectors):
            theta = i * sector_step
            x = radius * math.cos(theta)
            z = radius * math.sin(theta)

            next_i = (i + 1) % sectors
            indices.extend([center_bottom, 2 * i + 1, 2 * next_i + 1])

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        ids = glGenBuffers(4)
        coords = np.array(coords, dtype='float32')
        normals = np.array(normals, dtype='float32')
        texcoords = np.array(texcoords, dtype='float32')
        tangents = np.array(tangents, dtype='float32')
        indices = np.array(indices, dtype='uint32')

        glBindBuffer(GL_ARRAY_BUFFER, ids[0])
        glBufferData(GL_ARRAY_BUFFER, coords.nbytes, coords, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, ids[1])
        glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, ids[2])
        glBufferData(GL_ARRAY_BUFFER, tangents.nbytes, tangents, GL_STATIC_DRAW)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(2)

        glBindBuffer(GL_ARRAY_BUFFER, ids[3])
        glBufferData(GL_ARRAY_BUFFER, texcoords.nbytes, texcoords, GL_STATIC_DRAW)
        glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(3)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, glGenBuffers(1))
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    def Draw(self, st):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.nind, GL_UNSIGNED_INT, None)
