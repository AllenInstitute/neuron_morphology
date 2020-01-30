from Typing import List, Tuple

import fenics as fen
import mshr as msh
from shapely import geometry as geo


def get_ccw_vertices(line1: List[Tuple], line2: List[Tuple]):
    """
        Generates clockwise vertices from two Line Strings

        Uses method described in: https://www.element84.com/blog/
        determining-the-winding-of-a-polygon-given-as-a-set-of-ordered-points

        Returns
        -------
        vertices in counter clockwise order
    """

    # First, make sure that lines are in circular order
    line1 = geo.LineString([line1[0], line2[-1]])
    line2 = geo.LineString([line1[-1], line2[0]])

    if line1.crosses(line2):
        line2.reverse()

    vertices = line1 + line2 + [line1[0]]

    # Second, make sure that they are in ccw order
    winding = 0
    for i in range(len(vertices)-1):
        (x0, y0) = vertices[i]
        (x1, y1) = vertices[i+1]
        winding += (x1 + x0) * (y1 + y0)

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
        value_field: solution to the laplace equation at each cell
        gradient_field: gradient of that solution
        gradient_mesh: gradient at each vertex in the mesh

    """

    # Make sure vertices are in counter clockwise order for generate_mesh
    vertices = get_ccw_vertices(top_line, bottom_line)

    # Create Mesh and Variational space
    polygon = msh.cpp.Polygon([fen.Point((x, y)) for (x, y) in vertices])
    mesh = msh.generate_mesh(polygon, mesh_res)
    V = fen.FunctionSpace(mesh, 'P', 1)

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

    # Solve
    value_field = solve_laplace_2d(V, bcs)
    gradient_field = fen.project(fen.grad(value_field))
    mesh_gradients = compute_gradient(value_field, mesh)

    return value_field, gradient_field, mesh_gradients
