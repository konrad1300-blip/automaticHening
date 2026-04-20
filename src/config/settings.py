class Settings:
    """Konfiguracja aplikacji."""
    
    def __init__(self):
        self.seam_allowance = 0.015
        self.sewing_type = "zszywana"
        self.velcro_width = 0.03
        self.auto_reinforcement = True
        self.reinforcement_size = 0.10
        
        self.window_width = 1200
        self.window_height = 800
        
        self.recent_files = []
        self.max_recent_files = 10
    
    def set_seam_allowance(self, value: float):
        self.seam_allowance = value
    
    def set_sewing_type(self, type_: str):
        if type_ in ["zszywana", "zgrzewana"]:
            self.sewing_type = type_
            if type_ == "zszywana":
                self.seam_allowance = 0.015
            else:
                self.seam_allowance = 0.025
    
    def add_recent_file(self, file_path: str):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        self.recent_files.insert(0, file_path)
        
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]
    
    def get_recent_files(self) -> list:
        return self.recent_files


DEFAULT_SETTINGS = Settings()