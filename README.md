<!-- inspired from https://github.com/testdrivenio/fastapi-celery -->

# DEVSimPy Restfull API

This is a Restfull API service for the DEVSimPy Python simulator.  

## Want to use this project?

Spin up the containers:

```sh
$ docker-compose up -d --build
```

Open your browser to [http://localhost:8004/docs](http://localhost:8004/docs) to view the API Rest routes or to [http://localhost:5556](http://localhost:5556) to view the Flower dashboard.

Test the API:

```sh
$ docker-compose exec web python -m pytest
```

Trigger a new DEVS simulation:

```sh
$ curl http://localhost:8004/simulate?filename=<YAML File>&duration=<ntl or int value>
```

It returns the SIM_ID in a JSON format. 

Check the status of the DEVS simulation <SIM_ID>:

```sh
$ curl http://localhost:8004/simulation/status/<SIM_ID>
```

It returns a JSON flow with the status and the results of the DEVS simulation.