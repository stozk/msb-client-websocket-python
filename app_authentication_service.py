# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
Authors: Daniel Stock, Matthias Stoehr

Licensed under the Apache License, Version 2.0
See the file "LICENSE" for the full license governing this code.
"""
import datetime
import threading
import uuid
import pymongo
import json
import flask
import requests
import threading
from flask import request
from flask import jsonify

from msb_client.ComplexDataFormat import ComplexDataFormat
from msb_client.DataType import DataType
from msb_client.Event import Event
from msb_client.CustomMetaData import CustomMetaData
from msb_client.TypeDescription import TypeDescription
from msb_client.TypeDescriptor import TypeDescriptor
from msb_client.Function import Function
from msb_client.MsbClient import MsbClient


if __name__ == "__main__":

    myclient = pymongo.MongoClient("mongodb://192.168.0.67:27017/")
    # myclient = pymongo.MongoClient("mongodb://192.168.1.9:27017/")

    somgmt_url = "http://192.168.0.67:8081"

    mydb = myclient["authentcation_service"]
    col_cpps = mydb["entity_cpps"]

    # authdata = {
    #     "uuid": "67f6dcf1-f558-4642-ab8c-4b5b918c2ec4",
    #     "operationId": "OPERATION_4b5b918c2ec4",
    #     "property": "PROP_4b5b918c2ec4",
    #     "value": "VALUE_4b5b918c2ec4",
    # }

    def syncServices2():
        params = {"lifecycleState": "VERIFIED"}
        resp = requests.get(somgmt_url + "/service", params=params)
        new_service_count = 0
        for serv in resp.json():

            entity_cpps = {
                "uuid": serv["uuid"],
                "name": serv["name"],
                "class": serv["@class"],
                "properties": [],
                "trustlevel": "0",
            }

            print(str(serv["uuid"]))
            meta_resp = requests.get(somgmt_url + "/meta/{0}".format(serv["uuid"]))
            for md in meta_resp.json():
                property = {
                    "serviceUuid": md["serviceUuid"],
                    "selector": md["selector"],
                    "weights": {
                        "origin": {
                            "natural": {"value": True, "weight": 0.8},
                            "artificial": {"value": False, "weight": 0.2},
                        },
                        "dynamicity": {
                            "static": {"value": True, "weight": 0.8},
                            "dynamic": {"value": False, "weight": 0.2},
                        },
                        "access": {
                            "open": {"value": True, "weight": 0.1},
                            "closed": {"value": False, "weight": 0.3},
                            "protected": {"value": False, "weight": 0.6},
                        },
                        "complexity": {
                            "simple": {"value": True, "weight": 0.4},
                            "complex": {"value": False, "weight": 0.6},
                        },
                        "context": {
                            "spatial": {"value": True, "weight": 0.2},
                            "temporal": {"value": False, "weight": 0.2},
                            "presence": {"value": False, "weight": 0.2},
                            "interaction": {"value": False, "weight": 0.2},
                            "event": {"value": False, "weight": 0.2},
                        },
                    },
                    "template_value": "",
                    "active": False,
                    "type": "initial",  # initial, active, continuous
                    "auth_state": "unverified",  # unverified, verified, verifying
                }

                if (
                    "typeDescription" in md
                    and md["typeDescription"]["typeDescriptor"] == "FINGERPRINT"
                ):
                    entity_cpps["properties"].append(property)

            if not col_cpps.count_documents({"uuid": serv["uuid"]}, limit=1):
                x = col_cpps.insert_one(entity_cpps)
                new_service_count = new_service_count + 1
        return new_service_count

    # myquery = {"uuid": authdata["uuid"]}
    # results = mycol.find(myquery)
    # if col_cpps.count_documents({"uuid": authdata["uuid"]}) == 0:
    #     x = col_cpps.insert_one(authdata)
    # if results.count() == 0:

    # dblist = myclient.list_database_names()
    # if "mydatabase" in dblist:
    #     print("The database exists.")
    # else:
    #     print("The database does not exist: " + str(dblist))

    # print(mydb.list_collection_names())

    # myquery = {"uuid": "67f6dcf1-f558-4642-ab8c-4b5b918c2ec4"}
    # mydoc = mycol.find(myquery)
    # print(mydoc)

    def initializeAuthentication(authData):
        print("initialize authentication")

    def findAuthserviceForProperty(authData):
        print("trying to find auth service for property")

    def authenticateProperty(authData):
        print("authenticating property")

    def startContinuousPropertyAuthentication(authData):
        print("authenticating property")

    def setTrustLevel(authData):
        print("trying to find auth service for property")

    app = flask.Flask(__name__)
    app.config["DEBUG"] = True

    @app.route("/", methods=["GET"])
    def home():
        return "<h1>Self-Description Property Authentication Service</h1><p>v.0.1</p>"

    @app.route("/sync", methods=["GET"])
    def syncServices():
        service_count = syncServices2()
        # myclient.drop_database("sdp_authentication")
        return "<h1>DB sync</h1><p>" + str(service_count) + " Services synched.</p>"

    @app.route("/drop", methods=["GET"])
    def dropDb():
        myclient.drop_database("authentcation_service")
        # myclient.drop_database("sdp_authentication")
        return "<h1>DB drop</h1><p>authentcation_service dropped.</p>"

    @app.route("/find", methods=["GET"])
    def getByUuidQuery():
        # here we want to get the value of user (i.e. ?user=some-value)
        uuid = request.args.get("uuid")
        # print(uuid)
        # if results.count() != 0:
        if col_cpps.count_documents({"uuid": str(uuid)}, limit=1):
            myquery = {"uuid": str(uuid)}
            results = col_cpps.find(myquery, {"_id": False})
            return jsonify(results[0])
        else:
            return jsonify({})

    @app.route("/<uuid>", methods=["GET"])
    def getByUuid(uuid):
        if col_cpps.count_documents({"uuid": uuid}, limit=1):
            myquery = {"uuid": uuid}
            results = col_cpps.find(myquery, {"_id": False})
            # if results.count() != 0:
            return jsonify(results[0])
        else:
            return jsonify({})

    @app.route("/<uuid>/<selector>", methods=["GET"])
    def getProperty(uuid, selector):
        if col_cpps.count_documents({"uuid": uuid}, limit=1):
            myquery = {"uuid": uuid}
            results = col_cpps.find(myquery, {"_id": False})
            for md in results[0]["properties"]:
                if md["selector"] == "/" + selector:
                    return jsonify(md)
        else:
            return jsonify({})

    @app.route("/<uuid>/<selector>/on", methods=["GET"])
    def enableAuthProperty(uuid, selector):
        if col_cpps.count_documents({"uuid": uuid}, limit=1):
            myquery = {"uuid": uuid}
            results = col_cpps.find(myquery, {"_id": False})
            for md in results[0]["properties"]:
                if md["selector"] == "/" + selector:
                    col_cpps.find_one_and_update(
                        {"uuid": uuid, "properties": md},
                        {"$set": {"properties.$.active": True}},
                    )
                    return jsonify(md)
            return jsonify(md)
        else:
            return jsonify({})

    @app.route("/<uuid>/<selector>/off", methods=["GET"])
    def disableAuthProperty(uuid, selector):
        if col_cpps.count_documents({"uuid": uuid}, limit=1):
            myquery = {"uuid": uuid}
            results = col_cpps.find(myquery, {"_id": False})
            for md in results[0]["properties"]:
                if md["selector"] == "/" + selector:
                    col_cpps.find_one_and_update(
                        {"uuid": uuid, "properties": md},
                        {"$set": {"properties.$.active": False}},
                    )
                    return jsonify(md)
            return jsonify(md)
        else:
            return jsonify({})

    @app.route("/all", methods=["GET"])
    def getAll():
        if col_cpps.count_documents({}):
            results = col_cpps.find({}, {"_id": False})
            resArray = []
            for res in results:
                resArray.append(res)
            return jsonify(resArray)
        else:
            return jsonify([])

    @app.route("/generate", methods=["GET"])
    def generate():
        insertList = []
        insertListPrint = []
        for i in range(1, 10):
            UUID = str(uuid.uuid4())
            print(UUID)
            authdata = {
                "uuid": str(UUID),
                "operationId": "OPERATION_" + str(UUID[-12:]),
                "property": "PROP_" + str(UUID[-12:]),
                "value": "VALUE_" + str(UUID[-12:]),
            }
            # mycol.insert_one(authdata)
            # insertedArray.append(authdata)
            insertList.append(authdata)
            insertListPrint.append(authdata.copy())
        col_cpps.insert_many(insertList)
        return jsonify(insertListPrint)

    @app.route("/register", methods=["POST"])
    def register():
        print(str(request.json))
        return json.dumps({"success": True}), 200, {"ContentType": "application/json"}

    # app.run(host="0.0.0.0", port=1337)

    """This is a sample client for the MSB python client library."""
    # define service properties as constructor parameters
    SERVICE_TYPE = "Application"
    SO_UUID = "af71d1ad-a2b9-4fd7-a450-ef8b7c72b107"
    SO_NAME = "Authentication Service"
    SO_DESCRIPTION = "CPPS Authentication Service"
    SO_TOKEN = "ef8b7c72b107"
    myMsbClient = MsbClient(
        SERVICE_TYPE,
        SO_UUID,
        SO_NAME,
        SO_DESCRIPTION,
        SO_TOKEN,
    )

    # msb_url = "wss://192.168.1.9:8084"
    msb_url = "wss://192.168.0.67:8084"

    myMsbClient.enableDebug(True)
    myMsbClient.enableTrace(False)
    myMsbClient.enableDataFormatValidation(True)
    myMsbClient.disableAutoReconnect(False)
    myMsbClient.setReconnectInterval(10000)
    myMsbClient.disableEventCache(False)
    myMsbClient.setEventCacheSize(1000)
    myMsbClient.disableHostnameVerification(True)
    myMsbClient.enableThreadAsDaemon(False)

    myMsbClient.addMetaData(
        CustomMetaData(
            "authentication_service",
            "A service which authenticates CPPS",
            TypeDescription(TypeDescriptor.CUSTOM, "authentication_service", ""),
        )
    )

    def f_func1():
        print("FUNCTION1")

    e_event1 = Event(
        "EVENT1",
        "EVENT1",
        "EVENT1",
        DataType.STRING,
        1,
        False,
    )

    f_function1 = Function(
        "FUNCTION1", "FUNCTION1", "FUNCTION1", DataType.STRING, f_func1, False
    )

    myMsbClient.addEvent(e_event1)

    myMsbClient.addFunction(f_function1)

    # myMsbClient.addMetaData(
    #     CustomMetaData(
    #         "SEN",
    #         "Sensor - device which, when excited by a physical phenomenon, produces an electric signal characterizing the physical phenomenon",
    #         TypeDescription(
    #             TypeDescriptor.CDD,
    #             "0112/2///61360_4#AAA103#001",
    #             "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/2a050a792eee78e1c12575560054b803/219d27329351ec25c1257dd300515f69",
    #         ),
    #     )
    # )

    # myMsbClient.addMetaData(
    #     CustomMetaData(
    #         "Fine Particle Sensor",
    #         "Sensor which measures fine particles",
    #         TypeDescription(
    #             TypeDescriptor.CUSTOM, "0112/2///61360_4#AAA103#001-FEIN", ""
    #         ),
    #     )
    # )

    # myMsbClient.addMetaData(
    #     CustomMetaData(
    #         "MUP",
    #         "CPU - processor whose elements have been miniaturized into an integrated circuit",
    #         TypeDescription(
    #             TypeDescriptor.CDD,
    #             "0112/2///61360_4#AAA062#001",
    #             "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/2a050a792eee78e1c12575560054b803/670dc436b7e157cac1257dd300515f41",
    #         ),
    #         "/",
    #         "METHOD_STUB_TO_GET_DATA",
    #         DataType.STRING,
    #     )
    # )

    # myMsbClient.addMetaData(
    #     CustomMetaData(
    #         "CPU_Architecture",
    #         "CPU_Architecture",
    #         TypeDescription(TypeDescriptor.CUSTOM, "0112/2///61360_4#AAA062#001", ""),
    #         "/",
    #         "METHOD_STUB_TO_GET_DATA",
    #         DataType.STRING,
    #     )
    # )

    # myMsbClient.addMetaData(
    #     CustomMetaData(
    #         "RAM",
    #         "memory that permits access to any of its address locations in any desired sequence",
    #         TypeDescription(
    #             TypeDescriptor.CDD,
    #             "0112/2///61360_4#AAA062#001",
    #             "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/2a050a792eee78e1c12575560054b803/670dc436b7e157cac1257dd300515f41",
    #         ),
    #         "/",
    #         "METHOD_STUB_TO_GET_DATA",
    #         DataType.DOUBLE,
    #     )
    # )

    # myMsbClient.addMetaData(
    #     CustomMetaData(
    #         "OS_platform",
    #         "Operating system platform",
    #         TypeDescription(TypeDescriptor.CUSTOM, "OS_platform", ""),
    #         "/",
    #         "METHOD_STUB_TO_GET_DATA",
    #         DataType.STRING,
    #     )
    # )

    # myMsbClient.addMetaData(
    #     CustomMetaData(
    #         "OS_hostname",
    #         "OS_hostname",
    #         TypeDescription(TypeDescriptor.CUSTOM, "OS_hostname", ""),
    #         "/",
    #         "METHOD_STUB_TO_GET_DATA",
    #         DataType.STRING,
    #     )
    # )

    # myMsbClient.addMetaData(
    #     CustomMetaData(
    #         "OS_platform_release",
    #         "OS_platform_release",
    #         TypeDescription(TypeDescriptor.CUSTOM, "OS_platform_release", ""),
    #         "/",
    #         "METHOD_STUB_TO_GET_DATA",
    #         DataType.STRING,
    #     )
    # )

    # myMsbClient.addMetaData(
    #     CustomMetaData(
    #         "OS_platform_version",
    #         "OS_platform_version",
    #         TypeDescription(TypeDescriptor.CUSTOM, "OS_platform_version", ""),
    #         "/",
    #         "METHOD_STUB_TO_GET_DATA",
    #         DataType.STRING,
    #     )
    # )

    # myMsbClient.addMetaData(
    #     CustomMetaData(
    #         "OS_system_serial",
    #         "OS_system_serial",
    #         TypeDescription(TypeDescriptor.CUSTOM, "OS_system_serial", ""),
    #         "/",
    #         "METHOD_STUB_TO_GET_DATA",
    #         DataType.STRING,
    #     )
    # )

    # myMsbClient.addMetaData(
    #     CustomMetaData(
    #         "CPU_CORES",
    #         "CPU core count",
    #         TypeDescription(TypeDescriptor.CUSTOM, "CPU_CORES", ""),
    #         "/",
    #         "METHOD_STUB_TO_GET_DATA",
    #         DataType.INT32,
    #     )
    # )

    # e_particle_concentration = Event(
    #     "PARTICLE_CONCENTRATION",
    #     "Aktuelle Partikelkonzentration",
    #     "Aktuelle Konzentration der Feinstaubpartikel in PPM",
    #     DataType.INT32,
    #     1,
    #     False,
    # )
    # e_particle_concentration.addMetaData(
    #     CustomMetaData(
    #         "Particle Concentration",
    #         "Particle Concentration",
    #         TypeDescription(
    #             TypeDescriptor.CDD,
    #             "0112/2///61987#ABT514#001",
    #             "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514",
    #         ),
    #         "/PARTICLE_CONCENTRATION",
    #     )
    # )
    # e_particle_concentration.addMetaData(
    #     TypeDescription(
    #         TypeDescriptor.CDD,
    #         "0112/2///61987#ABT514#001",
    #         "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514",
    #         "/PARTICLE_CONCENTRATION",
    #     )
    # )
    # myMsbClient.addEvent(e_particle_concentration)

    # e_temperature = Event(
    #     "AMBIENT_TEMPERATURE",
    #     "Current ambient temperature",
    #     "Current temperature reading in °C",
    #     DataType.DOUBLE,
    #     1,
    #     False,
    # )
    # e_temperature.addMetaData(
    #     CustomMetaData(
    #         "Temperature",
    #         "Ambient temperature",
    #         TypeDescription(
    #             TypeDescriptor.CDD,
    #             "0112/2///61987#ABT514#001",
    #             "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514",
    #         ),
    #         "/AMBIENT_TEMPERATURE",
    #         DataType.DOUBLE,
    #     )
    # )

    # e_temperature.addMetaData(
    #     TypeDescription(
    #         TypeDescriptor.CDD,
    #         "0112/2///62720#UAA033#001",
    #         "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/Units/0112-2---62720%23UAA033",
    #         "/AMBIENT_TEMPERATURE",
    #     )
    # )
    # myMsbClient.addEvent(e_temperature)

    # def sendParticleData():
    #     print("Method stub for data sending")

    # def startReadFineParticle():
    #     print("Method stub for particle reading")

    # f_start_fp_detection = Function(
    #     "START_FP_DETECTION",
    #     "Start fine particle measurement",
    #     "Starts the Process of fine particle measurements",
    #     DataType.BOOLEAN,
    #     startReadFineParticle,
    #     False,
    #     ["PARTICLE_CONCENTRATION"],
    # )
    # f_start_fp_detection.addMetaData(
    #     CustomMetaData(
    #         "Funktion_Temperatur",
    #         "Funktion_Umgebungstemperatur",
    #         TypeDescription(
    #             TypeDescriptor.CDD,
    #             "0112/2///61987#ABT514#001",
    #             "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514",
    #         ),
    #         "/START_FP_DETECTION",
    #     )
    # )
    # myMsbClient.addFunction(f_start_fp_detection)

    # e_cpu_speed_reading = Event(
    #     "CPU_SPEED_READINGS",
    #     "CPU speed readings",
    #     "CPU speed readings for fingerprinting",
    #     DataType.DOUBLE,
    #     1,
    #     True,
    # )
    # e_cpu_speed_reading.addMetaData(
    #     CustomMetaData(
    #         "CPU speed readings",
    #         "CPU speed readings",
    #         TypeDescription(TypeDescriptor.FINGERPRINT, "FP_CPU_SPEED_READINGS", ""),
    #         "/CPU_SPEED_READINGS",
    #         DataType.DOUBLE,
    #     )
    # )

    # myMsbClient.addEvent(e_cpu_speed_reading)

    # f_cpu_speed = Function(
    #     "CPU_SPEED",
    #     "Start CPU speed measurement",
    #     "Starts CPU speed measurement for fingerprinting",
    #     DataType.BOOLEAN,
    #     startReadFineParticle,
    #     False,
    #     ["CPU_SPEED_READINGS"],
    # )
    # f_cpu_speed.addMetaData(
    #     CustomMetaData(
    #         "CPU_SPEED",
    #         "Measure CPU speed for fingerprinting",
    #         TypeDescription(TypeDescriptor.FINGERPRINT, "FP_CPU_SPEED", ""),
    #         "/CPU_SPEED",
    #     )
    # )
    # myMsbClient.addFunction(f_cpu_speed)

    # e_cpu_temp_reading = Event(
    #     "CPU_TEMPERATURE_READINGS",
    #     "CPU temperature readings",
    #     "CPU temperature readings for fingerprinting",
    #     DataType.DOUBLE,
    #     1,
    #     False,
    # )
    # e_cpu_temp_reading.addMetaData(
    #     CustomMetaData(
    #         "CPU temperature",
    #         "CPU temperature readings for fingerprinting",
    #         TypeDescription(
    #             TypeDescriptor.FINGERPRINT, "FP_CPU_TEMPERATURE_READINGS", ""
    #         ),
    #         "/CPU_TEMPERATURE_READINGS",
    #         DataType.DOUBLE,
    #     )
    # )

    # myMsbClient.addEvent(e_cpu_temp_reading)

    # f_cpu_temp = Function(
    #     "CPU_TEMPERATURE",
    #     "Get CPU temperature measurement",
    #     "Get the CPU tempreature for fingerprinting",
    #     DataType.DOUBLE,
    #     startReadFineParticle,
    #     False,
    #     ["CPU_TEMPERATURE_READINGS"],
    # )
    # f_cpu_temp.addMetaData(
    #     CustomMetaData(
    #         "CPU_TEMPERATURE",
    #         "Measure CPU temperature for fingerprinting",
    #         TypeDescription(TypeDescriptor.FINGERPRINT, "FP_CPU_TEMPERATURE", ""),
    #         "/CPU_TEMPERATURE",
    #     )
    # )
    # myMsbClient.addFunction(f_cpu_temp)

    # f_storage_speeds = Function(
    #     "STORAGE_W_SPEED",
    #     "Measure storage speed",
    #     "Measure the CPU Speed for fingerprinting",
    #     DataType.DOUBLE,
    #     startReadFineParticle,
    #     False,
    #     [],
    # )
    # f_storage_speeds.addMetaData(
    #     CustomMetaData(
    #         "STORAGE_W_SPEED",
    #         "Measure the CPU Speed for fingerprinting",
    #         TypeDescription(TypeDescriptor.FINGERPRINT, "FP_STORAGE_W_SPEED", ""),
    #         "/STORAGE_W_SPEED",
    #     )
    # )
    # myMsbClient.addFunction(f_storage_speeds)

    print(myMsbClient.objectToJson(myMsbClient.getSelfDescription()))

    # myMsbClient.connect(msb_url)
    # myMsbClient.register()

    # def runMsbClient():
    #     myMsbClient.connect(msb_url)
    #     myMsbClient.register()

    # wst = threading.Thread(target=runMsbClient)
    # # wst.setDaemon(True)
    # wst.start()

    app.run(host="0.0.0.0", port=1337)
