import os
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget,
                                QFileDialog, QToolBar, QStatusBar, QSplitter,
                                QMenuBar, QMenu)
from PySide6.QtGui import QAction, QKeySequence
from src.gui.occ_viewer_widget import OccViewerWidget
from src.core.step_loader import StepLoader


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutomaticHening")
        self.resize(1200, 800)
        
        self.viewer = OccViewerWidget()
        self.step_loader = StepLoader()
        self.current_file = None
        
        self._setup_ui()
        self._create_actions()
        self._create_menubar()
        self._create_toolbar()
        self._create_statusbar()
    
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.viewer)
    
    def _create_actions(self):
        self.open_action = QAction("&Otwórz STEP...", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self._open_step)
        
        self.generate_action = QAction("&Generuj plandekę", self)
        self.generate_action.setShortcut(QKeySequence("Ctrl+G"))
        self.generate_action.setEnabled(False)
        self.generate_action.triggered.connect(self._generate_tarpaulin)
        
        self.export_action = QAction("&Eksportuj...", self)
        self.export_action.setShortcut(QKeySequence("Ctrl+E"))
        self.export_action.setEnabled(False)
        self.export_action.triggered.connect(self._export_pattern)
        
        self.wall_off_action = QAction("Wyłącz &ścianę", self)
        self.wall_off_action.setShortcut(QKeySequence("Ctrl+W"))
        self.wall_off_action.triggered.connect(self._disable_wall)
    
    def _create_menubar(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        
        file_menu = menubar.addMenu("&Plik")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.generate_action)
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.wall_off_action)
        
        operations_menu = menubar.addMenu("&Operacje")
        operations_menu.addAction(self.generate_action)
        operations_menu.addAction(self.wall_off_action)
    
    def _create_toolbar(self):
        toolbar = QToolBar("Główne")
        self.addToolBar(toolbar)
        toolbar.addAction(self.open_action)
        toolbar.addSeparator()
        toolbar.addAction(self.generate_action)
        toolbar.addAction(self.wall_off_action)
    
    def _create_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Gotowy")
    
    def _open_step(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wybierz plik STEP", "",
            "STEP Files (*.stp *.step);;All Files (*.*)"
        )
        if file_path:
            self.status_bar.showMessage(f"Wczytywanie {os.path.basename(file_path)}...")
            shape = self.step_loader.load(file_path)
            if shape:
                self.viewer.display_shape(shape)
                self.current_file = file_path
                self.status_bar.showMessage(
                    f"Wczytano: {os.path.basename(file_path)}"
                )
                self.generate_action.setEnabled(True)
            else:
                self.status_bar.showMessage("Błąd wczytywania pliku")
    
    def _generate_tarpaulin(self):
        self.status_bar.showMessage("Generowanie plandeki...")
        self.generate_action.setEnabled(True)
    
    def _disable_wall(self):
        self.status_bar.showMessage("Ściana wyłączona")
    
    def _export_pattern(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Eksportuj wzór", "",
            "DXF Files (*.dxf);;PDF Files (*.pdf);;SVG Files (*.svg)"
        )
        if file_path:
            self.status_bar.showMessage(f"Eksportowano do: {file_path}")