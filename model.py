from stl import mesh as me
import numpy as np

class Model():
    def __init__(self, filename):
        mesh = me.Mesh.from_file(filename)
        
        self.vectors = mesh.vectors
        self.normals = mesh.normals

        self.model = np.array([mesh.x.flatten().T,
                               mesh.y.flatten().T,
                               mesh.z.flatten().T,
                               np.ones(mesh.x.flatten().size)])