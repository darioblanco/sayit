sayit
=====

Task manager for your daily stand ups.

### Requirements
Python 2.6+

### Python dependencies
Create a new virtualenv and run the following commands:
`pip install -r requirements.txt` and `pip install -r test_requirements.txt` (development)

### Redis install
There is an install script in `install-redis.sh` (it needs sudo privileges for moving `redis-server` and `redis-cli` to `/usr/local/bin`) which will do all the work for you. This is enough for testing Redis in a developer environment.
Once installed, you can execute the server with `redis-server` (needed for running the tests and for playing with the server locally) and the client with `redis-cli`.

### Running the server
Just run `sayit` typing `python runserver.py`
For more options: `python runserver.py -h`

### License
>     http://www.apache.org/licenses/LICENSE-2.0
