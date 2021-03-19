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
import platform, socket, re, uuid, json, psutil, netifaces, json, logging, os, sys, multiprocessing, subprocess, \
    hashlib, pkg_resources, time

from msb_client.ComplexDataFormat import ComplexDataFormat
from msb_client.DataType import DataType
from msb_client.Event import Event
from msb_client.CustomMetaData import CustomMetaData
from msb_client.TypeDescription import TypeDescription
from msb_client.TypeDescriptor import TypeDescriptor
from msb_client.Function import Function
from msb_client.MsbClient import MsbClient
from uptime import uptime
from time import perf_counter as time2

eventObj = {"uuid": "uuid",
         "eventId": "eventId",
         "dataObject": "dataObject",
         "priority": "priority",
         "postDate": "postDate",
         "correlationId": "correlationId"}

jobList = [{"id": "",
            "dateTime": "",
            "customer": ""}]

if __name__ == "__main__":
    """This is a sample client for the MSB python client library."""
    # define service properties as constructor parameters
    SERVICE_TYPE = "SmartObject"
    SO_UUID = "e24ded67-1ab9-4e01-a1b8-24f2666354a7"
    SO_NAME = "Banana Pi M3"
    SO_DESCRIPTION = "Raspberry PI 3 + Enviro+ sensor board"
    SO_TOKEN = "24f2666354a7"
    myMsbClient = MsbClient(
        SERVICE_TYPE,
        SO_UUID,
        SO_NAME,
        SO_DESCRIPTION,
        SO_TOKEN,
    )

    msb_url = "wss://192.168.1.9:8084"

    myMsbClient.enableDebug(True)
    myMsbClient.enableTrace(False)
    myMsbClient.enableDataFormatValidation(True)
    myMsbClient.disableAutoReconnect(False)
    myMsbClient.setReconnectInterval(10000)
    myMsbClient.disableEventCache(False)
    myMsbClient.setEventCacheSize(1000)
    myMsbClient.disableHostnameVerification(True)


    # Return RAM information (unit=kb) in a list
    # Index 0: total RAM
    # Index 1: used RAM
    # Index 2: free RAM
    def getRAMinfo():
        p = os.popen("free")
        i = 0
        while 1:
            i = i + 1
            line = p.readline()
            if i == 2:
                return line.split()[1:4]


    # Return % of CPU used by user as a character string
    def getCPUuse():
        return str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip())


    # Return information about disk space as a list (unit included)
    # Index 0: total disk space
    # Index 1: used disk space
    # Index 2: remaining disk space
    # Index 3: percentage of disk used
    def getDiskSpace():
        p = os.popen("df -h /")
        i = 0
        while 1:
            i = i + 1
            line = p.readline()
            if i == 2:
                return line.split()[1:5]


    def encrypt_string(hash_string):
        return hashlib.sha256(hash_string.encode()).hexdigest()


    def encodeJson(input_info):
        info_json = json.loads(input_info)
        for key in info_json:
            info_json[key] = encrypt_string(str(info_json[key]))
        return info_json


    def get_processor_name():
        if platform.system() == "Windows":
            return platform.processor()
        elif platform.system() == "Darwin":
            os.environ["PATH"] = os.environ["PATH"] + os.pathsep + "/usr/sbin"
            command = "sysctl -n machdep.cpu.brand_string"
            return subprocess.check_output(command).strip()
        elif platform.system() == "Linux":
            command = "cat /proc/cpuinfo"
            all_info = subprocess.check_output(command, shell=True).strip()
            for line in all_info.decode().split("\n"):
                if "model name" in line:
                    return re.sub(".*model name.*: ", "", line, 1)
        return ""


    def getMachine_addr():
        os_type = sys.platform.lower()
        if "win" in os_type:
            command = "wmic bios get serialnumber"
        elif "linux" in os_type:
            try:
                command = "hal-get-property --udi /org/freedesktop/Hal/devices/computer --key system.hardware.uuid"
            except:
                print("hal not available, probably Raspi system")
            return getRaspiSerial()
        elif "darwin" in os_type:
            command = "ioreg -l | grep IOPlatformSerialNumber"
        return os.popen(command).read().replace("\n", "").replace("	", "").replace(" ", "")


    def getRaspiSerial():
        # Extract serial from cpuinfo file
        cpuserial = "0000000000000000"
        try:
            f = open("/proc/cpuinfo", "r")
            for line in f:
                if line[0:6] == "Serial":
                    cpuserial = line[10:26]
            f.close()
        except:
            cpuserial = "ERROR000000000"
        return cpuserial

    def getCPUTemperature():
        try:
            if platform.system() == "Linux":
                try:
                    return psutil.sensors_temperatures()["cpu-thermal"][0][1]
                except:
                    return psutil.sensors_temperatures()
        except Exception as e:
            logging.exception(e)
            return 0

    def getNearByDevices():
        return []

    def getLocation():
        return {}

    def getSystemInfo():
        try:
            info = {}
            info["os"] = {}
            info["hw"] = {}
            ifacelist = {}
            info["os"]["platform"] = platform.system()
            info["os"]["platform-release"] = platform.release()
            info["os"]["platform-version"] = platform.version()
            try:
                info["os"]["hostname"] = socket.gethostname()
            except:
                print("Error: info['hostname']=socket.gethostname()")
            for iface in netifaces.interfaces():
                ifacelist[iface] = netifaces.ifaddresses(iface)
            info["network"] = ifacelist
            info["hw"]["architecture"] = platform.machine()
            info["hw"]["processor"] = get_processor_name()
            info["hw"]["cpu-cores"] = multiprocessing.cpu_count()
            info["hw"]["cpu-use"] = getCPUuse()
            info["hw"]["cpu-freq"] = psutil.cpu_freq(percpu=True)
            if platform.system() == "Linux":
                try:
                    info["hw"]["cpu-temp"] = psutil.sensors_temperatures()["cpu-thermal"][0][1]
                except:
                    info["hw"]["cpu-temp"] = psutil.sensors_temperatures()
            info["os"]["serial"] = getMachine_addr()
            RAM_stats = getRAMinfo()
            info["hw"]["ram"] = {}
            info["hw"]["ram"]["total"] = str(round(int(RAM_stats[0]) / 1000, 1))
            info["hw"]["ram"]["used"] = str(round(int(RAM_stats[1]) / 1000, 1))
            info["hw"]["ram"]["free"] = str(round(int(RAM_stats[2]) / 1000, 1))
            DISK_stats = getDiskSpace()
            info["hw"]["storage"] = {}
            info["hw"]["storage"]["total"] = str(DISK_stats[0])
            info["hw"]["storage"]["used"] = str(DISK_stats[1])
            info["hw"]["storage"]["free"] = str(DISK_stats[2])
            info["hw"]["storage"]["percentage"] = str(DISK_stats[3])
            info["hw"]["storage"]["partitions"] = psutil.disk_partitions()
            info["os"]["uptime"] = uptime()
            return json.dumps(info)
        except Exception as e:
            logging.exception(e)


    systemInfo = getSystemInfo()


    def runCPUBenchmark():
        laeufe = 10
        wiederholungen = 10
        # average = 0
        results = []
        for a in range(0, wiederholungen):
            start = time.time()
            for i in range(0, laeufe):
                for x in range(1, 1000):
                    3.141592 * 2 ** x
                for x in range(1, 10000):
                    float(x) / 3.141592
                for x in range(1, 10000):
                    float(3.141592) / x
            end = time.time()
            duration = (end - start)
            duration = round(duration, 3)
            results.append(duration)
            # average += duration
            # print(str(dauer))
        # print(ergebnisarray)
        # schnitt = round(schnitt / wiederholungen, 3)
        # print('Avarage: ' + str(schnitt))
        return results


    def getWriteBenchmark():
        def write_test(file, block_size, blocks_count):
            f = os.open(file, os.O_CREAT | os.O_WRONLY, 0o777)  # low-level I/O
            took = []
            for i in range(blocks_count):
                buff = os.urandom(block_size)  # get random bytes
                start = time()
                os.write(f, buff)
                os.fsync(f)  # force write to disk
                t = time() - start
                took.append(t)
            os.close(f)
            return took
        results = write_test("writetest", 100000, 1000)
        return results


    def getInstalledPackages():
        installed_packages = pkg_resources.working_set
        installed_packages_list = sorted(
            ["%s==%s" % (i.key, i.version) for i in installed_packages]
        )
        return installed_packages_list


    def getPythonVersion():
        return sys.version


    myMsbClient.addMetaData(
        CustomMetaData(
            "SEN",
            "Sensor - device which, when excited by a physical phenomenon, produces an electric signal characterizing the physical phenomenon",
            TypeDescription(
                TypeDescriptor.CDD,
                "0112/2///61360_4#AAA103#001",
                "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/2a050a792eee78e1c12575560054b803/219d27329351ec25c1257dd300515f69",
            ),
        )
    )

    myMsbClient.addMetaData(
        CustomMetaData(
            "Fine Particle Sensor",
            "Sensor which measures fine particles",
            TypeDescription(
                TypeDescriptor.CUSTOM, "0112/2///61360_4#AAA103#001-FEIN", ""
            ),
        )
    )

    myMsbClient.addMetaData(
        CustomMetaData(
            "MUP",
            "CPU - processor whose elements have been miniaturized into an integrated circuit",
            TypeDescription(
                TypeDescriptor.CDD,
                "0112/2///61360_4#AAA062#001",
                "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/2a050a792eee78e1c12575560054b803/670dc436b7e157cac1257dd300515f41",
            ),
            "/",
            "METHOD_STUB_TO_GET_DATA",
            DataType.STRING,
        )
    )

    myMsbClient.addMetaData(
        CustomMetaData(
            "CPU_Architecture",
            "CPU_Architecture",
            TypeDescription(TypeDescriptor.CUSTOM, "0112/2///61360_4#AAA062#001", ""),
            "/",
            "METHOD_STUB_TO_GET_DATA",
            DataType.STRING,
        )
    )

    myMsbClient.addMetaData(
        CustomMetaData(
            "RAM",
            "memory that permits access to any of its address locations in any desired sequence",
            TypeDescription(
                TypeDescriptor.CDD,
                "0112/2///61360_4#AAA062#001",
                "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/2a050a792eee78e1c12575560054b803/670dc436b7e157cac1257dd300515f41",
            ),
            "/",
            "METHOD_STUB_TO_GET_DATA",
            DataType.DOUBLE,
        )
    )

    myMsbClient.addMetaData(
        CustomMetaData(
            "OS_platform",
            "Operating system platform",
            TypeDescription(TypeDescriptor.CUSTOM, "OS_platform", ""),
            "/",
            "METHOD_STUB_TO_GET_DATA",
            DataType.STRING,
        )
    )

    myMsbClient.addMetaData(
        CustomMetaData(
            "OS_hostname",
            "OS_hostname",
            TypeDescription(TypeDescriptor.CUSTOM, "OS_hostname", ""),
            "/",
            "METHOD_STUB_TO_GET_DATA",
            DataType.STRING,
        )
    )

    myMsbClient.addMetaData(
        CustomMetaData(
            "OS_platform_release",
            "OS_platform_release",
            TypeDescription(TypeDescriptor.CUSTOM, "OS_platform_release", ""),
            "/",
            "METHOD_STUB_TO_GET_DATA",
            DataType.STRING,
        )
    )

    myMsbClient.addMetaData(
        CustomMetaData(
            "OS_platform_version",
            "OS_platform_version",
            TypeDescription(TypeDescriptor.CUSTOM, "OS_platform_version", ""),
            "/",
            "METHOD_STUB_TO_GET_DATA",
            DataType.STRING,
        )
    )

    myMsbClient.addMetaData(
        CustomMetaData(
            "OS_system_serial",
            "OS_system_serial",
            TypeDescription(TypeDescriptor.CUSTOM, "OS_system_serial", ""),
            "/",
            "METHOD_STUB_TO_GET_DATA",
            DataType.STRING,
        )
    )

    myMsbClient.addMetaData(
        CustomMetaData(
            "CPU_CORES",
            "CPU core count",
            TypeDescription(TypeDescriptor.CUSTOM, "CPU_CORES", ""),
            "/",
            "METHOD_STUB_TO_GET_DATA",
            DataType.INT32,
        )
    )

    e_particle_concentration = Event(
        "PARTICLE_CONCENTRATION",
        "Aktuelle Partikelkonzentration",
        "Aktuelle Konzentration der Feinstaubpartikel in PPM",
        DataType.INT32,
        1,
        False,
    )

    e_particle_concentration.addMetaData(
        CustomMetaData(
            "Particle Concentration",
            "Particle Concentration",
            TypeDescription(
                TypeDescriptor.CDD,
                "0112/2///61987#ABT514#001",
                "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514",
            ),
            "/PARTICLE_CONCENTRATION",
        )
    )

    e_particle_concentration.addMetaData(
        TypeDescription(
            TypeDescriptor.CDD,
            "0112/2///61987#ABT514#001",
            "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514",
            "/PARTICLE_CONCENTRATION",
        )
    )
    myMsbClient.addEvent(e_particle_concentration)

    e_temperature = Event(
        "AMBIENT_TEMPERATURE",
        "Current ambient temperature",
        "Current temperature reading in °C",
        DataType.DOUBLE,
        1,
        False,
    )
    e_temperature.addMetaData(
        CustomMetaData(
            "Temperature",
            "Ambient temperature",
            TypeDescription(
                TypeDescriptor.CDD,
                "0112/2///61987#ABT514#001",
                "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514",
            ),
            "/AMBIENT_TEMPERATURE",
            DataType.DOUBLE,
        )
    )

    e_temperature.addMetaData(
        TypeDescription(
            TypeDescriptor.CDD,
            "0112/2///62720#UAA033#001",
            "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/Units/0112-2---62720%23UAA033",
            "/AMBIENT_TEMPERATURE",
        )
    )
    myMsbClient.addEvent(e_temperature)


    def sendParticleData():
        print("Method stub for data sending")


    def startReadFineParticle():
        print("Method stub for particle reading")


    f_start_fp_detection = Function(
        "START_FP_DETECTION",
        "Start fine particle measurement",
        "Starts the Process of fine particle measurements",
        DataType.BOOLEAN,
        startReadFineParticle,
        False,
        ["PARTICLE_CONCENTRATION"],
    )
    f_start_fp_detection.addMetaData(
        CustomMetaData(
            "Funktion_Temperatur",
            "Funktion_Umgebungstemperatur",
            TypeDescription(
                TypeDescriptor.CDD,
                "0112/2///61987#ABT514#001",
                "https://cdd.iec.ch/cdd/iec61987/iec61987.nsf/ListsOfUnitsAllVersions/0112-2---61987%23ABT514",
            ),
            "/START_FP_DETECTION",
        )
    )
    myMsbClient.addFunction(f_start_fp_detection)

    e_cpu_speed_reading = Event(
        "CPU_SPEED_READINGS",
        "CPU speed readings",
        "CPU speed readings for fingerprinting",
        DataType.DOUBLE,
        1,
        True,
    )
    e_cpu_speed_reading.addMetaData(
        CustomMetaData(
            "CPU speed readings",
            "CPU speed readings",
            TypeDescription(TypeDescriptor.FINGERPRINT, "FP_CPU_SPEED_READINGS", ""),
            "/CPU_SPEED_READINGS",
            DataType.DOUBLE,
        )
    )

    myMsbClient.addEvent(e_cpu_speed_reading)

    f_cpu_speed = Function(
        "CPU_SPEED",
        "Start CPU speed measurement",
        "Starts CPU speed measurement for fingerprinting",
        DataType.BOOLEAN,
        startReadFineParticle,
        False,
        ["CPU_SPEED_READINGS"],
    )
    f_cpu_speed.addMetaData(
        CustomMetaData(
            "CPU_SPEED",
            "Measure CPU speed for fingerprinting",
            TypeDescription(TypeDescriptor.FINGERPRINT, "FP_CPU_SPEED", ""),
            "/CPU_SPEED",
        )
    )
    myMsbClient.addFunction(f_cpu_speed)

    e_cpu_temp_reading = Event(
        "CPU_TEMPERATURE_READINGS",
        "CPU temperature readings",
        "CPU temperature readings for fingerprinting",
        DataType.DOUBLE,
        1,
        False,
    )

    e_cpu_temp_reading2 = Event(
        "CPU_TEMPERATURE_READINGS_2",
        "CPU temperature readings",
        "CPU temperature readings for fingerprinting",
        DataType.DOUBLE,
        1,
        False,
    )

    e_cpu_temp_reading3 = Event(
        "CPU_TEMPERATURE_READINGS_2_3",
        "CPU temperature readings",
        "CPU temperature readings for fingerprinting",
        DataType.DOUBLE,
        1,
        False,
    )

    e_cpu_temp_reading.addMetaData(
        CustomMetaData(
            "CPU temperature",
            "CPU temperature readings for fingerprinting",
            TypeDescription(
                TypeDescriptor.FINGERPRINT, "FP_CPU_TEMPERATURE_READINGS", ""
            ),
            "/CPU_TEMPERATURE_READINGS",
            DataType.DOUBLE,
        )
    )

    e_cpu_temp_reading2.addMetaData(
        CustomMetaData(
            "CPU temperature",
            "CPU temperature readings for fingerprinting",
            TypeDescription(
                TypeDescriptor.FINGERPRINT, "FP_CPU_TEMPERATURE_READINGS", ""
            ),
            "/CPU_TEMPERATURE_READINGS/2",
            DataType.DOUBLE,
        )
    )

    e_cpu_temp_reading3.addMetaData(
        CustomMetaData(
            "CPU temperature",
            "CPU temperature readings for fingerprinting",
            TypeDescription(
                TypeDescriptor.FINGERPRINT, "FP_CPU_TEMPERATURE_READINGS", ""
            ),
            "/CPU_TEMPERATURE_READINGS/2/3",
            DataType.DOUBLE,
        )
    )

    myMsbClient.addEvent(e_cpu_temp_reading)
    myMsbClient.addEvent(e_cpu_temp_reading2)
    myMsbClient.addEvent(e_cpu_temp_reading3)

    f_cpu_temp = Function(
        "CPU_TEMPERATURE",
        "Get CPU temperature measurement",
        "Get the CPU temperature for fingerprinting",
        DataType.DOUBLE,
        startReadFineParticle,
        False,
        ["CPU_TEMPERATURE_READINGS"],
    )
    f_cpu_temp.addMetaData(
        CustomMetaData(
            "CPU_TEMPERATURE",
            "Measure CPU temperature for fingerprinting",
            TypeDescription(TypeDescriptor.FINGERPRINT, "FP_CPU_TEMPERATURE", ""),
            "/CPU_TEMPERATURE",
        )
    )
    myMsbClient.addFunction(f_cpu_temp)

    f_storage_speeds = Function(
        "STORAGE_W_SPEED",
        "Measure storage speed",
        "Measure the CPU Speed for fingerprinting",
        DataType.DOUBLE,
        startReadFineParticle,
        False,
        [],
    )
    f_storage_speeds.addMetaData(
        CustomMetaData(
            "STORAGE_W_SPEED",
            "Measure the CPU Speed for fingerprinting",
            TypeDescription(TypeDescriptor.FINGERPRINT, "FP_STORAGE_W_SPEED", ""),
            "/STORAGE_W_SPEED",
        )
    )
    myMsbClient.addFunction(f_storage_speeds)

    print(myMsbClient.objectToJson(myMsbClient.getSelfDescription()))

    myMsbClient.connect(msb_url)
    myMsbClient.register()
