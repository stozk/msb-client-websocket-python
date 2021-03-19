import json, uuid

f = open("jobList.json", "r")

uuidgen = str(uuid.uuid4())

for job in json.loads(f.read()):
    job["machineId"] = uuidgen
    print(job)
