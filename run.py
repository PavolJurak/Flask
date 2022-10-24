import sys
from mdblog.app import flask_app
from mdblog.app import init_db

def start():
    debug = True
    host = "0.0.0.0"
    flask_app.run(host, debug=debug)

def init():
    init_db(flask_app)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "start":
            start()
        elif command == "init":
            init()
    else:
        print("Pouzitie run.py [start | init]")

