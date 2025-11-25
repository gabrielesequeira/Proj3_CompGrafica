from OpenGL.GL import *
from shape import Shape
import numpy as np

class Cube(Shape):
    def __init__(self):
        # 8 vértices do cubo
        vertices = np.array([
            -1, -1, -1,
             1, -1, -1,
             1,  1, -1,
            -1,  1, -1,
            -1, -1,  1,
             1, -1,  1,
             1,  1,  1,
            -1,  1,  1
        ], dtype=np.float32)

        normals = np.array([
            0, 0, -1,
            0, 0, -1,
            0, 0, -1,
            0, 0, -1,
            0, 0,  1,
            0, 0,  1,
            0, 0,  1,
            0, 0,  1
        ], dtype=np.float32)

        indices = np.array([
            0, 1, 2, 2, 3, 0,  
            4, 5, 6, 6, 7, 4,   
            0, 4, 7, 7, 3, 0,   
            1, 5, 6, 6, 2, 1,   
            3, 2, 6, 6, 7, 3,   
            0, 1, 5, 5, 4, 0    
        ], dtype=np.uint32)

        self.nind = len(indices)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        nbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, nbo)
        glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)

        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    def Draw(self, st):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.nind, GL_UNSIGNED_INT, None)
