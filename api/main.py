from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from api.endpoints import api_routes

### https://github.com/testdrivenio/fastapi-celery

### To set up the project, launch the docker desktop and execute in a cmd: docker-compose up -d --build

description = """

DEVSimPy-Rest API REST allows remote execution of DEVSimPy simulations. 🚀

Powered by FastAPI and Celery, this API enables the execution of YAML DEVSimPy models on the server-side and retrieval of results on the front-end. 

### How to use it

#### Yaml Routes

GET requests:

* **/yaml/all** to have all static/yaml files description 
* **/yaml/filenames** to have the filenamne of the static/yaml files
* **/yaml/<filename>.yaml** to have the description of filename.yaml
* **/yaml/labels/<filename>.yaml** gives the filename.yaml file content
* **/yaml/labels/**?filename=*filename.yaml*&model=*name* gives the name model inside the filename.yaml file

POST request:

* **/yaml/update/** udpate the content of the filename.yaml according to the following {"filename":"*filename.yaml*", "model":"*name*", "args":{*"arg":val*}}
* **/yaml/upload/** upload YAML file in the static/yaml directory

##### Simulation Routes

* **/simulation/start/**?filename=*filename.yaml*&duration=*d* to simulate the file name YAML file during d simulation step
* **/simulation/start/**?filename=*filename.yaml*&duration=*d*&userid=*john* to simulate the file name YAML file during d simulation step with an user id john
* **/simulation/status/d2ad4871-5218-4c58-bd24-ec6201c5149b** gives the status of the simulation d2ad4871-5218-4c58-bd24-ec6201c5149b (PENDING, SUCCESS, FAILED)
"""

def create_app():
    # Initialize FastAPI app
    app = FastAPI(
    title="DEVSimPy-Rest",
    description=description,
    summary="DEVSimPy-Rest API REST allows remote execution of DEVSimPy simulations.",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Capocchi L.",
        "url": "https://github.com/capocchi",
        "email": "lcapocchi@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },)

    app.mount("/static", StaticFiles(directory="api/static"), name="static")

    # Enable CORS via middleware
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_headers=['*'],
        allow_methods=['*'],
        allow_origins=['*'],
    )

    app.include_router(api_routes)

    return app

app = create_app()