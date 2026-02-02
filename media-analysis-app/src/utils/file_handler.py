def save_file(file, destination):
    """Save a file to the specified destination."""
    with open(destination, 'wb') as f:
        f.write(file.getbuffer())

def load_file(file_path):
    """Load a file from the specified path."""
    with open(file_path, 'rb') as f:
        return f.read()