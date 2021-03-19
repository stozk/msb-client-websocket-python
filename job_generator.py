import pandas as pd
import datetime, uuid, json

start = '2020-03-17T22:16:59.066Z'
dateList = pd.date_range(start, periods=3000, freq="2h20min14s")
# print(datetime.datetime.utcnow().isoformat()[:-3] + "Z")

jobList = []

for dt in dateList:
    job = {}
    job["id"] = str(uuid.uuid4())
    job["machineId"] = ""
    job["dateTime"] = str(dt)
    job["customerId"] = str(uuid.uuid4())
    job["value"] = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
    jobList.append(job)

print(jobList)

file = open("jobList.json", "w")
file.write(json.dumps(jobList))
file.close()
