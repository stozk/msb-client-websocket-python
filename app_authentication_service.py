# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
Authors: Daniel Stock, Matthias Stoehr

Licensed under the Apache License, Version 2.0
See the file "LICENSE" for the full license governing this code.
"""
import datetime
import threading
from typing import TYPE_CHECKING
import uuid
import pymongo
import json
import copy
import flask
from deepdiff import DeepDiff
from pymongo.collection import ReturnDocument
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

    owner_uuid = "7c328ad1-cea5-410e-8dd8-6c7ca5a2e4f5"

    hostIp ="192.168.0.67"
    #hostIp ="192.168.1.9"

    myclient = pymongo.MongoClient("mongodb://{ip}:27017/".format(ip = hostIp))

    somgmt_url = "http://{ip}:8081".format(ip = hostIp)
    ifdmgmt_url = "http://{ip}:8082".format(ip = hostIp)

    auth_db = myclient["authentcation_service"]
    col_cpps = auth_db["entity_cpps"]
    col_cpps_sd = auth_db["entity_cpps_sd"]
    col_vservices = auth_db["verification_services"]
    col_authjobs = auth_db["authjobs"]
    col_flows = auth_db["flows"]

    # authdata = {
    #     "uuid": "67f6dcf1-f558-4642-ab8c-4b5b918c2ec4",
    #     "operationId": "OPERATION_4b5b918c2ec4",
    #     "property": "PROP_4b5b918c2ec4",
    #     "value": "VALUE_4b5b918c2ec4",
    # }

    auth_message = {
        "serviceUuid": "",
        "authData": ""
    }

    complex_prop = {
        "serviceUuid": "",
        "props": []
    }



    def createFlow(ownerUuid, providerServiceUuid, eventId, consumerServiceUuid, functionId, targetUuid, responseEventId, responseEventConsumerServiceUuid, responseEventConsumerServiceFunctionId, flowName, deploy):
        params = {"targetUuid": targetUuid,
                  "responseEventId": responseEventId,
                  "responseEventConsumerServiceUuid": responseEventConsumerServiceUuid,
                  "responseEventConsumerServiceFunctionId": responseEventConsumerServiceFunctionId,
                  "deploy": deploy,
                  "flowName": flowName}
        resp = requests.get(
            ifdmgmt_url + "/integrationFlow/create/{ownerUuid}/{providerServiceUuid}/{eventId}/{consumerServiceUuid}/{functionId}".format(
                ownerUuid=ownerUuid, providerServiceUuid=providerServiceUuid, eventId=eventId, consumerServiceUuid=consumerServiceUuid, functionId=functionId),
            params=params)
        if resp.status_code == 201:
            return resp.json()
        else:
            return resp.status_code


    def createAuthFlow():
        createFlow()

    def createTrainFlow():
        createFlow()

    def createIdFlow(serviceUuid):
        return createFlow(owner_uuid, SO_UUID, "SELFDESCRIPTION_REQUEST", serviceUuid, "SEND_SELFDESCRIPTION", serviceUuid, "SELFDESCRIPTION_DATA", SO_UUID, "ID_SELFDESCRIPTION", "Identify " + serviceUuid + " by self-description", True)

    def createInitAuthFlow():
        createFlow()

    def isJson(jsonObj):
        try:
            jsonObject = json.loads(str(jsonObj))
            print("VALID JSON: " + jsonObj)
        except ValueError as e:
            print("NOT JSON: " + json.dumps(jsonObj))
            return False
        return True


    def identifyEntity(msg):
        n = int(msg["dataObject"], 2)
        selfd = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()
        allentities = col_cpps_sd.find()
        for entity in allentities:
            ddiff = DeepDiff(selfd, entity, ignore_order=True)
            if ddiff == {}:
                print(entity["name"])
                print(entity["uuid"])
            else:
                print(entity["uuid"])


    def deleteFlow(integrationFlowUuid):
        resp = requests.delete(ifdmgmt_url + "/integrationFlow/{integrationFlowUuid}".format(integrationFlowUuid=integrationFlowUuid))
        print(resp)

    def syncEntities():
        params = {"lifecycleState": "VERIFIED"}
        resp = requests.get(somgmt_url + "/service", params=params)
        new_service_count = 0
        for serv in resp.json():

            entity_cpps = {
                "uuid": serv["uuid"],
                "name": serv["name"],
                "class": serv["@class"],
                "auth_active": False,
                "properties": [],
                "trustlevel": "0",
            }

            if not col_flows.count_documents({"uuid": serv["uuid"]}, limit=1):
                entity_flows = {"serviceUuid": serv["uuid"],
                                "flows": []}
                col_flows.find_one_and_update({"serviceUuid": serv["uuid"]}, {"$set": entity_flows}, upsert=True)

            serv_resp = requests.get(somgmt_url + "/service/{0}".format(serv["uuid"]))
            xsd = col_cpps_sd.replace_one({"uuid": serv["uuid"]}, serv_resp.json(), upsert=True)

            print(str(serv["uuid"]))
            meta_resp = requests.get(somgmt_url + "/meta/{0}".format(serv["uuid"]))
            insertFlag = True
            for md in meta_resp.json():
                if insertFlag:
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
                        "template": {"value": "", "ed": 1}, #euklidische Distanz
                        "active": False,
                        "type": "initial"  # initial, active, continuous
                    }

                    if (
                            "typeDescription" in md
                            and md["typeDescription"]["typeDescriptor"] == "FINGERPRINT"
                    ):
                        entity_cpps["properties"].append(property)

                    if (
                            "typeDescription" in md
                            and md["typeDescription"]["identifier"]
                            == "verification_service"
                    ):
                        insertFlag = False

            if (
                    not col_cpps.count_documents({"uuid": serv["uuid"]}, limit=1)
                    and insertFlag
            ):
                x = col_cpps.insert_one(entity_cpps)
                new_service_count = new_service_count + 1
            insertFlag = True
        return new_service_count


    def registerVerificationService(serv):

        verification_service = {
            "uuid": serv["uuid"],
            "name": serv["name"],
            "class": serv["@class"],
            "properties": [],
        }

        meta_resp = requests.get(somgmt_url + "/meta/{0}".format(serv["uuid"]))
        insertFlag = False
        for md in meta_resp.json():
            property = {}

            if (
                    "typeDescription" in md
                    and md["typeDescription"]["identifier"] == "verification_service"
            ):
                verification_service["properties"].append(property)
            if (
                    "typeDescription" in md
                    and md["typeDescription"]["identifier"] == "verification_service"
            ):
                insertFlag = True

        if (
                not col_vservices.count_documents({"uuid": serv["uuid"]}, limit=1)
                and insertFlag
        ):
            x = col_vservices.insert_one(verification_service)

        return x.acknowledged


    def syncVerificationServices():
        params = {"lifecycleState": "VERIFIED"}
        resp = requests.get(somgmt_url + "/service", params=params)
        change_result = {"new": 0, "update": 0}
        for serv in resp.json():
            isVerificationService = False

            verification_service = {
                "uuid": serv["uuid"],
                "name": serv["name"],
                "class": serv["@class"],
                "properties": [],
            }

            meta_resp = requests.get(somgmt_url + "/meta/{0}".format(serv["uuid"]))
            for md in meta_resp.json():
                if (
                        "typeDescription" in md
                        and md["typeDescription"]["identifier"] == "verification_service"
                ):
                    isVerificationService = True
                if (
                        "typeDescription" in md
                        and md["typeDescription"]["identifier"] == "property_verification"
                ):
                    verification_service["properties"].append(md["typeDescription"]["value"])

            if not col_vservices.count_documents({"uuid": serv["uuid"]}, limit=1) and isVerificationService:
                x = col_vservices.insert_one(verification_service)
                change_result["new"] = change_result["new"] + 1
            elif isVerificationService:
                # print("UPDATING SERVICE " + serv["uuid"])
                # updated = False
                # vservice = col_vservices.find_one({"uuid": serv["uuid"]}, {"_id": False})
                # print("found: " + json.dumps(vservice))
                # new_props = copy.deepcopy(vservice["properties"])
                # for prop in vservice["properties"]:
                #     if prop not in verification_service["properties"]:
                #         new_props.append(prop)
                #         updated = True
                col_vservices.find_one_and_update(
                    {"uuid": serv["uuid"]},
                    {"$set": {"name": serv["name"], "properties": verification_service["properties"]}},
                )
                # if updated:
                change_result["update"] = change_result["update"] + 1
        print(str(change_result))
        return change_result


    def initializeAuthentication(authData):
        print("initialize authentication")


    def findAuthserviceForProperty(authData):
        print("trying to find auth service for property")


    def authenticateProperty(authData):
        print("authenticating property")


    def startContinuousPropertyAuthentication(authData):
        print("authenticating property")


    def setTrustLevel(entity):
        print("trying to find auth service for property")


    def checkEntitiesForAuth():
        activeAuthEntities = col_cpps.find({"auth_active": True}, {"_id": False})
        inactiveAuthEntities = col_cpps.find({"auth_active": False}, projection={"uuid": True, "_id": False})
        # print(col_cpps.count_documents({"auth_active": True}))
        synchedJobs = {"added": [], "updated": [], "removed": []}
        activeUUIDs = []
        inactiveUUIDs = []
        for entity in activeAuthEntities:
            print(entity["uuid"])
            authjob = {
                "uuid": entity["uuid"],
                "name": entity["name"],
                "initial": [],
                "active": [],
                "continuous": []
            }

            for prop in entity["properties"]:
                if prop["active"]:
                    verificationjob = {
                        "uuid": entity["uuid"],
                        "selector": prop["selector"],
                        "verification_state": "unverified",  # unverified, verified, verifying
                    }
                    authjob[prop["type"]].append(verificationjob)

            activeUUIDs.append(entity["uuid"])
            if not col_authjobs.count_documents({"uuid": entity["uuid"]}, limit=1):
                col_authjobs.insert_one(authjob)
                synchedJobs["added"].append(col_authjobs.find_one({"uuid": entity["uuid"]}, {"_id": False}))

        for entity in inactiveAuthEntities:
            inactiveUUIDs.append(entity["uuid"])

        currentAuthJobs = col_authjobs.find({}, projection={"uuid": True, "_id": False})
        currentAuthJobUUIDs = []
        for uuid in currentAuthJobs:
            currentAuthJobUUIDs.append(uuid["uuid"])
        UUIDsToRemove = [x for x in inactiveUUIDs if x in currentAuthJobUUIDs]

        for uuid in UUIDsToRemove:
            synchedJobs["removed"].append(copy.copy(col_authjobs.find_one({"uuid": uuid}, {"_id": False})))
            col_authjobs.delete_one({"uuid": uuid})

        for entity in col_cpps.find({"auth_active": True}, {"_id": False}):
            updated = False
            authjob = col_authjobs.find_one({"uuid": entity["uuid"]}, {"_id": False})

            for prop in entity["properties"]:
                if not any(job['selector'] == prop["selector"] for job in authjob[prop["type"]]) and prop["active"]:
                    verificationjob = {
                        "uuid": entity["uuid"],
                        "selector": prop["selector"],
                        "verification_state": "unverified",  # unverified, verified, verifying
                    }

                    authjob["initial"] = [job for job in authjob["initial"] if job['selector'] != prop["selector"]]
                    authjob["active"] = [job for job in authjob["active"] if job['selector'] != prop["selector"]]
                    authjob["continuous"] = [job for job in authjob["continuous"] if
                                             job['selector'] != prop["selector"]]
                    authjob[prop["type"]].append(verificationjob)
                    updated = True

                elif not prop["active"]:
                    if any(job['selector'] == prop["selector"] for job in authjob["initial"]):
                        authjob["initial"] = [job for job in authjob["initial"] if job['selector'] != prop["selector"]]
                        updated = True
                    elif any(job['selector'] == prop["selector"] for job in authjob["active"]):
                        authjob["active"] = [job for job in authjob["active"] if job['selector'] != prop["selector"]]
                        updated = True
                    elif any(job['selector'] == prop["selector"] for job in authjob["continuous"]):
                        authjob["continuous"] = [job for job in authjob["continuous"] if
                                                 job['selector'] != prop["selector"]]
                        updated = True

                # elif any(job['selector'] == prop["selector"] for job in authjob[prop["type"]]) and not prop["active"]:
                #     authjob[prop["type"]] = [job for job in authjob[prop["type"]] if job['selector'] != prop["selector"]]
                #     updated = True

            if updated:
                col_authjobs.update_one(
                    {"uuid": entity["uuid"]},
                    {"$set": {"initial": authjob["initial"], "active": authjob["active"],
                              "continuous": authjob["continuous"]}}
                )

            if updated:
                synchedJobs["updated"].append(
                    copy.copy(col_authjobs.find_one({"uuid": entity["uuid"]}, {"_id": False})))

        return synchedJobs


    app = flask.Flask(__name__)
    app.config["DEBUG"] = False


    @app.route("/authentication", methods=["GET"])
    def getJobs():
        if col_cpps.count_documents({}):
            results = col_authjobs.find({}, {"_id": False})
            resArray = []
            for res in results:
                resArray.append(res)
            return jsonify(resArray)
        else:
            return jsonify([])


    @app.route("/authentication/<uuid>", methods=["GET"])
    def getJobByUuid(uuid):
        if col_authjobs.count_documents({"uuid": uuid}, limit=1):
            myquery = {"uuid": uuid}
            result = col_authjobs.find_one(myquery, {"_id": False})
            # if results.count() != 0:
            return jsonify(result)
        else:
            return jsonify({})


    @app.route("/authentication/sync", methods=["GET"])
    def syncJobs():
        return jsonify(checkEntitiesForAuth())


    @app.route("/", methods=["GET"])
    def home():
        homeinfo = {
            "application": "Self-Description Property Authentication Service",
            "version": "0.1"
        }
        return jsonify(homeinfo)


    @app.route("/entities/sync", methods=["GET"])
    def syncServiceCall():
        service_count = syncEntities()
        # myclient.drop_database("sdp_authentication")
        return str(service_count)


    @app.route("/entities/drop", methods=["GET"])
    def dropDb():
        myclient.drop_database("authentcation_service")
        # myclient.drop_database("sdp_authentication")
        return "<h1>DB drop</h1><p>authentcation_service dropped.</p>"

    # @app.route("/entities/identify", methods=["GET"])
    # def startIdentification():
    #     # here we want to get the value of user (i.e. ?user=some-value)
    #     uuid = request.args.get("uuid")
    #     #sendevent
    #     #triggers identifyEntity()


    @app.route("/entities/find", methods=["GET"])
    def getByUuidQuery():
        # here we want to get the value of user (i.e. ?user=some-value)
        uuid = request.args.get("uuid")
        if col_cpps.count_documents({"uuid": str(uuid)}, limit=1):
            result = col_cpps.find_one({"uuid": str(uuid)}, {"_id": False})
            return jsonify(result)
        else:
            return jsonify({})

    @app.route("/entities/selfdescription", methods=["GET"])
    def getSelfdescriptions():
        if col_cpps_sd.count_documents({}):
            results = col_cpps_sd.find({}, {"_id": False})
            # resArray = []
            # for res in results:
            #     resArray.append(res)
            return jsonify([res for res in results])
        else:
            return jsonify([])

    @app.route("/entities/selfdescription/<uuid>", methods=["GET"])
    def getSelfdescriptionByUuid(uuid):
        if col_cpps_sd.count_documents({"uuid": uuid}, limit=1):
            myquery = {"uuid": uuid}
            result = col_cpps_sd.find_one(myquery, {"_id": False})
            # if results.count() != 0:
            return jsonify(result)
        else:
            return jsonify({})

    @app.route("/entities/<uuid>", methods=["GET"])
    def getByUuid(uuid):
        if col_cpps.count_documents({"uuid": uuid}, limit=1):
            myquery = {"uuid": uuid}
            result = col_cpps.find_one(myquery, {"_id": False})
            # if results.count() != 0:
            return jsonify(result)
        else:
            return jsonify({})


    @app.route("/entities/<uuid>/<path:selector>", methods=["GET", "POST"])
    def getProperty(uuid, selector):
        if request.method == "GET":
            if col_cpps.count_documents({"uuid": uuid}, limit=1):
                myquery = {"uuid": uuid}
                results = col_cpps.find(myquery, {"_id": False})
                for md in results[0]["properties"]:
                    if md["selector"] == "/" + selector:
                        return jsonify(md)
            else:
                return jsonify({})

        elif request.method == "POST":
            data = json.loads(request.data.decode("utf-8"))
            if col_cpps.count_documents({"uuid": uuid}, limit=1):
                myquery = {"uuid": uuid}
                results = col_cpps.find(myquery, {"_id": False})
                for md in results[0]["properties"]:
                    if md["selector"] == "/" + selector:
                        col_cpps.update_one(
                            {"uuid": uuid, "properties": md},
                            {"$set": {"properties.$": data}},
                        )
                        print(data)
                result = col_cpps.find_one({"uuid": uuid}, {"_id": False})
                return jsonify(result)
            else:
                return jsonify({})


    @app.route("/entities/<uuid>/on", methods=["GET"])
    def enableEntityAuth(uuid):
        if col_cpps.count_documents({"uuid": uuid}, limit=1):
            retdoc = col_cpps.find_one_and_update(
                {"uuid": uuid},
                {"$set": {"auth_active": True}},
                projection={"_id": False},
                return_document=ReturnDocument.AFTER,
            )
            return jsonify(retdoc)
        else:
            return jsonify({})


    @app.route("/entities/<uuid>/off", methods=["GET"])
    def disableEntityAuth(uuid):
        if col_cpps.count_documents({"uuid": uuid}, limit=1):
            retdoc = col_cpps.find_one_and_update(
                {"uuid": uuid},
                {"$set": {"auth_active": False}},
                projection={"_id": False},
                return_document=ReturnDocument.AFTER,
            )
            return jsonify(retdoc)
        else:
            return jsonify({})


    @app.route("/entities/<uuid>/<path:selector>/on", methods=["GET"])
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


    @app.route("/entities/<uuid>/<path:selector>/off", methods=["GET"])
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


    @app.route("/entities", methods=["GET"])
    def getEntities():
        if col_cpps.count_documents({}):
            results = col_cpps.find({}, {"_id": False})
            # resArray = []
            # for res in results:
            #     resArray.append(res)
            return jsonify([res for res in results])
        else:
            return jsonify([])


    @app.route("/entities/verification", methods=["GET"])
    def getVServices():
        if col_vservices.count_documents({}):
            results = col_vservices.find({}, {"_id": False})
            # resArray = []
            # for res in results:
            #     resArray.append(res)
            return jsonify([res for res in results])
        else:
            return jsonify([])


    @app.route("/entities/generate", methods=["GET"])
    def generate():
        insertList = []
        insertListPrint = []
        for i in range(1, 10):
            UUID = str(uuid.uuid4())
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


    @app.route("/entities/register", methods=["GET", "POST"])
    def register():
        if request.method == "GET":
            service_count = syncVerificationServices()
            return jsonify(service_count)

        if request.method == "POST":
            insert_result = registerVerificationService(request.json)
            return (
                json.dumps({"success": insert_result}),
                200,
                {"ContentType": "application/json"},
            )

    @app.route("/entities/identify/<uuid>", methods=["GET"])
    def identifyEntityRestCall(uuid):
        if col_cpps.count_documents({"uuid": uuid}, limit=1):
            requestSelfdescription(uuid)
            return jsonify({"identification_started": True})
        else:
            return jsonify({"identification_started": False})

    # entity_flows = {"serviceUuid": "",
    #                 "flows": []}
    # entity_flow = {"selector": "",
    #                "flowName": "",
    #                "flowUuid": ""}

    @app.route("/flows", methods=["GET"])
    def getFlows():
        if col_flows.count_documents({}):
            results = col_flows.find({}, {"_id": False})
            return jsonify([res for res in results])
        else:
            return jsonify([])

    @app.route("/flows/<uuid>", methods=["GET"])
    def getFlowByUuid(uuid):
        if col_flows.count_documents({"flowUuid": uuid}):
            results = col_flows.find({"flowUuid": uuid}, {"_id": False})
            return jsonify([res for res in results])
        else:
            return jsonify([0])

    @app.route("/flows/service/<uuid>", methods=["GET"])
    def getFlowsByService(uuid):
        if col_flows.count_documents({}):
            results = col_flows.find({"serviceUuid": uuid}, {"_id": False})
            return jsonify([res for res in results])
        else:
            return jsonify([])

    @app.route("/flows/service/<uuid>/createIdFlow", methods=["GET"])
    def createIdFlowRestCall(uuid):
        if col_flows.count_documents({"serviceUuid": uuid}):
            resp = createIdFlow(uuid)
            # print(resp)

            if not isinstance(resp, int):

                entity_flow = {"selector": "SEND_SELFDESCRIPTION",
                               "flowName": resp["name"],
                               "flowUuid": resp["uuid"]}

                # col_cpps.find_one_and_update(
                #     {"uuid": uuid, "properties": md},
                #     {"$set": {"properties.$.active": False}},
                # )
                print(uuid)
                # if col_flows.count_documents({"serviceUuid": uuid, "flows.selector": "SEND_SELFDESCRIPTION"}):

                service_flows_object = col_flows.find_one({"serviceUuid": uuid})

                flowlist = copy.deepcopy(service_flows_object["flows"])

                for i in range(len(flowlist)):
                    if flowlist[i]["selector"] == "SEND_SELFDESCRIPTION":
                        deleteFlow(flowlist[i]["flowUuid"])
                        del flowlist[i]
                flowlist.append(entity_flow)

                service_flows = col_flows.update_one({"serviceUuid": uuid}, {"$set": {"flows": flowlist}}, upsert=True)
                # service_flows = col_flows.find_one_and_update({"serviceUuid": uuid}, {"$set": {"flows": entity_flow}}, projection={"_id": False}, upsert=True, return_document=ReturnDocument.AFTER)
                # service_flows = col_flows.find_one({"serviceUuid": uuid}, projection={"_id": False})
                results = col_flows.find_one({"serviceUuid": uuid}, {"_id": False})
                return jsonify(results)
                # else:
                #     service_flows = col_flows.insert_one(entity_flow, projection={"_id": False})
                #     return service_flows
            else:
                # print(resp)
                return {}


    myMsbClient.addMetaData(
        CustomMetaData(
            "authentication_service",
            "A service which authenticates CPPS",
            TypeDescription(TypeDescriptor.CUSTOM, "authentication_service", ""),
        )
    )

    def requestSelfdescription(serviceUuid):
        myMsbClient.publish("SELFDESCRIPTION_REQUEST", "", 1, False, None, serviceUuid)

    e_selfdescriptionRequest = Event(
        "SELFDESCRIPTION_REQUEST",
        "Request for selfdescription",
        "Request for selfdescription",
        DataType.STRING,
        1,
        False,
    )
    myMsbClient.addEvent(e_selfdescriptionRequest)

    f_idSelfdescription = Function("ID_SELFDESCRIPTION", "Identify Entity by its selfdescription", "Identify Entity", DataType.STRING, identifyEntity, False)
    myMsbClient.addFunction(f_idSelfdescription)

    print(myMsbClient.objectToJson(myMsbClient.getSelfDescription()))


    myMsbClient.connect(msb_url)
    myMsbClient.register()

    # def runMsbClient():
    #     myMsbClient.connect(msb_url)
    #     myMsbClient.register()

    # wst = threading.Thread(target=runMsbClient)
    # # wst.setDaemon(True)
    # wst.start()

    def set_interval(func, sec):
        def func_wrapper():
            set_interval(func, sec)
            func()

        t = threading.Timer(sec, func_wrapper)
        t.start()
        # t.cancel()
        return t


    # set_interval(checkEntitiesForAuth, 5)

    app.run(host="0.0.0.0", port=1337)
