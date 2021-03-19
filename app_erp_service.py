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
import copy
import flask
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

    msb_url = "wss://192.168.0.67:8084"
    somgmt_url = "http://192.168.0.67:8081"
    myclient = pymongo.MongoClient("mongodb://192.168.0.67:27017/")

    erp_db = myclient["erp_service"]
    col_orders = erp_db["orders"]
    col_customers = erp_db["customers"]
    col_products = erp_db["products"]
    col_personnel = erp_db["personnel"]
    col_scm = erp_db["scm"]

    app = flask.Flask(__name__)
    app.config["DEBUG"] = True

    #Kundendaten
    #Auftragsdaten
    #Produktdaten
    #SCM
    #Personaldaten

    @app.route("/", methods=["GET"])
    def home():
        homeinfo = {
            "application": "ERP Job Management Database Service",
            "version": "0.1"
        }
        return jsonify(homeinfo)

    @app.route("/orders", methods=["GET"])
    def getOrders():
        result = col_orders.find({}, {"_id": False})
        return jsonify([res for res in result])

    @app.route("/orders/find", methods=["GET"])
    def findOrder():
        # here we want to get the value of user (i.e. ?user=some-value)
        uuid_param = request.args.get("uuid")
        customer_param = request.args.get("customer")
        product_param = request.args.get("product")

        print(uuid_param)
        print(customer_param)
        print(product_param)

        if col_orders.count_documents({"uuid": str(uuid_param)}, limit=1):
            result = col_orders.find_one({"uuid": str(uuid_param)}, {"_id": False})
            return jsonify(result)
        else:
            return jsonify({})

    @app.route("/orders/<uuid>", methods=["GET"])
    def getOrderByUuid(uuid):
        if col_orders.count_documents({"uuid": uuid}, limit=1):
            result = col_orders.find_one({"uuid": uuid}, {"_id": False})
            # if results.count() != 0:
            return jsonify(result)
        else:
            return jsonify({})


    @app.route("/customers", methods=["GET"])
    def getCustomers():
        if col_orders.count_documents({"uuid": uuid}, limit=1):
            result = col_orders.find_one({"uuid": uuid}, {"_id": False})
            # if results.count() != 0:
            return jsonify(result)
        else:
            return jsonify({})

    @app.route("/customers/<uuid>", methods=["GET"])
    def getCustomerByUuid(uuid):
        if col_customers.count_documents({"uuid": uuid}, limit=1):
            result = col_customers.find_one({"uuid": uuid}, {"_id": False})
            # if results.count() != 0:
            return jsonify(result)
        else:
            return jsonify({})

    @app.route("/products", methods=["GET"])
    def getProducts():
        result = col_products.find({}, {"_id": False})
        return jsonify([res for res in result])








    """This is a sample client for the MSB python client library."""
    # define service properties as constructor parameters
    SERVICE_TYPE = "Application"
    SO_UUID = "4d239249-9473-4bd6-b980-cad1710e2d2e"
    SO_NAME = "ERP Job Management Service"
    SO_DESCRIPTION = "ERP Job Management Database Service"
    SO_TOKEN = "cad1710e2d2e"
    myMsbClient = MsbClient(
        SERVICE_TYPE,
        SO_UUID,
        SO_NAME,
        SO_DESCRIPTION,
        SO_TOKEN,
    )

    myMsbClient.enableDebug(True)
    myMsbClient.enableTrace(False)
    myMsbClient.enableDataFormatValidation(True)
    myMsbClient.disableAutoReconnect(False)
    myMsbClient.setReconnectInterval(10000)
    myMsbClient.disableEventCache(False)
    myMsbClient.setEventCacheSize(1000)
    myMsbClient.disableHostnameVerification(True)
    myMsbClient.enableThreadAsDaemon(False)

    print(myMsbClient.objectToJson(myMsbClient.getSelfDescription()))

    # myMsbClient.connect(msb_url)
    # myMsbClient.register()

    app.run(host="0.0.0.0", port=1339)


