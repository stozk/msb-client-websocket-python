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

from msb_client.ComplexDataFormat import ComplexDataFormat
from msb_client.DataType import DataType
from msb_client.Event import Event
from msb_client.CustomMetaData import CustomMetaData
from msb_client.TypeDescription import TypeDescription
from msb_client.TypeDescriptor import TypeDescriptor
from msb_client.Function import Function
from msb_client.MsbClient import MsbClient

if __name__ == "__main__":
    """This is a sample client for the MSB python client library."""
    # define service properties as constructor parameters
    SERVICE_TYPE = "Application"
    SO_UUID = "a6f425ac-9e7b-4837-b7e8-5084fda42d30"
    SO_NAME = "Flow Test Service 1"
    SO_DESCRIPTION = "Flow Test Service 1"
    SO_TOKEN = "5084fda42d30"
    myMsbClient = MsbClient(
        SERVICE_TYPE,
        SO_UUID,
        SO_NAME,
        SO_DESCRIPTION,
        SO_TOKEN,
    )

    # msb_url = "wss://192.168.0.67:8084"
    msb_url = "wss://192.168.1.9:8084"

    myMsbClient.enableDebug(True)
    myMsbClient.enableTrace(False)
    myMsbClient.enableDataFormatValidation(True)
    myMsbClient.disableAutoReconnect(False)
    myMsbClient.setReconnectInterval(10000)
    myMsbClient.disableEventCache(False)
    myMsbClient.setEventCacheSize(1000)
    myMsbClient.disableHostnameVerification(True)

    # targetMessage = ComplexDataFormat("TargetMessage")
    # targetMessage.addProperty("targetUuid", DataType.STRING, False)
    # targetMessage.addProperty("dataObj", DataType.STRING, False)

    event1 = Event("INFO_MESSAGE", "Information Message", "Information", DataType.STRING, 1)

    response_event1 = Event("RESPONSE_INFO_MESSAGE", "Response Information Message", "Information", DataType.STRING, 1)

    myMsbClient.addEvent(event1)

    myMsbClient.addEvent(response_event1)

    # define the function which will be passed to the function description
    def printMsg(msg):
        print(str(msg["dataObj"]))


    function1 = Function(
        "PRINT_MSG",
        "Print Message",
        "Print Message",
        DataType.STRING,
        printMsg,
        False,
        ["RESPONSE_INFO_MESSAGE"],
    )

    myMsbClient.addFunction(function1)

    def set_interval(func, sec):
        def func_wrapper():
            set_interval(func, sec)
            func()

        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t

    def send_data():
        # msgObject = {}
        # msgObject["targetUuid"] = "691c9fb2-5a4b-43bc-a0a8-9e0cefb59933"
        # msgObject["dataObj"] = "Message from service 1"
        myMsbClient.publish("INFO_MESSAGE", "Message from service 1 to service 2", 1, False, None, "691c9fb2-5a4b-43bc-a0a8-9e0cefb59933")
        # myMsbClient.publish("INFO_MESSAGE", "Message from service 1 to service 3", 1, False, None, "9c8b8d10-a97f-459b-8e6b-e63330425614")

    print(myMsbClient.objectToJson(myMsbClient.getSelfDescription()))

    myMsbClient.connect(msb_url)
    myMsbClient.register()

    set_interval(send_data, 5)
