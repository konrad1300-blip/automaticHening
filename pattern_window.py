from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QMessageBox,
                             QGroupBox, QCheckBox, QRadioButton, QSpinBox,
                             QDoubleSpinBox, QComboBox, QFrame, QGraphicsView,
                             QGraphicsScene, QGraphicsPolygonItem, QGraphicsLineItem,
                             QGraphicsEllipseItem, QGraphicsTextItem, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF, QFont
import math


class PatternWindow(QMainWindow):
    def __init__(self, pattern, parent=None):
        super().__init__(parent)
        self.pattern = pattern
        self.parent_window = parent
        
        self.setWindowTitle("AutomaticHening - Wzór plandeki 2D")
        self.setGeometry(150, 150, 1100, 750)
        
        self.straps = []
        self.selected_strap = None
        self.reinforcements = []
        
        self.setup_ui()
        self.draw_pattern()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setBackgroundBrush(QBrush(QColor("#e8e8e8")))
        self.view.setMinimumSize(700, 600)
        
        self.view.mousePressEvent = self.on_mouse_press
        
        self.controls = QFrame()
        self.controls.setMaximumWidth(350)
        self.controls.setStyleSheet("background-color: #FAFAFA; border-left: 1px solid #E0E0E0;")
        
        controls_layout = QVBoxLayout(self.controls)
        controls_layout.setContentsMargins(15, 15, 15, 15)
        controls_layout.setSpacing(10)
        
        title = QLabel("Konfiguracja wzoru")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: #1E88E5; padding-bottom: 10px;")
        controls_layout.addWidget(title)
        
        info_group = QGroupBox("Informacje o wzorze")
        info_layout = QVBoxLayout(info_group)
        
        dim_text = f"Szerokość: {self.pattern['dimensions'].get('width', 0):.2f} m\n"
        dim_text += f"Wysokość: {self.pattern['dimensions'].get('height', 0):.2f} m\n"
        dim_text += f"Głębokość: {self.pattern['dimensions'].get('depth', 0):.2f} m"
        
        self.dimensions_label = QLabel(dim_text)
        self.dimensions_label.setStyleSheet("font-family: monospace; font-size: 12px;")
        info_layout.addWidget(self.dimensions_label)
        
        controls_layout.addWidget(info_group)
        
        seam_group = QGroupBox("Naddatek na szwy")
        seam_layout = QVBoxLayout(seam_group)
        
        self.seam_label = QLabel(f"Typ: {self.pattern['sewing_type']}")
        seam_layout.addWidget(self.seam_label)
        
        self.seam_margin_label = QLabel(f"Naddatek: {self.pattern['seam_allowance']*100:.1f} cm")
        seam_layout.addWidget(self.seam_margin_label)
        
        controls_layout.addWidget(seam_group)
        
        straps_group = QGroupBox("Paski zapięcia")
        straps_layout = QVBoxLayout(straps_group)
        
        straps_desc = QLabel("Kliknij na wzorze, aby dodać pasek")
        straps_desc.setStyleSheet("font-size: 11px; color: #666;")
        straps_desc.setWordWrap(True)
        straps_layout.addWidget(straps_desc)
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Typ:"))
        
        self.strap_type_combo = QComboBox()
        self.strap_type_combo.addItems(["Klamra Camet", "Grzechotka"])
        type_layout.addWidget(self.strap_type_combo)
        
        straps_layout.addLayout(type_layout)
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Szerokość pasa:"))
        
        self.strap_width_spin = QDoubleSpinBox()
        self.strap_width_spin.setRange(0.02, 0.10)
        self.strap_width_spin.setValue(0.03)
        self.strap_width_spin.setSuffix(" m")
        size_layout.addWidget(self.strap_width_spin)
        
        straps_layout.addLayout(size_layout)
        
        self.straps_list_label = QLabel("Dodane paski: 0")
        straps_layout.addWidget(self.straps_list_label)
        
        controls_layout.addWidget(straps_group)
        
        reinforce_group = QGroupBox("Wzmocnienia")
        reinforce_layout = QVBoxLayout(reinforce_group)
        
        self.auto_reinforce_check = QCheckBox("Automatyczne wzmocnienia")
        self.auto_reinforce_check.setChecked(True)
        reinforce_layout.addWidget(self.auto_reinforce_check)
        
        if self.parent_window and hasattr(self.parent_window, 'reinforce_size_spin'):
            size = self.parent_window.reinforce_size_spin.value()
        else:
            size = 0.10
        
        reinforce_size_layout = QHBoxLayout()
        reinforce_size_layout.addWidget(QLabel("Rozmiar:"))
        
        self.reinforce_size_spin = QDoubleSpinBox()
        self.reinforce_size_spin.setRange(0.05, 0.30)
        self.reinforce_size_spin.setValue(size)
        self.reinforce_size_spin.setSuffix(" m")
        reinforce_size_layout.addWidget(self.reinforce_size_spin)
        
        reinforce_layout.addLayout(reinforce_size_layout)
        
        self.reinforce_count_label = QLabel("Wzmocnień: 0")
        reinforce_layout.addWidget(self.reinforce_count_label)
        
        controls_layout.addWidget(reinforce_group)
        
        controls_layout.addStretch()
        
        export_group = QGroupBox("Eksport")
        export_layout = QVBoxLayout(export_group)
        
        export_dxf_btn = QPushButton("Eksportuj do DXF")
        export_dxf_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E88E5;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        export_dxf_btn.clicked.connect(self.export_dxf)
        export_layout.addWidget(export_dxf_btn)
        
        export_pdf_btn = QPushButton("Eksportuj do PDF")
        export_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        export_pdf_btn.clicked.connect(self.export_pdf)
        export_layout.addWidget(export_pdf_btn)
        
        controls_layout.addWidget(export_group)
        
        splitter.addWidget(self.view)
        splitter.addWidget(self.controls)
        splitter.setSizes([750, 350])
        
        main_layout.addWidget(splitter)
    
    def draw_pattern(self):
        self.scene.clear()
        self.scene.setSceneRect(-500, -500, 1000, 1000)
        
        scale = 300
        offset_x = 0
        offset_y = 0
        
        colors = [
            QColor(200, 220, 255),
            QColor(220, 255, 200),
            QColor(255, 220, 200),
            QColor(255, 255, 200),
            QColor(220, 200, 255),
            QColor(200, 255, 255)
        ]
        
        for i, face in enumerate(self.pattern.get("faces", [])):
            color = colors[i % len(colors)]
            
            points = []
            for v in face.get("vertices", []):
                x = v[0] * scale + offset_x
                y = -v[1] * scale + offset_y
                points.append(QPointF(x, y))
            
            polygon = QPolygonF(points)
            poly_item = QGraphicsPolygonItem(polygon)
            poly_item.setBrush(QBrush(color))
            poly_item.setPen(QPen(QColor("#333333"), 2))
            self.scene.addItem(poly_item)
            
            center = face.get("center", (0, 0))
            cx = center[0] * scale + offset_x
            cy = -center[1] * scale + offset_y
            
            label = QGraphicsTextItem(face.get("name", f"Ściana {i+1}"))
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            label.setDefaultTextColor(QColor("#333333"))
            label.setPos(cx - 20, cy - 8)
            self.scene.addItem(label)
            
            for j in range(len(points)):
                p1 = points[j]
                p2 = points[(j + 1) % len(points)]
                
                mid_x = (p1.x() + p2.x()) / 2 + offset_x
                mid_y = (p1.y() + p2.y()) / 2 + offset_y
                
                dim = math.sqrt((p1.x() - p2.x())**2 + (p1.y() - p2.y())**2)
                dim_cm = dim / scale * 100
                
                if dim_cm > 5:
                    dim_label = QGraphicsTextItem(f"{dim_cm:.1f} cm")
                    dim_label.setFont(QFont("Arial", 8))
                    dim_label.setDefaultTextColor(QColor("#666666"))
                    dim_label.setPos(mid_x - 15, mid_y - 6)
                    self.scene.addItem(dim_label)
        
        if self.pattern.get("excluded", []):
            exclude_label = QGraphicsTextItem("Wykluczone ściany:")
            exclude_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            exclude_label.setDefaultTextColor(QColor("#ff4444"))
            exclude_label.setPos(-100, -200)
            self.scene.addItem(exclude_label)
            
            excluded_text = ", ".join(str(e + 1) for e in self.pattern["excluded"])
            excl_label = QGraphicsTextItem(f"Ściany: {excluded_text}")
            excl_label.setFont(QFont("Arial", 10))
            excl_label.setDefaultTextColor(QColor("#666666"))
            excl_label.setPos(-80, -180)
            self.scene.addItem(excl_label)
    
    def on_mouse_press(self, event):
        pos = self.view.mapToScene(event.pos())
        
        strap_type = self.strap_type_combo.currentText()
        
        self.add_strap(pos, strap_type)
    
    def add_strap(self, pos, strap_type):
        width = self.strap_width_spin.value() * 300
        
        ellipse = QGraphicsEllipseItem(pos.x() - width/2, pos.y() - width/2, width, width)
        ellipse.setBrush(QBrush(QColor("#FF6F00")))
        ellipse.setPen(QPen(QColor("#E65100"), 3))
        self.scene.addItem(ellipse)
        
        label = QGraphicsTextItem("🔗" if strap_type == "Klamra Camet" else "⚙️")
        label.setFont(QFont("Arial", 14))
        label.setPos(pos.x() - 8, pos.y() - 8)
        self.scene.addItem(label)
        
        strap_info = {
            "position": (pos.x(), pos.y()),
            "type": strap_type,
            "width": width,
            "item": ellipse,
            "label": label
        }
        self.straps.append(strap_info)
        
        self.straps_list_label.setText(f"Dodane paski: {len(self.straps)}")
    
    def add_reinforcement(self, position, size):
        scaled_size = size * 300
        
        rect = QGraphicsRectItem(
            position.x() - scaled_size/2,
            position.y() - scaled_size/2,
            scaled_size,
            scaled_size
        )
        rect.setBrush(QBrush(QColor(255, 200, 200, 150)))
        rect.setPen(QPen(QColor("#cc0000"), 2, Qt.PenStyle.DashLine))
        self.scene.addItem(rect)
        
        self.reinforcements.append({
            "position": position,
            "size": size,
            "item": rect
        })
        
        self.reinforce_count_label.setText(f"Wzmocnień: {len(self.reinforcements)}")
    
    def export_dxf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Eksportuj do DXF",
            "",
            "DXF Files (*.dxf)"
        )
        
        if file_path:
            try:
                import ezdxf
                
                doc = ezdxf.document.new()
                msp = doc.modelspace()
                
                scale = 300
                
                for face in self.pattern.get("faces", []):
                    points = []
                    for v in face.get("vertices", []):
                        x = v[0] * scale
                        y = -v[1] * scale
                        points.append((x, y))
                    
                    for i in range(len(points)):
                        p1 = points[i]
                        p2 = points[(i + 1) % len(points)]
                        msp.add_line(p1, p2)
                
                doc.saveas(file_path)
                QMessageBox.information(self, "Sukces", f"Zapisano do: {file_path}")
                
            except ImportError:
                self.create_simple_dxf(file_path)
    
    def create_simple_dxf(self, file_path):
        with open(file_path, 'w') as f:
            f.write("0\nSECTION\n2\nENTITIES\n")
            
            scale = 300
            
            for face in self.pattern.get("faces", []):
                points = []
                for v in face.get("vertices", []):
                    x = v[0] * scale
                    y = -v[1] * scale
                    points.append((x, y))
                
                for i in range(len(points)):
                    p1 = points[i]
                    p2 = points[(i + 1) % len(points)]
                    
                    f.write(f"0\nLINE\n")
                    f.write(f"8\n0\n")
                    f.write(f"10\n{p1[0]}\n20\n{p1[1]}\n30\n0\n")
                    f.write(f"11\n{p2[0]}\n21\n{p2[1]}\n31\n0\n")
            
            f.write("0\nENDSEC\n0\nEOF\n")
        
        QMessageBox.information(self, "Sukces", f"Zapisano do: {file_path}")
    
    def export_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Eksportuj do PDF",
            "",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.pdfgen import canvas
                
                c = canvas.Canvas(file_path, pagesize=A4)
                width, height = A4
                
                c.setFont("Helvetica", 16)
                c.drawString(50, height - 50, "Wzor plandeki")
                
                c.setFont("Helvetica", 12)
                
                info_text = f"Szerokosc: {self.pattern['dimensions'].get('width', 0):.2f} m"
                c.drawString(50, height - 80, info_text)
                
                info_text = f"Wysokosc: {self.pattern['dimensions'].get('height', 0):.2f} m"
                c.drawString(50, height - 100, info_text)
                
                c.save()
                
                QMessageBox.information(self, "Sukces", f"Zapisano do: {file_path}")
                
            except ImportError:
                QMessageBox.warning(self, "Ostrzeżenie", "Biblioteka reportlab nie jest zainstalowana.")