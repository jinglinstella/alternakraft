1. postgresql db:
- install docker
- run `docker-compose up -d`  in the docker-compose.yaml path.
- You can connect to the default postgres db using dbeaver and then create your own db 
or excute into the docker container, run psql and create the db via command line.
- Connection Info Should be:
  - PG_DB_NAME='whatever name you picked'
  - PG_DB_USER='postgres'
  - PG_DB_PWD=''
  - PG_DB_HOST='localhost'
- PG_DB_PORT='5432' 
2. If you want to use virtual enviroment, for example conda, create your environment:
 - `conda create -n cs6400 python=3.7.10`
 - `conda activate cs6400`

3. Install the dependencies:
- `pip install -r requirement.txt`
OR install the dependencies manually:
- `pip install flask`
- `pip install psycopg2`

4. run the boilerplate:
- `flask run`
