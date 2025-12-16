import os

############################################### set by the user
current_api_path = os.path.dirname(__file__)
devsimpy_dir = 'devsimpy-nogui'
yaml_path_dir = os.path.join(current_api_path, 'static', 'yaml')
users_path_dir = os.path.join(os.path.dirname(current_api_path), 'users')
devsimpy_nogui = os.path.join(current_api_path, devsimpy_dir, 'devsimpy-nogui.py')