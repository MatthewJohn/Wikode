
## WARNING

Do not push to - this is a replica from upstream https://phabricator.dockstudios.co.uk/diffusion/WIKODE/


## Install

    virtualenv .
    source bin/activate
    pip install -r requirements.txt

## Run

    python ./run.py

Goto http://localhost:5000

For alternative ports, see [Configure]


## Configure

Create config.json in root directory, following options are available:

* LISTEN_HOST
* LISTEN_PORT
* SCM_TYPE
* DATA_DIR
* SQLITE_PATH

