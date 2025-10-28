from OpenGL.GL import *
from shape import Shape
import numpy as np
import math

class Cylinder(Shape):
  def __init__(self, fatias=64):
    lista_vertices = []
    lista_normais = []
    lista_tangentes = []
    lista_texcoords = []
    lista_indices = []
    raio = 0.5
    altura = 1.0
    offset_vertice = 0 

    # Tampa de Baixo
    normal_tampa_baixo = [0.0, -1.0, 0.0]
    tangente_tampa = [1.0, 0.0, 0.0]
    lista_vertices.extend([0.0, 0.0, 0.0])
    lista_normais.extend(normal_tampa_baixo)
    lista_tangentes.extend(tangente_tampa)
    lista_texcoords.extend([0.5, 0.5]) 
    for i in range(fatias + 1): 
        angulo = (i / fatias) * 2.0 * math.pi
        x = raio * math.cos(angulo)
        z = raio * math.sin(angulo)
        lista_vertices.extend([x, 0.0, z])
        lista_normais.extend(normal_tampa_baixo)
        lista_tangentes.extend(tangente_tampa)
        lista_texcoords.extend([0.5 + 0.5 * math.cos(angulo), 0.5 + 0.5 * math.sin(angulo)])
    for i in range(fatias):
        lista_indices.extend([
            offset_vertice + 0,          
            offset_vertice + i + 1,      
            offset_vertice + i + 2      
        ])
    offset_vertice = len(lista_vertices) // 3

    # Tampa de Cima
    normal_tampa_cima = [0.0, 1.0, 0.0] 
    lista_vertices.extend([0.0, altura, 0.0])
    lista_normais.extend(normal_tampa_cima)
    lista_tangentes.extend(tangente_tampa) 
    lista_texcoords.extend([0.5, 0.5]) 
    for i in range(fatias + 1):
        angulo = (i / fatias) * 2.0 * math.pi
        x = raio * math.cos(angulo)
        z = raio * math.sin(angulo)
        lista_vertices.extend([x, altura, z])
        lista_normais.extend(normal_tampa_cima)
        lista_tangentes.extend(tangente_tampa)
        lista_texcoords.extend([0.5 + 0.5 * math.cos(angulo), 0.5 + 0.5 * math.sin(angulo)])
    for i in range(fatias):
        lista_indices.extend([
            offset_vertice + 0,          
            offset_vertice + i + 2,      
            offset_vertice + i + 1      
        ])
    
    offset_vertice = len(lista_vertices) // 3

    # Lateral 
    for i in range(fatias):
        angulo1 = (i / fatias) * 2.0 * math.pi
        angulo2 = ((i + 1) / fatias) * 2.0 * math.pi
        x1 = raio * math.cos(angulo1)
        z1 = raio * math.sin(angulo1)
        x2 = raio * math.cos(angulo2)
        z2 = raio * math.sin(angulo2)
        normal1 = [math.cos(angulo1), 0.0, math.sin(angulo1)]
        normal2 = [math.cos(angulo2), 0.0, math.sin(angulo2)]
        tangente1 = [-math.sin(angulo1), 0.0, math.cos(angulo1)]
        tangente2 = [-math.sin(angulo2), 0.0, math.cos(angulo2)]
        u1 = i / fatias
        u2 = (i + 1) / fatias
        lista_vertices.extend([x1, 0.0, z1])
        lista_normais.extend(normal1)
        lista_tangentes.extend(tangente1)
        lista_texcoords.extend([u1, 0.0]) 
        lista_vertices.extend([x1, altura, z1])
        lista_normais.extend(normal1)
        lista_tangentes.extend(tangente1)
        lista_texcoords.extend([u1, 1.0])
        lista_vertices.extend([x2, altura, z2])
        lista_normais.extend(normal2)
        lista_tangentes.extend(tangente2)
        lista_texcoords.extend([u2, 1.0])
        lista_vertices.extend([x2, 0.0, z2])
        lista_normais.extend(normal2)
        lista_tangentes.extend(tangente2)
        lista_texcoords.extend([u2, 0.0])
        idx = offset_vertice + (i * 4) 
        lista_indices.extend([idx + 0, idx + 1, idx + 2])
        lista_indices.extend([idx + 0, idx + 2, idx + 3])
            
    array_vertices = np.array(lista_vertices, dtype='float32')
    array_normais = np.array(lista_normais, dtype='float32')
    array_tangentes = np.array(lista_tangentes, dtype='float32')
    array_texcoords = np.array(lista_texcoords, dtype='float32')
    array_indices = np.array(lista_indices, dtype='uint32')

    self.total_indices = len(array_indices)
    
    self.vao = glGenVertexArrays(1)
    glBindVertexArray(self.vao)
    buffers = glGenBuffers(5)
    glBindBuffer(GL_ARRAY_BUFFER, buffers[0])
    glBufferData(GL_ARRAY_BUFFER, array_vertices.nbytes, array_vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)
    
    glBindBuffer(GL_ARRAY_BUFFER, buffers[1])
    glBufferData(GL_ARRAY_BUFFER, array_normais.nbytes, array_normais, GL_STATIC_DRAW)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(1)
    
    glBindBuffer(GL_ARRAY_BUFFER, buffers[2])
    glBufferData(GL_ARRAY_BUFFER, array_tangentes.nbytes, array_tangentes, GL_STATIC_DRAW)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(2)
    
    glBindBuffer(GL_ARRAY_BUFFER, buffers[3])
    glBufferData(GL_ARRAY_BUFFER, array_texcoords.nbytes, array_texcoords, GL_STATIC_DRAW)
    glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(3)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffers[4])
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, array_indices.nbytes, array_indices, GL_STATIC_DRAW)


  def Draw (self, st):
    glBindVertexArray(self.vao)
    glDrawElements(GL_TRIANGLES, self.total_indices, GL_UNSIGNED_INT, None)
