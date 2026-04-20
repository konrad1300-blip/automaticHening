from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TopoDS import TopoDS_Shape


class StepLoader:
    """Klasa do wczytywania plików STEP."""
    
    def load(self, file_path: str) -> TopoDS_Shape:
        """
        Wczytuje plik STEP i zwraca kształt.
        
        Args:
            file_path: Ścieżka do pliku STEP (.step lub .stp)
            
        Returns:
            TopoDS_Shape lub None w przypadku błędu
        """
        reader = STEPControl_Reader()
        status = reader.ReadFile(file_path)
        
        if status != IFSelect_RetDone:
            return None
        
        reader.TransferRoots()
        shape = reader.OneShape()
        return shape
    
    def load_multiple(self, file_path: str) -> list:
        """
        Wczytuje wszystkie kształty z pliku STEP.
        
        Args:
            file_path: Ścieżka do pliku STEP
            
        Returns:
            Lista TopoDS_Shape
        """
        reader = STEPControl_Reader()
        status = reader.ReadFile(file_path)
        
        if status != IFSelect_RetDone:
            return []
        
        reader.TransferRoots()
        results = []
        n = reader.NbShapes()
        for i in range(1, n + 1):
            shape = reader.Shape(i)
            if not shape.IsNull():
                results.append(shape)
        return results
    
    def get_shape_info(self, shape: TopoDS_Shape) -> dict:
        """
        Zwraca podstawowe informacje o kształcie.
        
        Args:
            shape: TopoDS_Shape
            
        Returns:
            Słownik z informacjami o kształcie
        """
        from OCC.Core.BRepBnd import BRepBnd_Add
        from OCC.Core.Bnd import Bnd_Box
        
        bbox = Bnd_Box()
        adder = BRepBnd_Add(shape)
        adder.Add(bbox)
        
        xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
        
        return {
            "width": xmax - xmin,
            "height": ymax - ymin,
            "depth": zmax - zmin,
            "xmin": xmin,
            "ymin": ymin,
            "zmin": zmin,
            "xmax": xmax,
            "ymax": ymax,
            "zmax": zmax
        }