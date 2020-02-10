from typing import List, Tuple

import fenics as fen
import mshr as msh
from shapely import geometry as geo


def get_ccw_vertices_from_two_lines(line1: List[Tuple], line2: List[Tuple]):
    """
        Convenience method two do both get_vertices_from_two_lines()
        and get_ccw_vertices()
    """
    return get_ccw_vertices(get_vertices_from_two_lines(line1, line2))


def get_vertices_from_two_lines(line1: List[Tuple], line2: List[Tuple]):
    """
        Generates circular vertices from two lines

        Parameters
        ----------
        line1, line2: List of coordinates describing two lines

        Returns
        -------
        vertices of the simple polygon created from line 1 and 2
        (first vertex = last vertex)

        1-2-3-4
        5-6-7-8 -> [1-2-3-4-8-7-6-5-1]

    """
    side1 = geo.LineString([line1[0], line2[-1]])
    side2 = geo.LineString([line1[-1], line2[0]])

    if side1.crosses(side2):
        line2.reverse()

    vertices = line1 + line2 + [line1[0]]
    return vertices


def get_ccw_vertices(vertices: List[Tuple]):
    """
        Generates counter clockwise vertices from vertices describing
        a simple polygon

        Method: Simplification of the shoelace formula, which calculates
        area of a simple polygon by integrating the area under each line
        segment of the polygon. If the total area is positive, the vertices
        were traversed in clockwise order, and if it is negative, they were
        traversed in counterclockwise order.

        Parameters
        ----------
        vertices: vertices describing a convex polygon
                  (vertices[0] = vertices[-1])

        Returns
        -------
        vertices in counter clockwise order

    """

    winding = 0
    for i in range(len(vertices)-1):
        (x0, y0) = vertices[i]
        (x1, y1) = vertices[i+1]
        winding += (x1 - x0) * (y1 + y0)

    if winding > 0:
        vertices.reverse()

    return vertices


def solve_laplace_2d(V, bcs):
    """Solves the laplace equation with boundary conditios bcs on V"""

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
        Generates the solution to the laplace equation

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
    mesh_values = [u(x) for x in mesh_coords]
    mesh_gradients = [grad_u(x) for x in mesh_coords]

    return u, grad_u, mesh_coords, mesh_values, mesh_gradients
