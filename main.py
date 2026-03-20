import json
from flask import Flask, request, render_template, jsonify,  Response
import os
import time
from Utils.gnss_read import GNSSData 
from Utils.generate_path import Path_plan
from Utils.run import Run_process
import socket
#---------------------ENTER CONFIGURATION HERE----------------

#specify file paths
gnss_data="/home/rnil/Documents/path_plan/ntrip_dev-main/c/thread/test.json"    # file path for current location data 
save_path='data/path_points.json'   # file path to store path generated from path planning module

#Initialize variables
Application_width=2.2
Turning_radius=4.4
Tractor_Wheelbase=2.0

#--------------------------------------------------------------

data_read = GNSSData(gnss_data)

app = Flask(__name__)
gcp=[]
proc_ntrip=""
def event_stream():
    while True:
        time.sleep(0.5)
        try:
            data = data_read.last_data()
            if data:
                yield f"data: {json.dumps(data)}\n\n"
            else:
                yield "data: {}\n\n"
        except Exception as e:
            print(f"Error in stream: {e}")
            break

 

           
@app.route("/")
def root():
    return render_template("check.html")



@app.route("/check/<test>")
def check(test):

    if test == "steering":
        result = True

    elif test == "gnss":
        
        proc = Run_process("/home/rnil/Documents/path_plan/ntrip_dev-main/c/thread","obj/ntrv","123456")
        #proc.run_with_sudo()
        proc.runobject()
        
        result = True

    elif test == "ntrip":
        while True:
            data = data_read.last_data()
            if data["NTRIP"]>0 and data["Quality"]==4:
                result = True
                break

            else:
                result = False
    
    if result:
        return jsonify({"status":"ok"})
    else:
        return jsonify({"status":"fail"})

@app.route("/page1")
def page1():
    return render_template("page1.html")

@app.route("/home")
def home():
    return render_template("homepage.html")
   
@app.route('/foo', methods=['POST']) 
def foo():
    gcp.clear()
    dat = request.json 
    data=dat["farm"]["boundary"]
    outt=[]
    for n in range(0,len(dat)):
        outt=[[data[n-1][0],data[n-1][1]],[data[n][0],data[n][1]]]
        gcp.append(outt)

    return jsonify(data)

@app.route('/path', methods=['GET']) 
def path():
    infor={}
    
    out= Path_plan(gcp, save_path,  Application_width, Turning_radius,Tractor_Wheelbase)
    tp=out.path()
    infor["track"]=tp

    return jsonify(infor)

@app.route('/livelocation', methods=['GET'])
def livelocation():
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/stop', methods=['GET'])
def stop():
    res = {"response":"stopped"}
    return jsonify(res)

#-------------------ntrip client-----------------------------
@app.route("/ntripcl")
def ntripcl():
    return render_template("ntrip_client.html")

@app.route("/get_mountpoints", methods=["POST"])
def get_mountpoints():

    data = request.json
    host = data["host"]
    port = int(data["port"])

    mountpoints = []

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, port))

        request_str = "GET / HTTP/1.1\r\nUser-Agent: NTRIP PythonClient\r\n\r\n"
        s.send(request_str.encode())

        response = s.recv(4096).decode(errors="ignore")

        lines = response.split("\n")

        for line in lines:
            if line.startswith("STR"):
                parts = line.split(";")
                mountpoints.append(parts[1])

        s.close()
        print(mountpoints)
        return jsonify({"mountpoints": mountpoints})

    except Exception as e:
        return jsonify({"mountpoints": [], "error": str(e)})


@app.route("/connect_ntrip", methods=["POST"])
def connect_ntrip():

    data = request.json

    host = data["host"]
    port = data["port"]
    mount = data["mountpoint"]
    user = data["username"]
    pas = data["password"]

    print("Connecting to NTRIP:")
    
    global runner
    runner = Run_process(
    path="/home/rnil/Documents/path_plan/ntrip_dev-main/c/test_ntrip",
    proc_name="./test",
    password="",
    args=[host, str(port), mount, user, pas] 
    )
    #runner.test()
    
    proc_ntrip=runner.runobject()

    if proc_ntrip:
        return {"status":"connected"}
    else:
        return {"status":"failed"}


@app.route("/disconnect_ntrip")
def disconnect_ntrip():

    runner.stopobject()
    return {"status":"disconnected"}
    
#-----------tractor page----------------------

@app.route("/tractor")
def tractor():
    return render_template("tractor.html")

@app.route("/addtractor")
def addtractor():
    return render_template("add_tractor.html")
   
TRACTOR_FILE = "data/tractor.json"

@app.route("/get_tractors")
def get_tractors():

    if os.path.exists(TRACTOR_FILE):
        with open(TRACTOR_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    return jsonify(data)

@app.route("/save_tractor", methods=["POST"])
def save_tractor():

    new_data = request.json

    name = str(new_data.get("name", "")).strip()
    wheelbase = new_data.get("wheelbase")
    radius = new_data.get("radius")

    # -------- VALIDATION ----------
    if not name or wheelbase is None or radius is None:
        return jsonify({"status":"error", "message":"All fields are required"})

    try:
        wheelbase = float(wheelbase)
        radius = float(radius)
    except:
        return jsonify({"status":"error", "message":"Wheelbase and radius must be numbers"})

    if wheelbase <= 0 or radius <= 0:
        return jsonify({"status":"error", "message":"Values must be positive"})

    try:
        # Load existing data
        if os.path.exists(TRACTOR_FILE):
            with open(TRACTOR_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []

        # -------- CHECK DUPLICATE NAME ----------
        for tractor in data:
            if tractor["name"].lower() == name.lower():
                return jsonify({
                    "status":"error",
                    "message":"Tractor with same name already exists"
                })

        # Append new tractor
        data.append({
            "name": name,
            "wheelbase": wheelbase,
            "radius": radius
        })

        # Save file
        with open(TRACTOR_FILE, "w") as f:
            json.dump(data, f, indent=4)

        return jsonify({"status":"saved"})

    except Exception as e:
        print(e)
        return jsonify({"status":"error", "message":"Server error"})

@app.route("/delete_tractor", methods=["POST"])
def delete_tractor():

    name = request.json.get("name")

    try:
        if os.path.exists(TRACTOR_FILE):
            with open(TRACTOR_FILE, "r") as f:
                data = json.load(f)
        else:
            return jsonify({"status":"error"})

        # remove tractor
        data = [t for t in data if t["name"] != name]

        with open(TRACTOR_FILE, "w") as f:
            json.dump(data, f, indent=4)

        return jsonify({"status":"deleted"})

    except Exception as e:
        print(e)
        return jsonify({"status":"error"})
#------------------implement page------------------
@app.route("/implement")
def implement():
    return render_template("implement.html")

@app.route("/addimplement")
def implement_list():
    return render_template("add_implement.html")  

IMPLEMENT_FILE = "data/implement.json"

@app.route("/get_implements")
def get_implements():

    if os.path.exists(IMPLEMENT_FILE):
        with open(IMPLEMENT_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    return jsonify(data)
    
@app.route("/save_implement", methods=["POST"])
def save_implement():

    new_data = request.json

    type_ = str(new_data.get("type", "")).strip()
    name = str(new_data.get("name", "")).strip()
    width = new_data.get("width")

    # -------- VALIDATION ----------
    if not type_ or not name or width is None:
        return jsonify({"status":"error", "message":"All fields are required"})

    try:
        width = float(width)
    except:
        return jsonify({"status":"error", "message":"Width must be a number"})

    if width <= 0:
        return jsonify({"status":"error", "message":"Width must be positive"})

    try:
        # Load existing data
        if os.path.exists(IMPLEMENT_FILE):
            with open(IMPLEMENT_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []

        # -------- DUPLICATE CHECK ----------
        for imp in data:
            if imp["name"].lower() == name.lower():
                return jsonify({
                    "status":"error",
                    "message":"Implement with same name already exists"
                })

        # Save new implement
        data.append({
            "type": type_,
            "name": name,
            "width": width
        })

        with open(IMPLEMENT_FILE, "w") as f:
            json.dump(data, f, indent=4)

        return jsonify({"status":"saved"})

    except Exception as e:
        print(e)
        return jsonify({"status":"error", "message":"Server error"})    

@app.route("/delete_implement", methods=["POST"])
def delete_implement():

    name = request.json.get("name")

    try:
        if os.path.exists(IMPLEMENT_FILE):
            with open(IMPLEMENT_FILE, "r") as f:
                data = json.load(f)
        else:
            return jsonify({"status":"error"})

        # remove implement
        data = [i for i in data if i["name"] != name]

        with open(IMPLEMENT_FILE, "w") as f:
            json.dump(data, f, indent=4)

        return jsonify({"status":"deleted"})

    except Exception as e:
        print(e)
        return jsonify({"status":"error"})        


#-----------------------------farm--------------------------------------        
        
@app.route("/farm")
def farm():
    return render_template("farms.html")

@app.route("/addfarms")
def farms_list():
    return render_template("add_farm.html")  
    
FARM_FILE = "data/farms.json"

@app.route("/get_farms")
def get_farms():
    if os.path.exists(FARM_FILE):
        with open(FARM_FILE, "r") as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route("/curr_loc")
def get_loc():
    try:
        data = data_read.last_data()
        if data:
            print(data)
            return jsonify(json.dumps(data))
        else:
            return jsonify([])
    except Exception as e:
        print(f"Error in stream: {e}")


@app.route("/delete_farm", methods=["POST"])
def delete_farm():

    name = request.json.get("name")

    try:
        if os.path.exists(FARM_FILE):
            with open(FARM_FILE, "r") as f:
                data = json.load(f)
        else:
            return jsonify({"status":"error"})

        data = [f for f in data if f["name"] != name]

        with open(FARM_FILE, "w") as f:
            json.dump(data, f, indent=4)

        return jsonify({"status":"deleted"})

    except:
        return jsonify({"status":"error"})
    
@app.route("/save_farm", methods=["POST"])
def save_farm():

    new_farm = request.json

    try:
        if os.path.exists(FARM_FILE):
            with open(FARM_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []

        # prevent duplicate name
        for farm in data:
            if farm["name"] == new_farm["name"]:
                return jsonify({"status":"error","message":"Farm already exists"})

        data.append(new_farm)

        with open(FARM_FILE, "w") as f:
            json.dump(data, f, indent=4)

        return jsonify({"status":"saved"})

    except Exception as e:
        print(e)
        return jsonify({"status":"error"})

@app.route("/view_farm")
def view_farm():
    return render_template("view_farm.html")

#------------------------path--------------------------------
@app.route("/paths")
def path_page():
    return render_template("paths.html")
    
@app.route("/addpath")
def path_add():
    return render_template("add_path.html")

CONFIG_FILE = "data/configs.json"

@app.route("/save_config", methods=["POST"])
def save_config():

    new_data = request.json

    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []

        # prevent duplicate path names
        for d in data:
            if d["name"] == new_data["name"]:
                return jsonify({
                    "status":"error",
                    "message":"Path name already exists"
                })

        data.append(new_data)

        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)

        return jsonify({"status":"saved"})

    except Exception as e:
        print(e)
        return jsonify({"status":"error"})

@app.route("/get_configs")
def get_configs():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route("/delete_config", methods=["POST"])
def delete_config():

    name = request.json.get("name")

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
    else:
        return jsonify({"status":"error"})

    data = [d for d in data if d["name"] != name]

    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return jsonify({"status":"deleted"})

#----------------------start oeration and  stop---------------------
@app.route("/view_path")
def view_path():
    return render_template("view_path.html")

path_runner = Run_process(
    path="data/",            
    proc_name="./test_points_can",          
    password=None,             
    args=[]                    
)

@app.route("/startop", methods=['GET'])
def startop():
    if path_runner.process is None:
        result = path_runner.runobject()
        return jsonify({"response": "started", "proc": result})
    else:
        return jsonify({"response": "already running"})
        
@app.route("/stopop", methods=['GET'])
def stopop():
    if path_runner.process is not None:
        msg = path_runner.stopobject()
        path_runner.process = None   # ✅ reset
        return jsonify({"response": msg})
    else:
        return jsonify({"response": "not running"})
@app.route("/settings")
def settings():
    return "<h1>Settings Page</h1>"


if __name__ == '__main__':
    
    try:
        app.run(host="0.0.0.0", port=5000, threaded=True)
    except:
        pass
