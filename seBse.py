from pyfiles import FileDict
import reapy
project = reapy.Project()
project_name = project.name
FileDict.main(file="../base/base.txt",key = project_name,label="Корневая нота")