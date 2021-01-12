from cx_Freeze import setup, Executable
import os
import os.path



PYTHON_INSTALL_DIR=os.path.dirname(os.path.dirname(os.__file__))
os.environ["TCL_LIBRARY"]=os.path.join(PYTHON_INSTALL_DIR,"tcl","tcl8.6")
os.environ["TK_LIBRARY"]=os.path.join(PYTHON_INSTALL_DIR, "tcl", "tk8.6")
setup(
	name="Hand_Recognition",
	options={"build_exe":{"packages":["numpy","cv2","PIL","threading"],"include_files":["C:\\Users\\MAKS\\AppData\\Local\\Programs\\Python\\Python36-32\\DLLs\\tcl86t.dll","C:\\Users\\MAKS\\AppData\\Local\\Programs\\Python\\Python36-32\\DLLs\\tk86t.dll"]}},
	version="1.0.0",
	description="Desc",
	executables=[Executable("index.py",base=None)]
)