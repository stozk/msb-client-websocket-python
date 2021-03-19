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

    mes_db = myclient["mes_service"]
    col_mde = mes_db["master_data"]

    app = flask.Flask(__name__)
    app.config["DEBUG"] = True

    #MDE
    #BDE
    #Tracking&Tracing
    #DNC&Einstelldaten
    #Materialmanagement
    #Prozessdaten
    #Feinplanung
    #Prozessdatenverarbeitung
    #Werkzeug- und Ressourcenmanagement
    #Energiemanagement

    #Personalmanagement
    #Qualitätsdaten

    # MDE:
    # Schalthäufigkeit, Unterbrechungen und Laufzeiten von Maschinen
    # gefertigte Stückzahlen
    # Meldungen und Störungen
    # Eingriffe des bedienenden Personals
    # Daten der Instandhaltung (Laufzeiten, Schaltspiel)
    # Verbrauch an Material, Energie und Hilfsmitteln
    # Messungen der Temperatur in Lagerräumen oder der Produktion, Immissionswerte

    @app.route("/", methods=["GET"])
    def home():
        homeinfo = {
            "application": "MES BDE Database Service",
            "version": "0.1"
        }
        return jsonify(homeinfo)


    @app.route("/mde/<uuid>", methods=["GET"])
    def getMDEByUuid(uuid):
        if col_mde.count_documents({"uuid": uuid}, limit=1):
            result = col_mde.find_one({"uuid": uuid}, {"_id": False})
            # if results.count() != 0:
            return jsonify(result)
        else:
            return jsonify({})








    """This is a sample client for the MSB python client library."""
    # define service properties as constructor parameters
    SERVICE_TYPE = "Application"
    SO_UUID = "a6f425ac-9e7b-4837-b7e8-5084fda42d30"
    SO_NAME = "MES BDE Service"
    SO_DESCRIPTION = "MES BDE Database Service"
    SO_TOKEN = "5084fda42d30"
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

    app.run(host="0.0.0.0", port=1338)


