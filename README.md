# Developer Technical Assignment
Solution for the [assignment](https://github.com/lioncowlionant/developer-test)

## First clone the repository
```bash
git clone https://github.com/devashishlohani/tech_test
```

## Install using one of the ways
1. Using virtual environment virtualenv
   1. Install [python3](https://www.python.org/downloads/) and [virtualenv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)
   2. Create a virtual environment and activate it
        ```bash
        python3 -m venv tech_venv
        ```
        ```bash
        . tech_venv/bin/activate
        ```
   3. Install required packages
        ```bash
        pip install -r venv_requirements.txt
       ```
2. Using conda virtual environment
   1. Install [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)
   2. Create a virtual environment with required packages
        ```bash
        conda env create -f conda_environment.yml
        ```
   3. Activate the environment
        ```bash
        conda activate tech_test
        ```
3. Using docker
   1. Install [docker](https://www.docker.com/)
   2. Create the docker image
        ```bash
        sudo docker build -t dev_test_app .
        ```
   3. Verify the docker image
        ```bash
        sudo docker images
        ```   

## Running 
1. When installed using virtual environments
   1. Run web-app as
        ```bash
        flask run --host 0.0.0.0 --port 5000
        ```
      and then go to http://localhost:5000/
   2. Run test in CLI as
        ```bash
       python give_me_the_odds.py examples/example3/millennium-falcon.json examples/example3/empire.json
        ```

2. When installed using docker
   1. Run docker container as
        ```bash
        sudo docker run -it -p 5000:5000 -d --name dev_test_app dev_test_app:latest
        ```
      1. For web-app, go to http://localhost:5000/
      2. For CLI, first run
           ```bash
          sudo docker exec -it dev_test_app /bin/sh
           ```
         Then run test as
           ```bash
          python give_me_the_odds.py examples/example3/millennium-falcon.json examples/example3/empire.json
           ```
         