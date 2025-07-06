class VirtualFile:
    def __init__(self, name, filetype="txt", content=""):
        self.name = name
        self.filetype = filetype
        self.content = content
        self.history = []

    def update_content(self, new_content):
        self.history.append(self.content)
        self.content = new_content

    def append_content(self, addition):
        self.history.append(self.content)
        self.content += addition

    def get_content(self):
        return self.content

    def export(self):
        return self.content  # Bisa diubah ke format file sesuai filetype

class CanvasManager:
    def __init__(self):
        self.files = {}

    def create_file(self, name, filetype="txt", content=""):
        self.files[name] = VirtualFile(name, filetype, content)
        return self.files[name]

    def get_file(self, name):
        return self.files.get(name)

    def list_files(self):
        return list(self.files.keys())

canvas_manager = CanvasManager() 