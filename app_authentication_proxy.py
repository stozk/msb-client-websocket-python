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

# from msb_client.ComplexDataFormat import ComplexDataFormat
# from msb_client.DataType import DataType
# from msb_client.Event import Event
# from msb_client.CustomMetaData import CustomMetaData
# from msb_client.TypeDescription import TypeDescription
# from msb_client.TypeDescriptor import TypeDescriptor
# from msb_client.Function import Function
# from msb_client.MsbClient import MsbClient


if __name__ == "__main__":

    somgmt_url = "http://192.168.0.67:8081"
    # somgmt_url = "http://192.168.1.9:8081"

    myclient = pymongo.MongoClient("mongodb://192.168.0.67:27017/")
    # myclient = pymongo.MongoClient("mongodb://192.168.1.9:27017/")

    mydb = myclient["authentcation_proxy"]
    mycol = mydb["auth_services"]

    authdata = {
        "uuid": "67f6dcf1-f558-4642-ab8c-4b5b918c2ec4",
        "operationId": "OPERATION_4b5b918c2ec4",
        "property": "PROP_4b5b918c2ec4",
        "value": "VALUE_4b5b918c2ec4",
    }

    entity = {
        "uuid": "67f6dcf1-f558-4642-ab8c-4b5b918c2ec4",
        "trustlevel": "0",
    }

    def registerAuthService(authServicedata):
        print("register auth service")

    def deleteAuthService(authServicedata):
        print("delete auth service")

    def connectAuthService(authServicedata):
        print("connect auth service")

    def findAuthService(authServicedata):
        print("find auth service")

    # task = {"summary": "Take out trash", "description": "9876543"}
    # resp = requests.post("http://127.0.0.1:1337/register", json=task)
    # print(resp.status_code)
    # # if resp.status_code != 201:
    # #     raise ApiError("POST /tasks/ {}".format(resp.status_code))
    # print("Response: " + json.dumps((resp.json())))

    def getAuthServices():
        params = {"lifecycleState": "VERIFIED"}
        resp = requests.get(somgmt_url + "/service", params=params)
        # print(resp.status_code)
        # if resp.status_code != 201:
        #     raise ApiError("POST /tasks/ {}".format(resp.status_code))
        # print("Response: " + json.dumps((resp.json())))

        auth_list = []

        for serv in resp.json():
            meta_resp = requests.get(somgmt_url + "/meta/{0}".format(serv["uuid"]))
            for md in meta_resp.json():
                # if "name" in md and md["name"] == "verification_service":
                #     #         print("FOUND!")
                #     #         print(json.dumps(md))
                #     # print("##########")
                #     print(md)
                if (
                    "typeDescription" in md
                    and md["typeDescription"]["identifier"] == "verification_service"
                ):

                    auth_list.append(md)
                    # print(md)
        return auth_list
        # print("############################")
        # print(json.dumps((meta_resp.json())))

    # print(getAuthServices())

    resp_uuid = getAuthServices()

    def getService(uuid):
        resp = requests.get(somgmt_url + "/service/{0}".format(uuid))
        return resp.json()

    print(getService(resp_uuid[0]["serviceUuid"]))

    # app = flask.Flask(__name__)
    # app.config["DEBUG"] = True

    # @app.route("/", methods=["GET"])
    # def home():
    #     return "<h1>SDP Authentication Service Proxy</h1><p>v.0.1</p>"

    # @app.route("/drop", methods=["GET"])
    # def dropDb():
    #     myclient.drop_database("authentcation_service")
    #     # myclient.drop_database("sdp_authentication")
    #     return "<h1>DB drop</h1><p>authentcation_service dropped.</p>"

    # @app.route("/find", methods=["GET"])
    # def getByUuidQuery():
    #     # here we want to get the value of user (i.e. ?user=some-value)
    #     uuid = request.args.get("uuid")
    #     # print(uuid)
    #     # if results.count() != 0:
    #     if mycol.count_documents({"uuid": str(uuid)}) != 0:
    #         myquery = {"uuid": str(uuid)}
    #         results = mycol.find(myquery, {"_id": False})
    #         return jsonify(results[0])
    #     else:
    #         return jsonify({})

    # @app.route("/<uuid>", methods=["GET"])
    # def getByUuid(uuid):
    #     if mycol.count_documents({"uuid": uuid}) != 0:
    #         myquery = {"uuid": uuid}
    #         results = mycol.find(myquery, {"_id": False})
    #         # if results.count() != 0:
    #         return jsonify(results[0])
    #     else:
    #         return jsonify({})

    # @app.route("/all", methods=["GET"])
    # def getAll():
    #     if mycol.count_documents({}) != 0:
    #         results = mycol.find({}, {"_id": False})
    #         resArray = []
    #         for res in results:
    #             resArray.append(res)
    #         return jsonify(resArray)
    #     else:
    #         return jsonify([])

    # @app.route("/generate", methods=["GET"])
    # def generate():
    #     insertList = []
    #     insertListPrint = []
    #     for i in range(1, 10):
    #         UUID = str(uuid.uuid4())
    #         print(UUID)
    #         authdata = {
    #             "uuid": str(UUID),
    #             "operationId": "OPERATION_" + str(UUID[-12:]),
    #             "property": "PROP_" + str(UUID[-12:]),
    #             "value": "VALUE_" + str(UUID[-12:]),
    #         }
    #         # mycol.insert_one(authdata)
    #         # insertedArray.append(authdata)
    #         insertList.append(authdata)
    #         insertListPrint.append(authdata.copy())
    #     mycol.insert_many(insertList)
    #     return jsonify(insertListPrint)

    # @app.route("/register", methods=["POST"])
    # def register():
    #     print(str(request.json))
    #     return json.dumps({"success": True}), 200, {"ContentType": "application/json"}

    # """This is a sample client for the MSB python client library."""
    # # define service properties as constructor parameters
    # SERVICE_TYPE = "Application"
    # SO_UUID = "d16c5634-c860-4e53-9163-fb884cea92fc"
    # SO_NAME = "Influx DB Database"
    # SO_DESCRIPTION = "Raspberry PI 3 + Enviro+ sensor board"
    # SO_TOKEN = "fb884cea92fc"
    # myMsbClient = MsbClient(
    #     SERVICE_TYPE,
    #     SO_UUID,
    #     SO_NAME,
    #     SO_DESCRIPTION,
    #     SO_TOKEN,
    # )

    # msb_url = 'wss://localhost:8084'

    # myMsbClient.enableDebug(True)
    # myMsbClient.enableTrace(False)
    # myMsbClient.enableDataFormatValidation(True)
    # myMsbClient.disableAutoReconnect(False)
    # myMsbClient.setReconnectInterval(10000)
    # myMsbClient.disableEventCache(False)
    # myMsbClient.setEventCacheSize(1000)
    # myMsbClient.disableHostnameVerification(True)

    # myMsbClient.addMetaData(CustomMetaData("SEN",
    #                                        "Sensor - device which, when excited by a physical phenomenon, produces an electric signal characterizing the physical phenomenon",
    #                                        TypeDescription(TypeDescriptor.CDD,
    #                                                        "0112/2///61360_4#AAA103#001",
    #                                                        "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/2a050a792eee78e1c12575560054b803/219d27329351ec25c1257dd300515f69")))

    # myMsbClient.addMetaData(CustomMetaData("Fine Particle Sensor",
    #                                        "Sensor which measures fine particles",
    #                                        TypeDescription(TypeDescriptor.CUSTOM,
    #                                                        "0112/2///61360_4#AAA103#001-FEIN",
    #                                                        "")))

    # myMsbClient.addMetaData(CustomMetaData("MUP",
    #                                        "CPU - processor whose elements have been miniaturized into an integrated circuit",
    #                                        TypeDescription(TypeDescriptor.CDD,
    #                                                        "0112/2///61360_4#AAA062#001",
    #                                                        "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/2a050a792eee78e1c12575560054b803/670dc436b7e157cac1257dd300515f41"),
    #                                        "/",
    #                                        "METHOD_STUB_TO_GET_DATA",
    #                                        DataType.STRING))

    # myMsbClient.addMetaData(CustomMetaData("CPU_Architecture",
    #                                        "CPU_Architecture",
    #                                        TypeDescription(TypeDescriptor.CUSTOM,
    #                                                        "0112/2///61360_4#AAA062#001",
    #                                                        ""),
    #                                        "/",
    #                                        "METHOD_STUB_TO_GET_DATA",
    #                                        DataType.STRING))

    # myMsbClient.addMetaData(CustomMetaData("RAM",
    #                                        "memory that permits access to any of its address locations in any desired sequence",
    #                                        TypeDescription(TypeDescriptor.CDD,
    #                                                        "0112/2///61360_4#AAA062#001",
    #                                                        "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/2a050a792eee78e1c12575560054b803/670dc436b7e157cac1257dd300515f41"),
    #                                        "/",
    #                                        "METHOD_STUB_TO_GET_DATA",
    #                                        DataType.DOUBLE))

    # myMsbClient.addMetaData(CustomMetaData("OS_platform",
    #                                        "Operating system platform",
    #                                        TypeDescription(TypeDescriptor.CUSTOM,
    #                                                        "OS_platform",
    #                                                        ""),
    #                                        "/",
    #                                        "METHOD_STUB_TO_GET_DATA",
    #                                        DataType.STRING))

    # myMsbClient.addMetaData(CustomMetaData("OS_hostname",
    #                                        "OS_hostname",
    #                                        TypeDescription(TypeDescriptor.CUSTOM,
    #                                                        "OS_hostname",
    #                                                        ""),
    #                                        "/",
    #                                        "METHOD_STUB_TO_GET_DATA",
    #                                        DataType.STRING))

    # myMsbClient.addMetaData(CustomMetaData("OS_platform_release",
    #                                        "OS_platform_release",
    #                                        TypeDescription(TypeDescriptor.CUSTOM,
    #                                                        "OS_platform_release",
    #                                                        ""),
    #                                        "/",
    #                                        "METHOD_STUB_TO_GET_DATA",
    #                                        DataType.STRING))

    # myMsbClient.addMetaData(CustomMetaData("OS_platform_version",
    #                                        "OS_platform_version",
    #                                        TypeDescription(TypeDescriptor.CUSTOM,
    #                                                        "OS_platform_version",
    #                                                        ""),
    #                                        "/",
    #                                        "METHOD_STUB_TO_GET_DATA",
    #                                        DataType.STRING))

    # myMsbClient.addMetaData(CustomMetaData("OS_system_serial",
    #                                        "OS_system_serial",
    #                                        TypeDescription(TypeDescriptor.CUSTOM,
    #                                                        "OS_system_serial",
    #                                                        ""),
    #                                        "/",
    #                                        "METHOD_STUB_TO_GET_DATA",
    #                                        DataType.STRING))

    # myMsbClient.addMetaData(CustomMetaData("CPU_CORES",
    #                                        "CPU core count",
    #                                        TypeDescription(TypeDescriptor.CUSTOM,
    #                                                        "CPU_CORES",
    #                                                        ""),
    #                                        "/",
    #                                        "METHOD_STUB_TO_GET_DATA",
    #                                        DataType.INT32))

    # e_particle_concentration = Event("PARTICLE_CONCENTRATION", "Aktuelle Partikelkonzentration", "Aktuelle Konzentration der Feinstaubpartikel in PPM", DataType.INT32, 1, False)
    # e_particle_concentration.addMetaData(CustomMetaData("Particle Concentration",
    #                                                     "Particle Concentration",
    #                                                     TypeDescription(TypeDescriptor.CDD,
    #                                                                     "0112/2///61987#ABT514#001",
    #                                                                     "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514"),
    #                                                     "/PARTICLE_CONCENTRATION"))
    # e_particle_concentration.addMetaData(TypeDescription(TypeDescriptor.CDD,
    #                                                      "0112/2///61987#ABT514#001",
    #                                                      "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514",
    #                                                      "/PARTICLE_CONCENTRATION"))
    # myMsbClient.addEvent(e_particle_concentration)

    # e_temperature = Event("AMBIENT_TEMPERATURE", "Current ambient temperature", "Current temperature reading in °C", DataType.DOUBLE, 1, False)
    # e_temperature.addMetaData(CustomMetaData("Temperature",
    #                                          "Ambient temperature",
    #                                          TypeDescription(TypeDescriptor.CDD,
    #                                                          "0112/2///61987#ABT514#001",
    #                                                          "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514"),
    #                                          "/AMBIENT_TEMPERATURE",
    #                                          DataType.DOUBLE))

    # e_temperature.addMetaData(TypeDescription(TypeDescriptor.CDD,
    #                                           "0112/2///62720#UAA033#001",
    #                                           "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/Units/0112-2---62720%23UAA033",
    #                                           "/AMBIENT_TEMPERATURE"))
    # myMsbClient.addEvent(e_temperature)

    # def sendParticleData():
    #     print("Method stub for data sending")

    # def startReadFineParticle():
    #     print("Method stub for particle reading")

    # f_start_fp_detection = Function("START_FP_DETECTION", "Start fine particle measurement", "Starts the Process of fine particle measurements", DataType.BOOLEAN, startReadFineParticle, False, ["PARTICLE_CONCENTRATION"])
    # f_start_fp_detection.addMetaData(CustomMetaData("Funktion_Temperatur",
    #                                                 "Funktion_Umgebungstemperatur",
    #                                                 TypeDescription(TypeDescriptor.CDD,
    #                                                                 "0112/2///61987#ABT514#001",
    #                                                                 "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514"),
    #                                                 "/START_FP_DETECTION"))
    # myMsbClient.addFunction(f_start_fp_detection)

    # e_cpu_speed_reading = Event("CPU_SPEED_READINGS", "CPU speed readings", "CPU speed readings for fingerprinting", DataType.DOUBLE, 1, True)
    # e_cpu_speed_reading.addMetaData(CustomMetaData("CPU speed readings",
    #                                                "CPU speed readings",
    #                                                TypeDescription(TypeDescriptor.FINGERPRINT,
    #                                                                "FP_CPU_SPEED_READINGS",
    #                                                                ""),
    #                                                "/CPU_SPEED_READINGS",
    #                                                DataType.DOUBLE))

    # myMsbClient.addEvent(e_cpu_speed_reading)

    # f_cpu_speed = Function("CPU_SPEED", "Start CPU speed measurement", "Starts CPU speed measurement for fingerprinting", DataType.BOOLEAN, startReadFineParticle, False, ["CPU_SPEED_READINGS"])
    # f_cpu_speed.addMetaData(CustomMetaData("CPU_SPEED",
    #                                        "Measure CPU speed for fingerprinting",
    #                                        TypeDescription(TypeDescriptor.FINGERPRINT,
    #                                                        "FP_CPU_SPEED",
    #                                                        ""),
    #                                        "/CPU_SPEED"))
    # myMsbClient.addFunction(f_cpu_speed)

    # e_cpu_temp_reading = Event("CPU_TEMPERATURE_READINGS", "CPU temperature readings", "CPU temperature readings for fingerprinting", DataType.DOUBLE, 1, False)
    # e_cpu_temp_reading.addMetaData(CustomMetaData("CPU temperature",
    #                                               "CPU temperature readings for fingerprinting",
    #                                               TypeDescription(TypeDescriptor.FINGERPRINT,
    #                                                               "FP_CPU_TEMPERATURE_READINGS",
    #                                                               ""),
    #                                               "/CPU_TEMPERATURE_READINGS",
    #                                               DataType.DOUBLE))

    # myMsbClient.addEvent(e_cpu_temp_reading)

    # f_cpu_temp = Function("CPU_TEMPERATURE", "Get CPU temperature measurement", "Get the CPU tempreature for fingerprinting", DataType.DOUBLE, startReadFineParticle, False, ["CPU_TEMPERATURE_READINGS"])
    # f_cpu_temp.addMetaData(CustomMetaData("CPU_TEMPERATURE",
    #                                       "Measure CPU temperature for fingerprinting",
    #                                       TypeDescription(TypeDescriptor.FINGERPRINT,
    #                                                       "FP_CPU_TEMPERATURE",
    #                                                       ""),
    #                                       "/CPU_TEMPERATURE"))
    # myMsbClient.addFunction(f_cpu_temp)

    # f_storage_speeds = Function("STORAGE_W_SPEED", "Measure storage speed", "Measure the CPU Speed for fingerprinting", DataType.DOUBLE, startReadFineParticle, False, [])
    # f_storage_speeds.addMetaData(CustomMetaData("STORAGE_W_SPEED",
    #                                             "Measure the CPU Speed for fingerprinting",
    #                                             TypeDescription(TypeDescriptor.FINGERPRINT,
    #                                                             "FP_STORAGE_W_SPEED",
    #                                                             ""),
    #                                             "/STORAGE_W_SPEED"))
    # myMsbClient.addFunction(f_storage_speeds)

    # def storeData(data):
    #     print("Storing data")

    # f_store_data = Function("STORE_DATA", "Store Data", "Stores Data to the Database", DataType.STRING, storeData, False, [])

    # print(myMsbClient.objectToJson(myMsbClient.getSelfDescription()))

    # myMsbClient.connect(msb_url)
    # myMsbClient.register()

    # app.run(host="0.0.0.0", port=1338)