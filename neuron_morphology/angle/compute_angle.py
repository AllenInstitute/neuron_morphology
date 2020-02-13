from typing import Dict, Optional, List, Any

import numpy as np
import math
from sklearn.neighbors import NearestNeighbors
from scipy import interpolate
import xarray as xr

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

    def angle_between(self, v1, v2):
        """ 
            Returns the angle in radians between vectors 'v1' and 'v2' 
            
        """
        v1_u = self.unit_vector(v1)
        v2_u = self.unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

    def unique_rows(self,a):
        """ 
            Remove duplicated element in a numpy array

            Parameters
            ----------
            a: a numpy array

            Returns
            ----------
            a numpy array with unique rows 
            
        """
        a = np.ascontiguousarray(a)
        unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))
        return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))

    def _get_val(self, xcoord, ycoord, idx, v, node_x=0, node_y=0, neighbors=16):
        """ 
            Calculate the scalar value given an array and a location by interpolation

            Parameters
            ----------
            xcoord: the x coordinates
            ycoord: the y coordinates
            idx: the coordinates of non-NaN values of the array (dx/dy of the vector field)
            node_x: x-coordinate of the node
            node_y: y-coordinate of the node
            neighbors: the number of nearest neighbors used for interpolation

            Returns
            ----------
            scalar value

        """
        n = len(xcoord)
        coordinates = list(zip(xcoord, ycoord))
        
        if n>neighbors:
            knn = NearestNeighbors(n_neighbors=neighbors)
            coordinates = np.insert(coordinates, 0, [node_x, node_y], axis = 0)
            knn.fit(coordinates)
            distances, indices = knn.kneighbors([coordinates[0]])

            x = coordinates[indices][0][1:,0]
            y = coordinates[indices][0][1:,1]
            z = v[indices[0][1:]]

            try:
                f = interpolate.interp2d(x, y, z)
            except (RuntimeError, TypeError, NameError):
                print('interpolation error')
                
            return f(node_x,node_y)
        else:
            nn = idx
            x = xcoord
            y = ycoord
            z = v[nn[:,0],nn[:,1]]
            
            try:
                f = interpolate.interp2d(x, y, z)
            except (RuntimeError, TypeError, NameError):
                print('interpolation error')
                
            return f(node_x,node_y)

    def calculate_upright_angle(self,gradient,node:Optional[List[float]],neighbors=16):
        """
            Calculate the upright angle at node, e.g. a soma, given a gradient field

            Parameters
            ----------
            gradient: the gradient field stored in xarray
            node: a list [x,y,z] to present the node location 

            Returns
            -------
            upright angle

        """
        theta = 0.0
        
        vert_vec = np.zeros(3)
        vert_vec[1] = 1.0

        node_vec = np.zeros(3)

        vals = gradient.values

        dx = vals[:,:,0]
        dy = vals[:,:,1]

        xidx = np.argwhere(~np.isnan(dx))
        yidx = np.argwhere(~np.isnan(dy))

        xidxset = set([tuple(e) for e in xidx])
        yidxset = set([tuple(e) for e in yidx])

        idx = np.array([x for x in xidxset & yidxset])

        xcoord = gradient.coords['x'].values
        ycoord = gradient.coords['y'].values

        vx = dx[idx[:,0],idx[:,1]]
        vy = dy[idx[:,0],idx[:,1]]

        node_grad_x = self._get_val(xcoord[idx[:,0]],ycoord[idx[:,1]],idx,vx,node[0],node[1],neighbors)
        node_grad_y = self._get_val(xcoord[idx[:,0]],ycoord[idx[:,1]],idx,vy,node[0],node[1],neighbors)

        node_vec[0] = node_grad_x[0]
        node_vec[1] = node_grad_y[0]

        theta = self.angle_between(vert_vec, node_vec)

        return theta
    
    def compute(self, gradient_path, node:Optional[List[float]], step = 10):
        """
            Calculate the angle at node, e.g. soma, given a gradient field

            Parameters
            ----------
            gradient_path: a file path to the gradient field
            step: ratio to downsample the grid of gradient
            node: a list [x,y,z] to present the node location 

            Returns
            -------
            angle

        """
        with xr.open_dataarray(gradient_path) as gradient:
            gradient_ds = gradient[::step,::step,:]
            return self.calculate_upright_angle(gradient_ds, node)

        
