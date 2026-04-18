def getPaths(file):
    path = file.split("/")
    sPath = ""
    for i in range(len(path) - 1):
        sPath += path[i] + "/"
    file_midi = sPath + "midi/" + path[len(path) - 1].replace(".muz", ".mid")
    file_vis = sPath + "visual/" + path[len(path) - 1].replace(".muz", ".vis")
   # print(file_midi, file_vis)
    return (file_midi, file_vis)