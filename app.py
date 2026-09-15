import sys, os

# Forward execution to the inner project directory
project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "overloaded-vehicle-detection")
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

os.chdir(project_dir)

if __name__ == "__main__":
    import app
    app.main()
