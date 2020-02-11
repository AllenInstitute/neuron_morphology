from typing import Dict, Optional, List, Any

import numpy as np
import math
from sklearn.neighbors import NearestNeighbors
from scipy import interpolate
import xarray as xr

from neuron_morphology.morphology import Morphology
from neuron_morphology.transforms.transform_base import TransformBase
from neuron_morphology.transforms.affine_transform import AffineTransform

class ComputeAngle():
    
    def __init__(self, angle: Optional[Any] = None):
        """
            Represent the rotation transform as a (4,4) np.ndarray affine matrix

            Parameters
            ----------
            affine: (4,4) array-like affine transformation

        """
        if angle is None:
            self.angle = 0.0
        else:
            self.angle = angle

    def unit_vector(self,vector):
        """ 
            Returns the unit vector of the vector.  

        """
        return vector / np.linalg.norm(vector)

    def angle_between(self,v1, v2):
        """ 
            Returns the angle in radians between vectors 'v1' and 'v2' 
            
        """
        v1_u = self.unit_vector(v1)
        v2_u = self.unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

    def _get_val(self,xcoord, ycoord, idx, v, soma_x=0, soma_y=0, neighbors=16):
        """ 
            Returns a value calculated from soma's neighbors by interpolation

        """
        n = len(xcoord)
        coordinates = list(zip(xcoord, ycoord))
        
        if n>neighbors:
            knn = NearestNeighbors(n_neighbors=neighbors)
            coordinates = np.insert(coordinates, 0, [soma_x, soma_y], axis = 0)
            knn.fit(coordinates)
            distances, indices = knn.kneighbors([coordinates[0]])

            x = coordinates[indices][0][1:,0]
            y = coordinates[indices][0][1:,1]
            z = v[indices[0][1:]]

            try:
                f = interpolate.interp2d(x, y, z)
            except (RuntimeError, TypeError, NameError):
                print('interpolation error')
                
            return f(soma_x,soma_y)
        else:
            nn = idx
            x = xcoord
            y = ycoord
            z = v[nn[:,0],nn[:,1]]
            
            try:
                f = interpolate.interp2d(x, y, z)
            except (RuntimeError, TypeError, NameError):
                print('interpolation error')
                
            return f(soma_x,soma_y)

    def compute(self, gradient_path,soma:Optional[List[float]]):
        """
            Calculate the angle at soma given a gradient field

            Parameters
            ----------
            gradient_path: a file path to the gradient field
            soma: a list [x,y,z] to present the soma location 

            Returns
            -------
            angle

        """
        theta = 0.0
        
        vert_vec = np.zeros(3)
        vert_vec[1] = 1.0

        soma_vec = np.zeros(3)

        with xr.open_dataarray(gradient_path) as grad:
            dx_obj = grad.sel(dim ='dx')
            dy_obj = grad.sel(dim ='dy')

            dx = dx_obj.values
            dy = dy_obj.values

            xidx = np.argwhere(~np.isnan(dx))
            yidx = np.argwhere(~np.isnan(dy))

            idx = np.array([i for i in xidx & yidx])

            dx_xcoord = dx_obj.coords['x'].values
            dx_ycoord = dx_obj.coords['y'].values

            vx = dx[idx[:,0],idx[:,1]]
            vy = dy[idx[:,0],idx[:,1]]

            soma_grad_x = self._get_val(dx_xcoord[idx[:,0]],dx_ycoord[idx[:,1]],idx,vx,soma[0],soma[1])
            soma_grad_y = self._get_val(dy_xcoord[idx[:,0]],dy_ycoord[idx[:,1]],idx,vy,soma[0],soma[1])

            soma_vec[0] = soma_grad_x[0]
            soma_vec[1] = soma_grad_y[0]

            theta = self.angle_between(vert_vec, soma_vec) / math.pi

        return theta
