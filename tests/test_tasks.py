import json, time
from api.worker import *

#############################################################
# To test all tests: docker-compose exec web python -m pytest
#############################################################

# docker-compose exec web python -m pytest -k "test_home"
def test_home(test_app):
    response = test_app.get("/")
    assert response.status_code == 200

# docker-compose exec web python -m pytest -k "test_get_all_yaml"
def test_get_all_yaml(test_app):
    ### url to test
    url = "/yaml/all"
    response = test_app.get(url)
    content = response.json()
    assert response.status_code == 200 and content['success']

# docker-compose exec web python -m pytest -k "test_get_yaml_filenames"
def test_get_yaml_filenames(test_app):
    ### url to test
    url = "/yaml/filenames"
    response = test_app.get(url)
    content = response.json()
    assert response.status_code == 200 and content['success']

# docker-compose exec web python -m pytest -k "test_get_yaml_data"
def test_get_yaml_data(test_app):
    ### url to test with status code 200
    url = "/yaml/SimpleTrade.yaml"
    response = test_app.get(url)
    content = response.json()
    assert response.status_code == 200 and content['success']

    ### url to test for status code 422
    urls = ["/yaml/SimpleTrade.ya", "/yaml/Simple.yaml"]
    for url in urls:
        response = test_app.get(url)
        content = response.json()
        assert response.status_code == 422

# docker-compose exec web python -m pytest -k "test_get_yaml_model_data"
def test_get_yaml_model_data(test_app):
    ### url to test with status code 200
    urls = ["/yaml/models/?filename=test_SimpleTradeWithPredictions.yaml", "/yaml/models/?filename=SimpleTrade.yaml&model=Env"]
    for url in urls:
        response = test_app.get(url)
        content = response.json()
        assert response.status_code == 200 and content['success']

    ### url to test with status code 422
    urls = ["/yaml/models/?filename=test_SimpleTradeWithPredictions.y", "/yaml/models/?filename=Simple.yaml"]
    for url in urls:
        response = test_app.get(url)
        content = response.json()
        assert response.status_code == 422

    ### url to test with status code 200 but with a model E that doesnt exist
    urls = ["/yaml/models/?filename=SimpleTrade.yaml&model=E"]
    for url in urls:
        response = test_app.get(url)
        content = response.json()
        assert response.status_code == 200 and not content['success']

# docker-compose exec web python -m pytest -k "test_update_yaml"
def test_update_yaml(test_app):

    data = {'good_data':[
                ### all is good
                {   "userid":"test",
                    "filename":"SimpleTradeWithPredictions.yaml",
                    "model":"Env",
                    "args":{"cash":1000}
                },
                ### userid could be empty (search the file name in the yaml dir)
                {   "userid":"",
                    "filename":"SimpleTradeWithPredictions.yaml",
                    "model":"Env",
                    "args":{"cash":1000}
                },
                ### args could be empty
                {   "userid":"test",
                    "filename":"SimpleTradeWithPredictions.yaml",
                    "model":"Env",
                    "args":{}
                },
                ### bad args toto is not a good key but is not considered
                {   "userid":"test",
                    "filename":"SimpleTradeWithPredictions.yaml",
                    "model":"Env",
                    "args":{"toto":10, "cash":1000}
                }
            ],
            'bad_data': [
                ### bad extention of YAML file
                {   "userid":"test",
                    "filename":"SimpleTradeWithPredictions.ya",
                    "model":"Env",
                    "args":{"cash":1000}
                },
                ### bad YAML file name
                {   "userid":"",
                    "filename":"Simple.yaml",
                    "model":"Env",
                    "args":{"cash":1000}
                },
                ### bad model name
                {   "userid":"test",
                    "filename":"SimpleTradeWithPredictions.yaml",
                    "model":"E",
                    "args":{"cash":1000}
                }
            ]
            }
    
    for k,v in data.items():
        for param in v:
            response = test_app.post(
                "/yaml/update",
                data=json.dumps(param)
            )
        if k =='good_data':
            assert response.status_code == 200
        else:
            content = response.json()
            assert response.status_code == 200 and not content['success'] or response.status_code == 442
    

# docker-compose exec web python -m pytest -k "test_simulation"
def test_yaml_simulation(test_app):

    ### update the yaml file (create it if needed)
    response = test_app.post(
        "/yaml/update",
        data=json.dumps(
            {   "userid":"test",
                "filename":"SimpleTradeWithPredictions.yaml",
                "model":"Env",
                "args":{"cash":100000} ### if the cash is bigger, the simulation takes more time
            })
    )
    assert response.status_code == 200

    ### simulation the test_SimpleTradeWithPredictions.yaml file
    url =  "/simulation/start?userid=test&filename=SimpleTradeWithPredictions.yaml&duration=ntl&tag=MyApp"
    response = test_app.get(url)
    assert response.status_code == 200

    ### get the simulation id
    content = response.json()
    sim_id = content["sim_id"]
    assert sim_id

    ### check the status of the simulation 
    response = test_app.get(f"/simulation/{sim_id}/status/")
    assert response.status_code == 200
    content = response.json()
    assert content == {"sim_id": sim_id, "sim_status": "PENDING", "sim_result": None}

    ### cancel the simulation 
    response = test_app.get(f"/simulation/{sim_id}/cancel/")
    assert response.status_code == 200
    content = response.json()
    assert content == {"sim_id": sim_id, "canceled": True}

    ### check the status until the simulation is done
    # while content["sim_status"] == "PENDING":
    #     response = test_app.get(f"/simulation/{sim_id}/status/")
    #     content = response.json()
    # assert content['sim_id'] == sim_id and content['sim_status'] == "SUCCESS" and content["sim_result"] != None

    ### three simulation with different cash
    cashs = [100000, 200000, 300000]
    ids = []
    for cash in cashs:
        ### update the yaml file (create it if needed)
        response = test_app.post(
            "/yaml/update",
            data=json.dumps(
                {   "userid":"",
                    "filename":"SimpleTradeWithPredictions.yaml",
                    "model":"Env",
                    "args":{"cash":cash} ### if the cash is bigger, the simulation takes more time
                })
        )
        assert response.status_code == 200

        ### simulation the SimpleTradeWithPredictions.yaml file
        url =  "/simulation/start?filename=SimpleTradeWithPredictions.yaml&duration=ntl"
        response = test_app.get(url)
        assert response.status_code == 200
        
        ### simulation the SimpleTradeWithPredictions.yaml file
        url =  "/simulation/start?filename=SimpleTradeWithPredictions.yaml&duration=ntl"
        response = test_app.get(url)
        assert response.status_code == 200
        content = response.json()
        ids.append(content['sim_id'])
    
    ### cancel all simulation starting for the first created
    while ids:
         ### wait 10s
        time.sleep(60)

        sim_id = ids.pop(0)
        ### cancel the first simulation 
        response = test_app.get(f"/simulation/{sim_id}/cancel/")
        assert response.status_code == 200
        content = response.json()
        assert content == {"sim_id": sim_id, "canceled": True}
        
       