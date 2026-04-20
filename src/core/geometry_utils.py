from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_VERTEX
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.GEOMImpl import GEOMImpl_Builder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Face, TopoDS_Edge, TopoDS_Vertex
import numpy as np


def get_faces(shape: TopoDS_Shape) -> list:
    """Zwraca listę wszystkich ścian w kształcie."""
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    faces = []
    while explorer.More():
        face = TopoDS_Face(explorer.Current())
        faces.append(face)
        explorer.Next()
    return faces


def get_edges(shape: TopoDS_Shape) -> list:
    """Zwraca listę wszystkich krawędzi w kształcie."""
    explorer = TopExp_Explorer(shape, TopAbs_EDGE)
    edges = []
    while explorer.More():
        edge = TopoDS_Edge(explorer.Current())
        edges.append(edge)
        explorer.Next()
    return edges


def get_vertices(shape: TopoDS_Shape) -> list:
    """Zwraca listę wszystkich wierzchołków w kształcie."""
    explorer = TopExp_Explorer(shape, TopAbs_VERTEX)
    vertices = []
    while explorer.More():
        vertex = TopoDS_Vertex(explorer.Current())
        vertices.append(vertex)
        explorer.Next()
    return vertices


def get_face_center(face: TopoDS_Face) -> tuple:
    """Zwraca środek ściany jako krotkę (x, y, z)."""
    from OCC.Core.BRepTools import BRepTools_UVBounds
    from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
    
    surface = BRepAdaptor_Surface(face)
    umin, umax, vmin, vmax = BRepTools_UVBounds(face)
    u = (umin + umax) / 2
    v = (vmin + vmax) / 2
    
    pnt = surface.Value(u, v)
    return (pnt.X(), pnt.Y(), pnt.Z())


def get_face_normal(face: TopoDS_Face) -> tuple:
    """Zwraca wektor normalny ściany jako krotkę (x, y, z)."""
    from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
    
    surface = BRepAdaptor_Surface(face)
    surf_type = surface.GetType()
    
    if surf_type == 1:
        plane = surface.Plane()
        dirn = plane.Axis().Direction()
        return (dirn.X(), dirn.Y(), dirn.Z())
    
    umin, umax, vmin, vmax = BRepTools_UVBounds(face)
    u = (umin + umax) / 2
    v = (vmin + vmax) / 2
    
    dfu = surface.DU(u, v)
    dfv = surface.DV(u, v)
    
    normal = gp_Vec()
    normal.Cross(dfu, dfv)
    normal.Normalize()
    
    return (normal.X(), normal.Y(), normal.Z())


def get_bounding_box(shape: TopoDS_Shape) -> dict:
    """Zwraca obwiednię kształtu."""
    from OCC.Core.BRepBnd import BRepBnd_Add
    from OCC.Core.Bnd import Bnd_Box
    
    bbox = Bnd_Box()
    adder = BRepBnd_Add(shape)
    adder.Add(bbox)
    
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    
    return {
        "xmin": xmin, "ymin": ymin, "zmin": zmin,
        "xmax": xmax, "ymax": ymax, "zmax": zmax,
        "width": xmax - xmin,
        "height": ymax - ymin,
        "depth": zmax - zmin
    }


def project_to_2d(face: TopoDS_Face) -> np.ndarray:
    """Projektuje ścianę na płaszczyznę 2D."""
    normal = get_face_normal(face)
    
    edges = get_edges(face)
    vertices_2d = []
    
    for edge in edges:
        vertices = get_edge_vertices(edge)
        if vertices:
            v = vertices[0]
            p = BRep_Tool.Pnt(v)
            
            if abs(normal[2]) > 0.9:
                vertices_2d.append((p.X(), p.Y()))
            elif abs(normal[1]) > 0.9:
                vertices_2d.append((p.X(), p.Z()))
            else:
                vertices_2d.append((p.Y(), p.Z()))
    
    return np.array(vertices_2d) if vertices_2d else np.array([])


def get_edge_vertices(edge: TopoDS_Edge) -> list:
    """Zwraca wierzchołki krawędzi."""
    from OCC.Core.TopExp import TopExp
    
    vertex1 = TopoDS_Vertex()
    vertex2 = TopoDS_Vertex()
    
    exp = TopExp()
    exp.Vertices(edge, vertex1, vertex2)
    
    vertices = []
    if not vertex1.IsNull():
        vertices.append(vertex1)
    if not vertex2.IsNull():
        vertices.append(vertex2)
    
    return vertices