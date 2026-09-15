import sys, os, subprocess

project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "overloaded-vehicle-detection")
PY = sys.executable

if __name__ == "__main__":
    proc = subprocess.run([PY, os.path.join(project_dir, "run.py")], cwd=project_dir)
    sys.exit(proc.returncode)
