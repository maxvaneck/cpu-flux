from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBServerError,InfluxDBClientError
import subprocess
import time
import datetime
import platform
import requests
import threading


class Measurements():

    def collect_cpu_temp(self):

        measurements = []

        lines = subprocess.check_output(['sensors']).decode("utf-8")
        lines = lines.split("\n")

        core = 0
        for line in lines:
            if "Core" in line:
                point_temp = {
                        "measurement": "cpu_temp",
                        "tags": {
                            "Cpu_core_temp": f"Cpu_core_temp_{core}",
                            "Host": str(platform.node())
                        },

                        "fields": {
                            "value": float(line[15:19])
                        }
                    }

                core = core + 1
                measurements.append(point_temp)


        return measurements

    def collect_cpu_clock(self):

        measurements = []

        lines = []
        with open("/proc/cpuinfo", "r") as file:
            for line in file:
                lines.append(line)

        core = 0
        for line in lines:
            if "MHz" in line:
                clock_point = {
                        "measurement": "cpu_clock",
                        "tags": {
                            "Cpu_core": f"Cpu_core{core}",
                            "Host": str(platform.node())
                        },
                        "fields": {
                            "value": float(line[11:])
                        }
                    }

                core = core + 1

                measurements.append(clock_point)

        return measurements



if __name__ == "__main__":



    client = InfluxDBClient(host="192.168.1.49",port=8086,database="telegraf")

    measurements = Measurements()

    while True:
        try:
            client.write_points(measurements.collect_cpu_clock())
            client.write_points(measurements.collect_cpu_temp())
        except Exception:
            time.sleep(150)
            print("Exception occurred")
            
        time.sleep(10)

