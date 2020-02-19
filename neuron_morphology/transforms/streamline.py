from typing import List, Tuple

import fenics as fen
import mshr as msh
from shapely import geometry as geo
import numpy as np

from neuron_morphology.transforms.geometry import (
    get_ccw_vertices, get_vertices_from_two_lines
)


def solve_laplace_2d(V: fen.FunctionSpace,
                     bcs: List[fen.DirichletBC]):
    """
        Solves the laplace equation with boundary conditions bcs on V

        Parameters
        ----------
        V: Fenics FunctionSpace object created from a mesh
        bcs: List of Fenics DirichletBC Boundary Conditions
    """

    # Define variational problem
    u = fen.TrialFunction(V)
    v = fen.TestFunction(V)
    f = fen.Constant(0)  # no source for the Laplace equation
    a = fen.dot(fen.grad(u), fen.grad(v)) * fen.dx
    L = f * v * fen.dx

    # Compute solution
    u = fen.Function(V)
    fen.solve(a == L, u, bcs)

    return u


def compute_gradient(u, mesh):
    """Computes the gradient of the value field at the mesh points"""

    W = fen.VectorFunctionSpace(mesh, 'P', 1)
    gradient = fen.project(fen.grad(u), W)

    return gradient


def generate_laplace_field(top_line: List[Tuple],
                           bottom_line: List[Tuple],
                           mesh_res: float = 20,
                           top_value: float = 1.0,
                           bottom_value: float = 0.0,
                           eps_bounds: float = 1e-8):
    """
        Solve Laplace equation inside a polygon bounded
        by two lines (top_line and bottom_line) and the artificial
        straight side lines connecting the ends of the two lines.
        Apply Dirichlet BC on top_line and bottom_line and
        zero Neuman BC on the side lines.


        Demo of fenics: https://github.com/hplgit/fenics-tutorial/
                        blob/master/pub/python/vol1/ft01_poisson.py

        If top_value and bottom_value defaults are used, value_field
        will be the normalized distance to the top_line

        Parameters
        ----------
        top_line: line that will have top_value boundary condition
        bottom_line: line that will have bottom_value boundary condition
        mesh_res: resolution of the mesh
        top_value: value for top Dirichlet Boundary
        bottom_value: value for bottom Dirichlet Boundary

        Returns
        -------
        u: returns value at input point e.g. 0.5 = u((0.5, 0.5))
        grad_u: returns gradient at input point e.g. [0, 1] = u((0.5, 0.5))

        mesh_coords: coordinates of each vertex in the mesh
        mesh_values: values at each vertex in the mesh
        gradient_mesh: gradient at each vertex in the mesh

    """

    # Make sure vertices are in counter clockwise order for generate_mesh
    circular_vertices = get_vertices_from_two_lines(top_line, bottom_line)
    vertices = get_ccw_vertices(circular_vertices)

    # Create Mesh and Variational space
    polygon = msh.cpp.Polygon([fen.Point((x, y)) for (x, y) in vertices])
    mesh = msh.generate_mesh(polygon, mesh_res)
    V = fen.FunctionSpace(mesh, 'P', 1)
    W = fen.VectorFunctionSpace(mesh, 'P', 1)

    # Create boundary conditions
    top_ls = geo.LineString(top_line)

    def boundary_top(point, on_boundary):
        if not on_boundary:
            return False

        point = geo.Point(point)
        if top_ls.distance(point) < eps_bounds:
            return True

    bottom_ls = geo.LineString(bottom_line)

    def boundary_bottom(point, on_boundary):
        if not on_boundary:
            return False

        point = geo.Point(point)
        if bottom_ls.distance(point) < eps_bounds:
            return True

    bc_top = fen.DirichletBC(V, fen.Constant(top_value), boundary_top)
    bc_bottom = fen.DirichletBC(V, fen.Constant(bottom_value), boundary_bottom)
    bcs = [bc_top, bc_bottom]

    # Solve for value field
    u = solve_laplace_2d(V, bcs)  # u = TrialFunction on V
    u = fen.project(u, V)

    # Get derivative
    grad_u = fen.project(fen.grad(u), W)  # grad_u = Grad

    # Get values at mesh points
    mesh_coords = mesh.coordinates()
    mesh_values = u.compute_vertex_values(mesh)
    mesh_gradients = np.reshape(grad_u.compute_vertex_values(mesh),
                                [2, len(mesh_coords)]).T

    return u, grad_u, mesh, mesh_coords, mesh_values, mesh_gradients
