from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.AIS import AIS_InteractiveObject


def _init_occ_backend():
    """Initialize OCC Qt backend."""
    from OCC.Display.backend import load_backend
    load_backend('pyside6')


class OccViewerWidget(QWidget):
    """Widget 3D oparty na PythonOCC."""
    
    shape_loaded = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = None
        self.display = None
        self._setup_ui()
        self._init_viewer()
    
    def _setup_ui(self):
        self.setMinimumSize(800, 600)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        try:
            _init_occ_backend()
            from OCC.Display.qtDisplay import qtViewer3d
            self.canvas = qtViewer3d(self)
            layout.addWidget(self.canvas)
            self.display = self.canvas._display
            self.canvas.InitDriver()
        except Exception as e:
            print(f"OCC viewer failed, using fallback: {e}")
            self._setup_fallback_display(layout)
    
    def _setup_fallback_display(self, layout):
        try:
            from PySide6.QtOpenGL import QOpenGLWidget as OpenGLWidget
        except ImportError:
            from PySide6.QtGui import QOpenGLWidget as OpenGLWidget
        
        self.canvas = OpenGLWidget(self)
        self._gl_initialized = False
        self.canvas.initializeGL = self._init_gl
        self.canvas.paintGL = self._paint_gl
        layout.addWidget(self.canvas)
        self.display = None
    
    def _init_viewer(self):
        if self.display:
            self.display.DisplayShape(TopoDS_Shape())
            self.display.FitAll()
    
    def _init_gl(self):
        self._gl_initialized = True
    
    def _paint_gl(self):
        pass
    
    def display_shape(self, shape: TopoDS_Shape):
        """Wyświetla kształt w oknie."""
        if self.display:
            self.display.EraseAll()
            self.display.DisplayShape(shape, update=True)
            self.display.FitAll()
        self.shape_loaded.emit(shape)
    
    def display_ais_object(self, ais_object: AIS_InteractiveObject):
        """Wyświetla obiekt AIS w oknie."""
        if self.display:
            self.display.Context.Display(ais_object)
    
    def fit_all(self):
        """Dopasowuje widok do wszystkiego."""
        if self.display:
            self.display.FitAll()
    
    def erase_all(self):
        """Czyści widok."""
        if self.display:
            self.display.EraseAll()
    
    def get_shape(self):
        """Zwraca aktualnie wyświetlany kształt."""
        if self.display:
            return self.display.SelectedShape
        return None