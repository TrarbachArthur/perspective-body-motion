import numpy as np

class Camera:
    def __init__(self):
        # initialize camera at origin
        self.M = np.eye(4)
        
        self.image = (1280,720)
        self.ccd = (36,24)
        self.focal_dist = 50
        self.stheta = 0

    def get_intrinsic_matrix(self):
        # calculate the intrinsic matrix
        f = self.focal_dist
        stheta = self.stheta
        sx = self.image[0]/self.ccd[0]
        sy = self.image[1]/self.ccd[1]
        cx = self.image[0]/2
        cy = self.image[1]/2

        return np.array([[f*sx, f*stheta, f*cx],
                         [0, f*sy, f*cy],
                         [0, 0, 1]])
    
    def update_intrinsic(self, image=None, ccd=None, fd=None, stheta=None):
        self.image = image if image != None else self.image
        self.ccd = ccd if ccd != None else self.ccd 
        self.focal_dist = fd if fd != None else self.focal_dist
        self.stheta = stheta if stheta != None else self.stheta

        print(self.image, self.ccd, self.focal_dist, self.stheta)

    def reset(self):
        self.M = np.eye(4)
        self.update_intrinsic(image=(1280,720), ccd=(36,24), fd=50, stheta=0)