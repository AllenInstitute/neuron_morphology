import gmsh
import ufl
import numpy as np
import dolfinx.fem as fem
from dolfinx.io import gmshio
from typing import List, Tuple
from mpi4py import MPI
from petsc4py.PETSc import ScalarType
from shapely import geometry as geo
from neuron_morphology.transforms.geometry import (
    get_ccw_vertices, get_vertices_from_two_lines
)


def solve_laplace_2d(V: fem.FunctionSpace,
                     bcs: List[fem.bcs.DirichletBCMetaClass]):
    """
        Solves the laplace equation with boundary conditions bcs on V

        Parameters
        ----------
        V: Fenics FunctionSpace object created from a mesh
        bcs: List of Fenics DirichletBC Boundary Conditions
    """

    u = ufl.TrialFunction(V)
    v = ufl.TestFunction(V)
    f = fem.Constant(V, ScalarType(0)) # no source for the Laplace equation
    a = ufl.dot(ufl.grad(u), ufl.grad(v)) * ufl.dx
    L = f * v * ufl.dx

    problem = fem.petsc.LinearProblem(a, L, bcs=bcs, petsc_options={"ksp_type": "preonly", "pc_type": "lu"})
    uh = problem.solve()

    return uh


def compute_gradient(uh, W, bcs=[]):
    Wf = fem.Function(W)
    f = ufl.grad(uh)
    V = Wf.function_space
    dx = ufl.dx(V.mesh)

    u = ufl.TrialFunction(V)
    v = ufl.TestFunction(V)
    a = ufl.inner(u, v) * dx
    L = ufl.inner(f, v) * dx

    problem = fem.petsc.LinearProblem(a, L, bcs=bcs, petsc_options={"ksp_type": "preonly", "pc_type": "lu"})
    grad_uh = problem.solve()

    return grad_uh


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

    # Collect and sort vertices for mesh generation
    circular_vertices = get_vertices_from_two_lines(top_line, bottom_line)
    vertices = get_ccw_vertices(circular_vertices)

    # Create mesh with gmsh
    gmsh.initialize()

    # Set up the points
    point_tags = [gmsh.model.geo.addPoint(x, y, 0, meshSize=mesh_res)
        for (x, y) in vertices[:-1]]

    # connect the points into lines
    line_tags = [gmsh.model.geo.addLine(point_tags[i], point_tags[i + 1])
        for i in range(len(point_tags) - 1)]
    line_tags += [gmsh.model.geo.addLine(point_tags[-1], point_tags[0])]

    # add the curve loop
    curve_loop = gmsh.model.geo.addCurveLoop(line_tags)

    # add the surface
    surface = gmsh.model.geo.addPlaneSurface([curve_loop])

    # generate the mesh
    gmsh.model.geo.synchronize()
    gdim = 2 # value of 2 for 2D
    gmsh.model.addPhysicalGroup(gdim, [surface])
    gmsh.model.mesh.generate(gdim)

    # import mesh into dolfinx
    gmsh_model_rank = 0
    mesh_comm = MPI.COMM_WORLD
    domain, cell_markers, facet_markers = gmshio.model_to_mesh(gmsh.model, mesh_comm, gmsh_model_rank, gdim=gdim)

    # Create variational space
    V = fem.FunctionSpace(domain, ("CG", 1))
    W = fem.VectorFunctionSpace(domain, ("CG", 1))

    # Create boundary conditions
    top_ls = geo.LineString(top_line)
    def boundary_top(coords):
        points = [geo.Point((x, y)) for x, y in coords[:2, :].T]
        return np.array([top_ls.distance(point) < eps_bounds for point in points])

    bottom_ls = geo.LineString(bottom_line)
    def boundary_bottom(coords):
        points = [geo.Point((x, y)) for x, y in coords[:2, :].T]
        return np.array([bottom_ls.distance(point) < eps_bounds for point in points])

    boundary_dofs_top = fem.locate_dofs_geometrical(V, boundary_top)
    boundary_dofs_bottom = fem.locate_dofs_geometrical(V, boundary_bottom)

    bc_top = fem.dirichletbc(ScalarType(top_value), boundary_dofs_top, V)
    bc_bottom = fem.dirichletbc(ScalarType(bottom_value), boundary_dofs_bottom, V)
    bcs = [bc_top, bc_bottom]

    # Solve for value field
    u = solve_laplace_2d(V, bcs)

    # Get derivative
    grad_u = compute_gradient(u, W)  # grad_u = Grad

    # Get values at mesh points
    mesh_coords = domain.geometry.x[:, :2]
    mesh_values = u.x.array
    mesh_gradients = np.reshape(grad_u.x.array, (-1, 2))

    return u, grad_u, domain, mesh_coords, mesh_values, mesh_gradients
