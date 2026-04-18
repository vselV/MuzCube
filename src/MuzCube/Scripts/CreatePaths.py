import os
defPath = "C:/Users/vsevolod/AppData/Roaming/REAPER/Scripts"
cube = "/MuzCube"
project = "/Proj"
lod = "/Autoload"
def new_path(folder_path):
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    else:
        print("Папка уже существует!")

def make_dirs_cube(dir):
    muz_cube = dir+ cube
    new_path(muz_cube)
    proj = muz_cube + project
    new_path(proj)
    loads = muz_cube + lod
    new_path(loads)
def get_autoload_path():
    return defPath + cube + lod
def get_files_lod():
    path = get_autoload_path()
    files_only = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files_only
make_dirs_cube(defPath)