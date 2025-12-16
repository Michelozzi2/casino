import os
import subprocess

from celery import Celery

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

from api.config import devsimpy_nogui

@celery.task(name="create_sim")
def create_sim(yaml_filename:str, duration:str, name:str=""):
    """Create a simulation

    Args:
        yaml_filename (str): YAML filemane to simulate.
        duration (str): Duration of the simulation.
        name (str Optional): Name of the simuation.

    Returns:
        _type_: dict including the result of the simulation.
    """
    args = [str(duration)]
    
    if name: 
        args.extend(['-name',str(name)])
      
    output = execute_cmd(yaml_filename, args)

    if output['success']:
        # Decode and clean the binary result from the subprocess
        data = output['output'].decode('utf-8')
        data = data.replace("'", "\"").replace("\n", "")
        data = "[" + data.replace("}{", "},{") + "]"  # Enclose individual objects in an array
        output['output'] = data

    return output

def execute_cmd(yaml_filename:str,args:list):
    """Execute the cmd to simulate the yaml file with args.

    Args:
        yaml_filename (str): YAML file to execute with devsimpy-nogui
        args (list): Params passed to the devsimpy-nogui.

    Returns:
        _type_: dict including the result of the execution (simulation)
    """
    # Command to be executed
    cmd = ["python", devsimpy_nogui, yaml_filename] + args

    ## execute command using check_out
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = {'success': False, 'output': "", "info": str(e.output)}
    else:
        output = {'success': True, 'output': result, "info":""}

    return output