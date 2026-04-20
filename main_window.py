from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QMessageBox,
                             QMenuBar, QMenu, QToolBar, QStatusBar, QDockWidget,
                             QListWidget, QFrame, QGraphicsView, QGraphicsScene,
                             QSlider, QCheckBox, QRadioButton, QGroupBox, QSpinBox,
                             QDoubleSpinBox, QComboBox, QTextEdit, QSplitter, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QTimer
from PyQt6.QtGui import QAction, QIcon, QFont, QPalette, QColor, QPainter, QBrush, QPolygonF
import math
import numpy as np
from pathlib import Path

try:
    from PyQt6.QtOpenGL import QOpenGLWidget
    from OpenGL.GL import *
    HAS_OPENGL = True
except (ImportError, Exception):
    HAS_OPENGL = False
    QOpenGLWidget = None


class MainWindow(QMainWindow):
    pattern_generated = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutomaticHening - Projektant plandek")
        self.setGeometry(100, 100, 1200, 800)
        
        self.current_file = None
        self.step_data = None
        self.vertices = []
        self.faces = []
        self.pattern_faces = []
        self.excluded_faces = []
        self.seam_allowance = 0.015
        self.sewing_type = "zszywana"
        self.velcro_width = 0.03
        
        self.view_rotation = [30, 45, 0]
        self.view_zoom = 1.0
        self.view_pan = [0, 0]
        
        self.is_dragging = False
        self.last_mouse_pos = None
        
        self.setup_ui()
        self.create_menus()
        self.create_toolbar()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        if HAS_OPENGL and QOpenGLWidget is not None:
            self.view_3d = QOpenGLWidget(self)
            self.view_3d.setMinimumSize(800, 600)
            self.view_3d.setCursor(Qt.CursorShape.CrossCursor)
            self.view_3d.mousePressEvent = self.on_3d_mouse_press
            self.view_3d.mouseMoveEvent = self.on_3d_mouse_move
            self.view_3d.wheelEvent = self.on_3d_wheel
            self.view_3d.paintGL = self.paint_3d
        else:
            self.view_3d = self.create_simple_3d_view()
        
        self.scene = QGraphicsScene()
        self.view_2d = QGraphicsView(self.scene)
        self.view_2d.setMinimumSize(400, 600)
        self.view_2d.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view_2d.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view_2d.setBackgroundBrush(QBrush(QColor("#f5f5f5")))
        
        splitter.addWidget(self.view_3d)
        splitter.addWidget(self.view_2d)
        splitter.setSizes([800, 400])
        
        main_layout.addWidget(splitter)
        
        self.statusBar().showMessage("Gotowy")
        
        self.left_panel = QFrame()
        self.left_panel.setMaximumWidth(280)
        self.left_panel.setStyleSheet("background-color: #FAFAFA; border-right: 1px solid #E0E0E0;")
        
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(10)
        
        config_label = QLabel("Konfiguracja plandeki")
        config_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #1E88E5;")
        left_layout.addWidget(config_label)
        
        seam_group = QGroupBox("Rodzaj połączenia")
        seam_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        seam_layout = QVBoxLayout(seam_group)
        
        self.radio_sewing = QRadioButton("Zszywana (naddatek 1.5cm)")
        self.radio_sewing.setChecked(True)
        self.radio_sewing.toggled.connect(self.on_seam_type_changed)
        seam_layout.addWidget(self.radio_sewing)
        
        self.radio_welding = QRadioButton("Zgrzewana (naddatek 2.5cm)")
        self.radio_welding.toggled.connect(self.on_seam_type_changed)
        seam_layout.addWidget(self.radio_welding)
        
        left_layout.addWidget(seam_group)
        
        faces_group = QGroupBox("Ściany do wykluczenia")
        faces_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        faces_layout = QVBoxLayout(faces_group)
        
        self.faces_list = QListWidget()
        self.faces_list.setMaximumHeight(120)
        faces_layout.addWidget(self.faces_list)
        
        self.velcro_check = QCheckBox("Połączenie na rzep")
        self.velcro_check.setEnabled(False)
        faces_layout.addWidget(self.velcro_check)
        
        velcro_layout = QHBoxLayout()
        velcro_layout.addWidget(QLabel("Szerokość:"))
        self.velcro_width_spin = QDoubleSpinBox()
        self.velcro_width_spin.setRange(0.01, 0.10)
        self.velcro_width_spin.setValue(0.03)
        self.velcro_width_spin.setSuffix(" m")
        self.velcro_width_spin.setEnabled(False)
        velcro_layout.addWidget(self.velcro_width_spin)
        faces_layout.addLayout(velcro_layout)
        
        left_layout.addWidget(faces_group)
        
        reinforce_group = QGroupBox("Wzmocnienia")
        reinforce_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        reinforce_layout = QVBoxLayout(reinforce_group)
        
        self.auto_reinforce_check = QCheckBox("Automatyczne wzmocnienia")
        self.auto_reinforce_check.setChecked(True)
        reinforce_layout.addWidget(self.auto_reinforce_check)
        
        reinforce_size_layout = QHBoxLayout()
        reinforce_size_layout.addWidget(QLabel("Rozmiar:"))
        self.reinforce_size_spin = QDoubleSpinBox()
        self.reinforce_size_spin.setRange(0.05, 0.30)
        self.reinforce_size_spin.setValue(0.10)
        self.reinforce_size_spin.setSuffix(" m")
        reinforce_size_layout.addWidget(self.reinforce_size_spin)
        reinforce_layout.addLayout(reinforce_size_layout)
        
        left_layout.addWidget(reinforce_group)
        
        left_layout.addStretch()
        
        dock = QDockWidget("Opcje", self)
        dock.setWidget(self.left_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        
    def create_simple_3d_view(self):
        scene_3d = QGraphicsScene()
        view_3d = QGraphicsView(scene_3d)
        view_3d.setMinimumSize(800, 600)
        view_3d.setCursor(Qt.CursorShape.CrossCursor)
        view_3d.setBackgroundBrush(QBrush(QColor("#e0e0e0")))
        
        self.simple_3d_scene = scene_3d
        self.simple_3d_view = view_3d
        
        view_3d.mousePressEvent = self.on_3d_mouse_press_simple
        view_3d.mouseMoveEvent = self.on_3d_mouse_move_simple
        view_3d.wheelEvent = self.on_3d_wheel
        
        self.draw_simple_model()
        
        return view_3d
    
    def draw_simple_model(self):
        if not hasattr(self, 'simple_3d_scene') or not self.simple_3d_scene:
            return
        
        self.simple_3d_scene.clear()
        
        scale = 150
        center_x = 400
        center_y = 300
        
        colors = [
            QColor(100, 150, 255),
            QColor(100, 200, 100),
            QColor(255, 150, 100),
            QColor(255, 255, 100),
            QColor(200, 100, 255),
            QColor(100, 255, 255)
        ]
        
        rotation_x = self.view_rotation[0]
        rotation_y = self.view_rotation[1]
        
        transformed_vertices = []
        for v in self.vertices:
            x, y, z = v
            
            angle_rad = math.radians(rotation_y)
            x_rot = x * math.cos(angle_rad) - z * math.sin(angle_rad)
            z_rot = x * math.sin(angle_rad) + z * math.cos(angle_rad)
            x, z = x_rot, z_rot
            
            angle_rad = math.radians(rotation_x)
            y_rot = y * math.cos(angle_rad) - z * math.sin(angle_rad)
            z_rot = y * math.sin(angle_rad) + z * math.cos(angle_rad)
            y = y_rot
            
            transformed_vertices.append((x * scale + center_x, -z * scale + center_y, y * scale))
        
        for i, face in enumerate(self.faces):
            color = colors[i % len(colors)]
            
            points = []
            for v_idx in face["vertices"]:
                pts = transformed_vertices[v_idx]
                points.append(QPointF(pts[0], pts[1]))
            
            polygon = QPolygonF(points)
            poly_item = QGraphicsPolygonItem(polygon)
            poly_item.setBrush(QBrush(color))
            poly_item.setPen(QPen(QColor("#333333"), 2))
            self.simple_3d_scene.addItem(poly_item)
    
    def on_3d_mouse_press_simple(self, event):
        self.is_dragging = True
        self.last_mouse_pos = event.pos()
    
    def on_3d_mouse_move_simple(self, event):
        if self.is_dragging and self.last_mouse_pos:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            
            self.view_rotation[0] += dy * 0.5
            self.view_rotation[1] += dx * 0.5
            
            self.view_rotation[0] = max(-90, min(90, self.view_rotation[0]))
            
            self.last_mouse_pos = event.pos()
            self.draw_simple_model()
    
    def create_menus(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("background-color: #FAFAFA;")
        
        file_menu = menubar.addMenu("Plik")
        
        open_action = QAction("Otwórz STEP...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_step_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("Eksportuj...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setEnabled(False)
        export_action.triggered.connect(self.export_pattern)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Wyjdź", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu("Widok")
        
        reset_view_action = QAction("Resetuj widok", self)
        reset_view_action.setShortcut("Ctrl+0")
        reset_view_action.triggered.connect(self.reset_view)
        view_menu.addAction(reset_view_action)
        
        generate_menu = menubar.addMenu("Generuj")
        
        generate_action = QAction("Generuj plandekę", self)
        generate_action.setShortcut("Ctrl+G")
        generate_action.triggered.connect(self.generate_tarpaulin)
        generate_menu.addAction(generate_action)
        
        help_menu = menubar.addMenu("Pomoc")
        
        about_action = QAction("O programie", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        toolbar = QToolBar("Główne narzędzia")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #1E88E5;
                border: none;
                spacing: 5px;
                padding: 5px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.addToolBar(toolbar)
        
        open_btn = QPushButton("📂 Otwórz")
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        open_btn.clicked.connect(self.open_step_file)
        toolbar.addWidget(open_btn)
        
        toolbar.addSeparator()
        
        rotate_btn = QPushButton("🔄 Obróć")
        rotate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rotate_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        rotate_btn.clicked.connect(lambda: self.set_rotation_mode(True))
        toolbar.addWidget(rotate_btn)
        
        zoom_in_btn = QPushButton("🔍+")
        zoom_in_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        zoom_in_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        zoom_in_btn.clicked.connect(lambda: self.zoom(1.2))
        toolbar.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("🔍-")
        zoom_out_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        zoom_out_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        zoom_out_btn.clicked.connect(lambda: self.zoom(0.8))
        toolbar.addWidget(zoom_out_btn)
        
        toolbar.addSeparator()
        
        generate_btn = QPushButton("🎯 Generuj plandekę")
        generate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6F00;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF8F00;
            }
        """)
        generate_btn.clicked.connect(self.generate_tarpaulin)
        toolbar.addWidget(generate_btn)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
    
    def open_step_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Otwórz plik STEP",
            "",
            "STEP Files (*.step *.stp);;All Files (*)"
        )
        
        if file_path:
            self.current_file = file_path
            self.load_step_file(file_path)
    
    def load_step_file(self, file_path):
        try:
            self.statusBar().showMessage(f"Wczytywanie: {Path(file_path).name}")
            self.parse_step_file(file_path)
            self.statusBar().showMessage(f"Wczytano: {Path(file_path).name}")
            self.view_3d.update()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie można wczytać pliku: {str(e)}")
    
    def parse_step_file(self, file_path):
        self.vertices = [
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
            [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
        ]
        
        self.faces = [
            {"vertices": [0, 1, 2, 3], "normal": [0, 0, -1], "name": "Przód"},
            {"vertices": [4, 5, 6, 7], "normal": [0, 0, 1], "name": "Tył"},
            {"vertices": [0, 4, 5, 1], "normal": [0, -1, 0], "name": "Dół"},
            {"vertices": [2, 6, 7, 3], "normal": [0, 1, 0], "name": "Góra"},
            {"vertices": [0, 3, 7, 4], "normal": [-1, 0, 0], "name": "Lewo"},
            {"vertices": [1, 5, 6, 2], "normal": [1, 0, 0], "name": "Prawo"}
        ]
        
        self.faces_list.clear()
        for i, face in enumerate(self.faces):
            self.faces_list.addItem(f"{i+1}. {face['name']}")
        
        self.create_sample_model()
    
    def create_sample_model(self):
        box = {
            "width": 1.0,
            "height": 1.0,
            "depth": 1.0
        }
        self.model_bounds = box
    
    def paint_3d(self):
        from OpenGL.GL import glClear, glClearColor, glEnable, glBlendFunc, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
        from OpenGL.GL import glLoadIdentity, glTranslatef, glRotatef, glScalef
        from OpenGL.GL import glBegin, glEnd, glVertex3f, glColor3f, GL_QUADS, GL_LINES
        from OpenGL import GL
        
        glClearColor(0.95, 0.95, 0.95, 1.0)
        glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        glEnable(GL.GL_DEPTH_TEST)
        glEnable(GL.GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glLoadIdentity()
        glTranslatef(0, 0, -3)
        glRotatef(self.view_rotation[0], 1, 0, 0)
        glRotatef(self.view_rotation[1], 0, 1, 0)
        glScalef(self.view_zoom, self.view_zoom, self.view_zoom)
        
        self.draw_model()
    
    def draw_model(self):
        from OpenGL.GL import glBegin, glEnd, glVertex3f, glColor3f, glNormal3f, GL_QUADS
        
        colors = [
            (0.3, 0.5, 0.9),
            (0.3, 0.5, 0.9),
            (0.4, 0.6, 0.3),
            (0.4, 0.6, 0.3),
            (0.9, 0.4, 0.3),
            (0.9, 0.4, 0.3)
        ]
        
        for face_idx, face in enumerate(self.faces):
            glBegin(GL_QUADS)
            color = colors[face_idx % len(colors)]
            glColor3f(*color)
            
            for v_idx in face["vertices"]:
                v = self.vertices[v_idx]
                n = face["normal"]
                glNormal3f(*n)
                glVertex3f(*v)
            glEnd()
    
    def on_3d_mouse_press(self, event):
        self.is_dragging = True
        self.last_mouse_pos = event.pos()
    
    def on_3d_mouse_move(self, event):
        if self.is_dragging and self.last_mouse_pos:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            
            self.view_rotation[0] += dy * 0.5
            self.view_rotation[1] += dx * 0.5
            
            self.view_rotation[0] = max(-90, min(90, self.view_rotation[0]))
            
            self.last_mouse_pos = event.pos()
            self.view_3d.update()
    
    def on_3d_wheel(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom(1.1)
        else:
            self.zoom(0.9)
    
    def zoom(self, factor):
        self.view_zoom *= factor
        self.view_zoom = max(0.1, min(10, self.view_zoom))
        self.view_3d.update()
    
    def set_rotation_mode(self, enabled):
        if enabled:
            self.view_3d.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.view_3d.setCursor(Qt.CursorShape.ArrowCursor)
    
    def reset_view(self):
        self.view_rotation = [30, 45, 0]
        self.view_zoom = 1.0
        self.view_pan = [0, 0]
        self.view_3d.update()
    
    def on_seam_type_changed(self):
        if self.radio_sewing.isChecked():
            self.sewing_type = "zszywana"
            self.seam_allowance = 0.015
        else:
            self.sewing_type = "zgrzewana"
            self.seam_allowance = 0.025
    
    def generate_tarpaulin(self):
        from pattern_window import PatternWindow
        
        if not self.vertices:
            QMessageBox.warning(self, "Ostrzeżenie", "Najpierw wczytaj plik STEP")
            return
        
        excluded = []
        for idx in self.faces_list.selection:
            excluded.append(idx)
        
        pattern = self.calculate_pattern(excluded)
        
        pattern_window = PatternWindow(pattern, self)
        pattern_window.show()
    
    def calculate_pattern(self, excluded_indices):
        pattern = {
            "faces": [],
            "dimensions": {},
            "excluded": excluded_indices,
            "seam_allowance": self.seam_allowance,
            "sewing_type": self.sewing_type
        }
        
        for i, face in enumerate(self.faces):
            if i not in excluded_indices:
                poly = self.project_face_2d(face, i)
                pattern["faces"].append(poly)
        
        pattern["dimensions"] = self.model_bounds
        
        return pattern
    
    def project_face_2d(self, face, face_idx):
        vertices = face["vertices"]
        v_coords = [self.vertices[i] for i in vertices]
        
        normal = face["normal"]
        
        if abs(normal[2]) > 0.5:
            proj_verts = [(v[0], v[1]) for v in v_coords]
        elif abs(normal[1]) > 0.5:
            proj_verts = [(v[0], v[2]) for v in v_coords]
        else:
            proj_verts = [(v[1], v[2]) for v in v_coords]
        
        poly = {
            "vertices": proj_verts,
            "face_idx": face_idx,
            "normal": normal,
            "name": face["name"],
            "center": self.calculate_centroid(proj_verts)
        }
        
        return poly
    
    def calculate_centroid(self, vertices):
        n = len(vertices)
        cx = sum(v[0] for v in vertices) / n
        cy = sum(v[1] for v in vertices) / n
        return cx, cy
    
    def export_pattern(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Eksportuj wzór",
            "",
            "DXF Files (*.dxf);;PDF Files (*.pdf);;SVG Files (*.svg)"
        )
        
        if file_path:
            self.statusBar().showMessage(f"Eksportowano do: {file_path}")
    
    def show_about(self):
        QMessageBox.about(
            self,
            "O programie",
            "AutomaticHening v1.0\n\n"
            "Program do projektowania plandek.\n\n"
            "Automatycznie generuje wzory z plików STEP."
        )
    
    def closeEvent(self, event):
        event.accept()