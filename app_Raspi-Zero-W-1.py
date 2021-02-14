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
    SERVICE_TYPE = "SmartObject"
    SO_UUID = "ccb5586a-d0e9-4c9b-9781-383759833119"
    SO_NAME = "Raspberry Pi Zero W 1"
    SO_DESCRIPTION = "Raspberry PI 3 + Enviro+ sensor board"
    SO_TOKEN = "383759833119"
    myMsbClient = MsbClient(
        SERVICE_TYPE,
        SO_UUID,
        SO_NAME,
        SO_DESCRIPTION,
        SO_TOKEN,
    )

    msb_url = 'wss://localhost:8084'

    myMsbClient.enableDebug(True)
    myMsbClient.enableTrace(False)
    myMsbClient.enableDataFormatValidation(True)
    myMsbClient.disableAutoReconnect(False)
    myMsbClient.setReconnectInterval(10000)
    myMsbClient.disableEventCache(False)
    myMsbClient.setEventCacheSize(1000)
    myMsbClient.disableHostnameVerification(True)

    myMsbClient.addMetaData(CustomMetaData("SEN",
                                           "Sensor - device which, when excited by a physical phenomenon, produces an electric signal characterizing the physical phenomenon",
                                           TypeDescription(TypeDescriptor.CDD,
                                                           "0112/2///61360_4#AAA103#001",
                                                           "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/2a050a792eee78e1c12575560054b803/219d27329351ec25c1257dd300515f69")))

    myMsbClient.addMetaData(CustomMetaData("Fine Particle Sensor",
                                           "Sensor which measures fine particles",
                                           TypeDescription(TypeDescriptor.CUSTOM,
                                                           "0112/2///61360_4#AAA103#001-FEIN",
                                                           "")))

    myMsbClient.addMetaData(CustomMetaData("MUP",
                                           "CPU - processor whose elements have been miniaturized into an integrated circuit",
                                           TypeDescription(TypeDescriptor.CDD,
                                                           "0112/2///61360_4#AAA062#001",
                                                           "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/2a050a792eee78e1c12575560054b803/670dc436b7e157cac1257dd300515f41"),
                                           "/",
                                           "METHOD_STUB_TO_GET_DATA",
                                           DataType.STRING))

    myMsbClient.addMetaData(CustomMetaData("CPU_Architecture",
                                           "CPU_Architecture",
                                           TypeDescription(TypeDescriptor.CUSTOM,
                                                           "0112/2///61360_4#AAA062#001",
                                                           ""),
                                           "/",
                                           "METHOD_STUB_TO_GET_DATA",
                                           DataType.STRING))

    myMsbClient.addMetaData(CustomMetaData("RAM",
                                           "memory that permits access to any of its address locations in any desired sequence",
                                           TypeDescription(TypeDescriptor.CDD,
                                                           "0112/2///61360_4#AAA062#001",
                                                           "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/2a050a792eee78e1c12575560054b803/670dc436b7e157cac1257dd300515f41"),
                                           "/",
                                           "METHOD_STUB_TO_GET_DATA",
                                           DataType.DOUBLE))

    myMsbClient.addMetaData(CustomMetaData("OS_platform",
                                           "Operating system platform",
                                           TypeDescription(TypeDescriptor.CUSTOM,
                                                           "OS_platform",
                                                           ""),
                                           "/",
                                           "METHOD_STUB_TO_GET_DATA",
                                           DataType.STRING))

    myMsbClient.addMetaData(CustomMetaData("OS_hostname",
                                           "OS_hostname",
                                           TypeDescription(TypeDescriptor.CUSTOM,
                                                           "OS_hostname",
                                                           ""),
                                           "/",
                                           "METHOD_STUB_TO_GET_DATA",
                                           DataType.STRING))

    myMsbClient.addMetaData(CustomMetaData("OS_platform_release",
                                           "OS_platform_release",
                                           TypeDescription(TypeDescriptor.CUSTOM,
                                                           "OS_platform_release",
                                                           ""),
                                           "/",
                                           "METHOD_STUB_TO_GET_DATA",
                                           DataType.STRING))

    myMsbClient.addMetaData(CustomMetaData("OS_platform_version",
                                           "OS_platform_version",
                                           TypeDescription(TypeDescriptor.CUSTOM,
                                                           "OS_platform_version",
                                                           ""),
                                           "/",
                                           "METHOD_STUB_TO_GET_DATA",
                                           DataType.STRING))

    myMsbClient.addMetaData(CustomMetaData("OS_system_serial",
                                           "OS_system_serial",
                                           TypeDescription(TypeDescriptor.CUSTOM,
                                                           "OS_system_serial",
                                                           ""),
                                           "/",
                                           "METHOD_STUB_TO_GET_DATA",
                                           DataType.STRING))

    myMsbClient.addMetaData(CustomMetaData("CPU_CORES",
                                           "CPU core count",
                                           TypeDescription(TypeDescriptor.CUSTOM,
                                                           "CPU_CORES",
                                                           ""),
                                           "/",
                                           "METHOD_STUB_TO_GET_DATA",
                                           DataType.INT32))


    e_particle_concentration = Event("PARTICLE_CONCENTRATION", "Aktuelle Partikelkonzentration", "Aktuelle Konzentration der Feinstaubpartikel in PPM", DataType.INT32, 1, False)
    e_particle_concentration.addMetaData(CustomMetaData("Particle Concentration",
                                                        "Particle Concentration",
                                                        TypeDescription(TypeDescriptor.CDD,
                                                                        "0112/2///61987#ABT514#001",
                                                                        "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514"),
                                                        "/PARTICLE_CONCENTRATION"))
    e_particle_concentration.addMetaData(TypeDescription(TypeDescriptor.CDD,
                                                         "0112/2///61987#ABT514#001",
                                                         "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514",
                                                         "/PARTICLE_CONCENTRATION"))
    myMsbClient.addEvent(e_particle_concentration)




    e_temperature = Event("AMBIENT_TEMPERATURE", "Current ambient temperature", "Current temperature reading in °C", DataType.DOUBLE, 1, False)
    e_temperature.addMetaData(CustomMetaData("Temperature",
                                             "Ambient temperature",
                                             TypeDescription(TypeDescriptor.CDD,
                                                             "0112/2///61987#ABT514#001",
                                                             "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514"),
                                             "/AMBIENT_TEMPERATURE",
                                             DataType.DOUBLE))

    e_temperature.addMetaData(TypeDescription(TypeDescriptor.CDD,
                                              "0112/2///62720#UAA033#001",
                                              "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/Units/0112-2---62720%23UAA033",
                                              "/AMBIENT_TEMPERATURE"))
    myMsbClient.addEvent(e_temperature)

    def sendParticleData():
        print("Method stub for data sending")

    def startReadFineParticle():
        print("Method stub for particle reading")


    f_start_fp_detection = Function("START_FP_DETECTION", "Start fine particle measurement", "Starts the Process of fine particle measurements", DataType.BOOLEAN, startReadFineParticle, False, ["PARTICLE_CONCENTRATION"])
    f_start_fp_detection.addMetaData(CustomMetaData("Funktion_Temperatur",
                                                    "Funktion_Umgebungstemperatur",
                                                    TypeDescription(TypeDescriptor.CDD,
                                                                    "0112/2///61987#ABT514#001",
                                                                    "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514"),
                                                    "/START_FP_DETECTION"))
    myMsbClient.addFunction(f_start_fp_detection)


    e_cpu_speed_reading = Event("CPU_SPEED_READINGS", "CPU speed readings", "CPU speed readings for fingerprinting", DataType.DOUBLE, 1, True)
    e_cpu_speed_reading.addMetaData(CustomMetaData("CPU speed readings",
                                                   "CPU speed readings",
                                                   TypeDescription(TypeDescriptor.FINGERPRINT,
                                                                   "FP_CPU_SPEED_READINGS",
                                                                   ""),
                                                   "/CPU_SPEED_READINGS",
                                                   DataType.DOUBLE))

    myMsbClient.addEvent(e_cpu_speed_reading)


    f_cpu_speed = Function("CPU_SPEED", "Start CPU speed measurement", "Starts CPU speed measurement for fingerprinting", DataType.BOOLEAN, startReadFineParticle, False, ["CPU_SPEED_READINGS"])
    f_cpu_speed.addMetaData(CustomMetaData("CPU_SPEED",
                                           "Measure CPU speed for fingerprinting",
                                           TypeDescription(TypeDescriptor.FINGERPRINT,
                                                           "FP_CPU_SPEED",
                                                           ""),
                                           "/CPU_SPEED"))
    myMsbClient.addFunction(f_cpu_speed)

    e_cpu_temp_reading = Event("CPU_TEMPERATURE_READINGS", "CPU temperature readings", "CPU temperature readings for fingerprinting", DataType.DOUBLE, 1, False)
    e_cpu_temp_reading.addMetaData(CustomMetaData("CPU temperature",
                                                  "CPU temperature readings for fingerprinting",
                                                  TypeDescription(TypeDescriptor.FINGERPRINT,
                                                                  "FP_CPU_TEMPERATURE_READINGS",
                                                                  ""),
                                                  "/CPU_TEMPERATURE_READINGS",
                                                  DataType.DOUBLE))

    myMsbClient.addEvent(e_cpu_temp_reading)


    f_cpu_temp = Function("CPU_TEMPERATURE", "Get CPU temperature measurement", "Get the CPU tempreature for fingerprinting", DataType.DOUBLE, startReadFineParticle, False, ["CPU_TEMPERATURE_READINGS"])
    f_cpu_temp.addMetaData(CustomMetaData("CPU_TEMPERATURE",
                                          "Measure CPU temperature for fingerprinting",
                                          TypeDescription(TypeDescriptor.FINGERPRINT,
                                                          "FP_CPU_TEMPERATURE",
                                                          ""),
                                          "/CPU_TEMPERATURE"))
    myMsbClient.addFunction(f_cpu_temp)


    f_storage_speeds = Function("STORAGE_W_SPEED", "Measure storage speed", "Measure the CPU Speed for fingerprinting", DataType.DOUBLE, startReadFineParticle, False, [])
    f_storage_speeds.addMetaData(CustomMetaData("STORAGE_W_SPEED",
                                                "Measure the CPU Speed for fingerprinting",
                                                TypeDescription(TypeDescriptor.FINGERPRINT,
                                                                "FP_STORAGE_W_SPEED",
                                                                ""),
                                                "/STORAGE_W_SPEED"))
    myMsbClient.addFunction(f_storage_speeds)


    print(myMsbClient.objectToJson(myMsbClient.getSelfDescription()))

    myMsbClient.connect(msb_url)
    myMsbClient.register()