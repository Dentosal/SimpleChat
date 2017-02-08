# Self-hosting
Self-hosting server is easy to try, but it isn't very good for production, since Flask in itself cannot handle requests simultaneously. Self-hosting setup wont server the application to non-localhost clients, unless you change line `SELFHOSTING_PUBLIC = False` in `app/config.py` to `SELFHOSTING_PUBLIC = False`.

## Dependencies
Install `nginx-server`. You'll need at least version 3.2. On macOS, you can use Homebrew to install it. Otherwise, compile it yourself:

```bash
wget http://download.redis.io/releases/redis-3.2.6.tar.gz
tar xzf redis-3.2.6.tar.gz
cd redis-3.2.6; make
cp src/redis-server .
```

And then take the `redis-server` from current directory and move it somewhere in your path, or in the SimpleChat project directory.

Then install other dependencies:

```bash
sudo apt-get install python3 -y # or just download Python3 from https://python.org
sudo python3 -m pip install flask redis
```

## Run
Start Redis with `redis-server redis.conf --daemonize yes`.
If you compiled redis yourself, remember to take the `redis-server` file from where the compile process left it, and use `./` in front of the file name.
Then just run `python3 app/app.py`, and the command should print out the address for the server.

# Hosted (nginx)
Currently hosted version works only with Linux. Configuration could easily be altered to work with macOS too, but it's not likely to work with Windows without significant configuration changes.

HTTPS certs are currently configured to user Let's Encrypt. This can be easily changed by modifying configuration.

## Dependencies
Linux (with apt-get):

```bash
sudo apt-get install build-essential python3 python3-dev python3-pip uwsgi uwsgi-plugin-python3 nginx-full python-setuptools -y
wget http://download.redis.io/releases/redis-3.2.6.tar.gz; tar xzf redis-3.2.6.tar.gz
cd redis-3.2.6
make
cp src/redis-server .
sudo python3 -m pip install flask redis
sudo python3 -m pip install uwsgi -I
```

## Configuration
Change path for ssl certificates on `nginx.conf`. Lines look like this:

```
ssl_certificate /etc/letsencrypt/live/d7.fi/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/d7.fi/privkey.pem;
```

## Setup
Linux:

```bash
# MUST USE ABSOLUTE PATH!
sudo ln -s /absolute/path/to/nginx.conf /etc/nginx/sites-enabled/simplechat
# test that ngingx config is ok
sudo nginx -t
# reload nginx conf
sudo nginx -s restart
```

## Run
Start Redis with `./redis-server redis.conf --daemonize yes`.
Remember to take the `redis-server` file from where the compile process left it.
Then run `uwsgi --ini uwsgi.ini`. Now tha server is running and available at https://localhost:8080/.
