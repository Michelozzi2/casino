"""
Primary API route endpoints

"""
from celery.result import AsyncResult
from fastapi import Query, Depends, HTTPException, APIRouter, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, validator

from .worker import execute_cmd, create_sim
from api.config import yaml_path_dir, users_path_dir

import shutil, os, time

# Init FastAPI router for API endpoints
api_routes = APIRouter()

def getYAMLFile(filename:str, path:str=users_path_dir)->dict:
    """Get yaml file with json format from path.

    Args:

        filename (str): YAML filename
        
        path (str, optional): Path that contains the YAML files. Defaults to users_path_dir.

    Returns:
        
        dict: JSON flow with file name as key and YAML description as value.
    """
    filename_path = os.path.join(path, filename)
    return dict([(filename, open(filename_path, 'r').read())]) if os.path.exists(filename_path) else {}

def getYAMLFiles(path:str=users_path_dir)->dict:
    """Get existing yaml files in path.

    Args:
        
        path (str, optional): Path that contains the YAML files. Defaults to users_path_dir.

    Returns:
        
        dict: JSON flow with file name as key and YAML description as value.
    """
    return dict([(entry, open(os.path.join(path, entry), 'r').read())\
                for entry in os.listdir(path)\
                if entry.endswith('.yaml')])

def getYAMLFilenames(path:str=users_path_dir)->dict:
    """Get all yaml file names in path.

    Args:
        
        path (str, optional): Path that contains the YAML files. Defaults to users_path_dir.

    Returns:
        
        dict: JSON flow with filename as key and a dict with YAML description,size and last modified date as value.
    """
    return dict([(entry, {'last modified':str(time.ctime(os.path.getmtime(os.path.join(path, entry)))), 'size':str(os.path.getsize(os.path.join(path, entry))*0.001)+' ko'})\
                for entry in os.listdir(path)\
                if entry.endswith('.yaml')])

############################################################################
@api_routes.get("/")
def home():
    """Get the static html page.

    Returns:
        
        _type_: str
    """
    return FileResponse("api/static/index.html")

############################################################################
### to use: https://..../yaml/all to have all static/yaml files description
class ResponseModelGetYAML(BaseModel):
    success: bool= True
    content: dict= {}

@api_routes.get("/yaml/all", response_model=ResponseModelGetYAML)
def get_all_stored_yaml():
    """Get all existing YAML files stored in the server.

    Returns:
        
        _type_: JSON with success (bool) as key and the YAML description as value.
    """
    data = getYAMLFiles(yaml_path_dir) | getYAMLFiles(users_path_dir)
    return { "success": True, "content": data }

############################################################################
### to use: https://.../yaml/filenames to have the filenamne of the static/yaml files
@api_routes.get("/yaml/filenames", response_model=ResponseModelGetYAML)
def get_stored_yaml_filenames():
    """Get all existing YAML file names stored in the server.

    Returns:
        
        _type_: JSON with success (bool) as key and the list of the YAML file names as value.
    """
    data = getYAMLFilenames()
    return { "success": True, "content": data }

############################################################################
### to use: https://.../yaml/SimpleTradeWithPredictions.yaml to have the description of SimpleTradeWithPredictions.yaml
def validate_filename(filename:str):
    """ Filename must have .yaml extention and in the static/yaml or users directory.
    """
    if filename and not (filename.endswith(".yaml") and os.path.exists(os.path.join(users_path_dir, filename)) or os.path.exists(os.path.join(yaml_path_dir, filename))):
        # List all files in the directory
        all_files = os.listdir(yaml_path_dir)+os.listdir(users_path_dir)
        # Filter only files with .yaml extension
        yaml_files = [file for file in all_files if file.endswith(".yaml")]
        raise HTTPException(status_code=422, detail=f"Name {filename} must exist and end with '.yaml'. The possible YAML files are in {yaml_files}")
    return filename

@api_routes.get("/yaml/{filename}", response_model=ResponseModelGetYAML)
def get_yaml_data(filename: str = Depends(validate_filename)):
    """Get the description of the YAML file name.

    Args:
        
        filename (str, optional): YAML file name. Defaults to Depends(validate_filename).

    Returns:
        
        _type_: JSON with success (bool) as key and the YAML description as value.
    """ 
    data = getYAMLFile(filename,users_path_dir) or getYAMLFile(filename,yaml_path_dir) if filename else {}
    return { "success": bool(filename), "content": data }
    
############################################################################
### to use: https://.../yaml/models/?filename=SimpleTradeWithPredictions.yaml
### to use: https://.../yaml/models/?filename=SimpleTradeWithPredictions.yaml&model=Env
class ResponseModelGetYAMLModel(BaseModel):
    success: bool = True
    output: str = "[\"Indexes\", \"Env\", \"Agent\"]"
    info: str = ""

@api_routes.get('/yaml/models/', response_model=ResponseModelGetYAMLModel)
def get_yaml_models_description(filename:str = Depends(validate_filename), model:str=Query("", description="Get the model parameters", example="Env")):
    """Get the model blocks list from YAML file name.

    Args:
        
        filename (str, optional): YAML file name. Defaults to Depends(validate_filename).
        
        model (str, optional): Name of the targeted model. Defaults to Query(None, description="Get the model parameters").

    Returns:
        
        _type_: The list of the model names included in the model.
    """
    args = ['-blockargs', str(model)] if model else ['-blockslist']
    path = yaml_path_dir if os.path.exists(os.path.join(yaml_path_dir, filename)) else users_path_dir
    return execute_cmd(os.path.join(path, filename), args)

############################################################################
### POST body (mode raw et type JSON) example:
### {"filename":"SimpleTrade.yaml", "model":"Env", "args":{"cash":1000}}
class ResponseModelUpdateYAML(BaseModel):
    success: bool = True
    output: str = "{\"success\": true, \"args\": {\"M\": 1, \"N\": 10, \"cash\": 10000, \"goal_reward\": true}}"
    info: str = ""

class UpdateYAMLQueryParam(BaseModel):
    userid: str = "test"
    filename: str = "SimpleTradeWithPredictions.yaml"
    model: str = "Env"
    args: dict = {"cash":10000}

    @validator("filename")
    def validate_filename(cls, value):
        if value and not (value.endswith(".yaml") and os.path.exists(os.path.join(yaml_path_dir,value))):
            raise ValueError(f"Filename must exist in {yaml_path_dir} and end with '.yaml'")
        return value
    
@api_routes.post("/yaml/update",response_model=ResponseModelUpdateYAML)
async def update_yaml_file(request_data: UpdateYAMLQueryParam):
    """Update a YAML file.

    Args:
        
        userid (str): ID of the simulation to execute.
        
        model (str): Name of a model inside the YAML model to be changed.
        
        filename (str): YAML file name corresponding to the model to simulate.
        
        args (dict): Couples key:value to change in the model.

    Returns:
        
        dict: Information about the udpate including the success and the news args.
    """
    ### yaml file is in /users dir and is construct as userid_filename (if request_data.userid == "", the filename is considered)
    yaml_filename = request_data.userid+'_'+request_data.filename if request_data.userid else request_data.filename
    yaml_filename_path = os.path.join(users_path_dir if request_data.userid else yaml_path_dir,yaml_filename) 
    
    ### if yaml file doesn't exist for the user, we copy the yaml_path_dir/filename into the /user
    if request_data.userid and not os.path.exists(yaml_filename_path):    
        # Copy the file
        source_file = os.path.join(yaml_path_dir,request_data.filename)
        destination_file = yaml_filename_path
        shutil.copy(source_file, destination_file)

    args = [
        '-blockargs', str(request_data.model),
        '-updateblockargs', str(request_data.args).replace("'", '"')
    ]
    return execute_cmd(yaml_filename_path, args)

############################################################################
### to use: /yaml/upload
def save_uploaded_file(upload_dir: str, file: UploadFile):
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file_path

@api_routes.post("/yaml/upload")
async def upload_yaml(file: UploadFile = File(..., description="YAML file to upload on the server")):
    """Upload YAML file in the static/yaml directory.

    Args:
        file (UploadFile, optional): _description_. Defaults to File(..., description="YAML file to upload on the server").

    Raises:
        HTTPException: Uploaded file msut avec .yaml extention.

    Returns:
        _type_: JSON flow
    """
    if not file.filename.endswith('.yaml'):
        raise HTTPException(status_code=404, detail="File must be an yaml!")
    
    ### upload in the yaml dir
    file_path = save_uploaded_file(yaml_path_dir, file)
    return {"success":True, "message": "File uploaded successfully", "file_path": file_path}

############################################################################
### to use: /simulation/start/?duration=ntl&filename=SimpleTradeWithPredictions.yaml' 
### or: /simulation/start/?userid=test&duration=ntl&filename=SimpleTradeWithPredictions.yaml'
@api_routes.get('/simulation/start/')
async def start_simulation(userid: str = Query("", title="User ID", description="ID of the user that wants to execute a simulation", example="jhon"),
                         duration: str = Query(..., title="Duration of the simulation", description="Duration of the simulation (ntl, inf or a digit is possible)", example="ntl"),
                         filename: str = Depends(validate_filename),
                         tag: str = Query("", title="Tag", description="Meta data related to the app used by a user that requests the simulation", example="MyApp")):
    """
    Start a simulation from a <filename> YAML model for <duration> simulation cycle.
    Warning: if userid is not empty, the filename userid_filename must exist. This endpoint dont create user file. For that, please use the /yaml/update/ endpoint. 
    Args:
        
        userid (str): ID of the simulation to execute.
        
        duration (str): Duration of the simulation. Can be ntl (no time limit) or inf (infinity). It can be also a digit like 300.
        
        filename (str): YAML file name corresponding to the model to simulate.
        
        tag (str): Meta data related to the app used by a user that requests the simulation.

    Returns:
        
        dict: simulation ID.
    """
    yaml_filename_path = os.path.join(users_path_dir if userid else yaml_path_dir, userid+'_'+filename if userid else filename)
    sim = create_sim.delay(str(yaml_filename_path), str(duration), str(userid))

    return {"sim_id": sim.id}

############################################################################
### to use: /simulation/d2ad4871-5218-4c58-bd24-ec6201c5149b/status
@api_routes.get("/simulation/{sim_id}/status/")
async def get_simulation_status(sim_id:str):
    """
    Get the status of a simulation.

    Args:
        
        sim_id (str): ID of the simulation to retrieve.

    Returns:
        
        dict: Information about the simulation, including its ID, status, and result.
    """
    sim = AsyncResult(sim_id)
    
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found!")

    result = {
        "sim_id": sim_id,
        "sim_status": sim.status,
        "sim_result": sim.result
    }
    return result

############################################################################
@api_routes.get("/simulation/{sim_id}/cancel/")
async def cancel_simulation(sim_id:str):
    """
    Cancel the simulation.

    Args:
        
        sim_id (str): ID of the simulation to cancel.

    Returns:
        
        dict: Confirmation about the canceled simulation.
    """
    AsyncResult(sim_id).revoke(terminate=True)

    result = {
        "sim_id": sim_id,
        "canceled": True,
    }
    return result
