import platform, socket, re, uuid, json, psutil, netifaces, json, logging, os, sys, multiprocessing, subprocess, hashlib
from uptime import uptime

hostname = "hostname_"
try:
    hostname = socket.gethostname() + "_"
except:
    print("Error: info['hostname']=socket.gethostname()")

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
        return getraspiserial()
    elif "darwin" in os_type:
        command = "ioreg -l | grep IOPlatformSerialNumber"
    return os.popen(command).read().replace("\n", "").replace("	", "").replace(" ", "")

def getraspiserial():
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


def getSystemInfo():
    try:
        info = {}
        info["os"] = {}
        info["hw"] = {}
        ifacelist = {}

        # if platform.system() == "Windows":
        #     try:
        #         print(x)
        #     w = wmi.WMI()
        #     info['cpu-temp']=w.Win32_TemperatureProbe()[0].CurrentReading
        #     w = wmi.WMI(namespace="c:\Apps\OpenHardwareMonitor")
        #     temperature_infos = w.Sensor()
        #     for sensor in temperature_infos:
        #         if sensor.SensorType==u'Temperature':
        #             # info['cpu-temp']=sensor.Valuep
        #             print(sensor.Name)
        #             print(sensor.Value)
        #     except:
        #         print("Failed reading temperature!")
        info["os"]["platform"] = platform.system()
        info["os"]["platform-release"] = platform.release()
        info["os"]["platform-version"] = platform.version()

        try:
            info["os"]["hostname"] = socket.gethostname()
        except:
            print("Error: info['hostname']=socket.gethostname()")
        # info['ip-address']=socket.gethostbyname(socket.gethostname())
        # info['ip-address']=socket.getaddrinfo(socket.gethostname(), 80)
        # try:
        #     info['hw']['mac-address']=':'.join(re.findall('..', '%012x' % uuid.getnode()))
        # except:
        #     print("Error: info['mac-address']=':'.join(re.findall('..', '%012x' % uuid.getnode()))")
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
                info["hw"]["cpu-temp"] = psutil.sensors_temperatures()["cpu-thermal"][
                    0
                ][1]
            except:
                info["hw"]["cpu-temp"] = psutil.sensors_temperatures()
        info["os"]["serial"] = getMachine_addr()
        # try:
        #     info['ram']=str(round(psutil.virtual_memory().total / (1024 **3)))+" GB"
        # except:
        #     print("Error: info['ram']=str(round(psutil.virtual_memory().total / (1024 **3)))")
        # info['ram']=str(psutil.virtual_memory().total / (1024 **3))
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


# # Output is in kb, here I convert it in Mb for readability
# RAM_stats = getRAMinfo()
# print("RAM_total " + str(round(int(RAM_stats[0]) / 1000,1)))
# print("RAM_used " + str(round(int(RAM_stats[1]) / 1000,1)))
# print("RAM_free " + str(round(int(RAM_stats[2]) / 1000,1)))

# # Disk information
# DISK_stats = getDiskSpace()
# print("DISK_total " + str(DISK_stats[0]))
# print("DISK_free " + str(DISK_stats[1]))
# print("DISK_perc " + str(DISK_stats[3]))


# print(getSystemInfo())
print(json.dumps(json.loads(getSystemInfo()), sort_keys=True, indent=4))

# print(json.dumps(encodeJson(getSystemInfo()),sort_keys=True, indent=4))


# print(psutil.virtual_memory().total)

# ifacelist = []


# ilist = netifaces.interfaces()
# print(ilist)

# print(netifaces.ifaddresses("{990FEF08-D9F8-4D91-9E86-3F64B5D605E5}")[netifaces.AF_LINK])

# for iface in netifaces.interfaces():
#     # ifacelist.append(netifaces.ifaddresses(iface)[netifaces.AF_LINK])
#     ifacelist.append(netifaces.ifaddresses(iface))


# print(json.dumps(ifacelist,sort_keys=True, indent=4))

# output machine serial code: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX

file = open(hostname + "sysinfo.txt", "w")
file.write(str(json.dumps(json.loads(getSystemInfo()), sort_keys=True, indent=4)))
file.close()