import os

def create_target_folder(path, name):
    target_folder = os.path.join(path, name)
    
    try:
        os.makedirs(target_folder)
        return target_folder
    except OSError:
        return None

def save_output_to_file(folder, filename, content):
    file_path = os.path.join(folder, filename)
    
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return True
    except OSError:
        return False
