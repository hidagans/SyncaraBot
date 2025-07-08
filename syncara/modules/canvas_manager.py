class VirtualFile:
    def __init__(self, name, filetype="txt", content=""):
        self.name = name
        self.filetype = filetype
        # Process newline characters in content
        self.content = content.replace('\\n', '\n') if content else ""
        self.history = []

    def update_content(self, new_content):
        self.history.append(self.content)
        # Process newline characters in new content
        self.content = new_content.replace('\\n', '\n') if new_content else ""

    def append_content(self, addition):
        self.history.append(self.content)
        # Process newline characters in addition
        processed_addition = addition.replace('\\n', '\n') if addition else ""
        self.content += processed_addition

    def get_content(self):
        return self.content

    def export(self):
        return self.content  # Bisa diubah ke format file sesuai filetype

class CanvasManager:
    def __init__(self):
        self.files = {}

    def create_file(self, name, filetype="txt", content=""):
        try:
            from syncara.console import console
            console.info(f"Creating file: {name} with type: {filetype}")
            
            # Process content to handle newlines
            processed_content = content.replace('\\n', '\n') if content else ""
            
            self.files[name] = VirtualFile(name, filetype, processed_content)
            
            console.info(f"File created successfully: {name}")
            console.info(f"Current files in canvas: {list(self.files.keys())}")
            
            return self.files[name]
        except Exception as e:
            try:
                from syncara.console import console
                console.error(f"Error creating file {name}: {str(e)}")
            except:
                print(f"Error creating file {name}: {str(e)}")
            return None

    def get_file(self, name):
        try:
            from syncara.console import console
            console.info(f"Getting file: {name}")
            console.info(f"Available files: {list(self.files.keys())}")
            
            file = self.files.get(name)
            if file:
                console.info(f"File {name} found")
            else:
                console.warning(f"File {name} not found")
            
            return file
        except Exception as e:
            try:
                from syncara.console import console
                console.error(f"Error getting file {name}: {str(e)}")
            except:
                print(f"Error getting file {name}: {str(e)}")
            return None

    def list_files(self):
        try:
            from syncara.console import console
            console.info(f"Listing files: {list(self.files.keys())}")
            return list(self.files.keys())
        except Exception as e:
            try:
                from syncara.console import console
                console.error(f"Error listing files: {str(e)}")
            except:
                print(f"Error listing files: {str(e)}")
            return []

    def clear_files(self):
        """Clear all files from canvas"""
        try:
            from syncara.console import console
            console.info("Clearing all files from canvas")
            self.files.clear()
            console.info("Files cleared successfully")
        except Exception as e:
            try:
                from syncara.console import console
                console.error(f"Error clearing files: {str(e)}")
            except:
                print(f"Error clearing files: {str(e)}")

# Create singleton instance
canvas_manager = CanvasManager() 