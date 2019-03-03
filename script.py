from influxdb import InfluxDBClient
import subprocess
import time
import platform

import multiprocessing
import argparse


class Measurements():

    def collect_cpu_temp(self):
        if "arm" in platform.machine():
            return self.collect_cpu_temp_arm()
        else:
            return self.collect_cpu_temp_x86()

    def collect_cpu_temp_arm(self):
        measurements = []
        core = 0

        for node in range(0,5):
            with open(f"/sys/devices/virtual/thermal/thermal_zone{core}/temp", "r") as file:
                clock_point = {
                    "measurement": "cpu_temp",
                    "tags": {
                        "Cpu_core": f"Cpu_core{core}",
                        "Host": str(platform.node())
                    },
                    "fields": {
                        "value": float(file.read())
                    }
                }
                measurements.append(clock_point)
                core +=1
        return measurements


    def collect_cpu_temp_x86(self):

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

                core +=1
                measurements.append(point_temp)
        return measurements

    def collect_cpu_clock(self):
        if "arm" in platform.machine():
            return self.collect_clock_arm()

        else:
            return self.collect_clock_x86()


    def collect_clock_arm(self):
        measurements = []
        core = 0

        for node in range(multiprocessing.cpu_count()):
            with open(f"/sys/devices/system/cpu/cpu{core}/cpufreq/cpuinfo_cur_freq", "r") as file:
                clock_point = {
                    "measurement": "cpu_clock",
                    "tags": {
                        "Cpu_core": f"Cpu_core{core}",
                        "Host": str(platform.node())
                    },
                    "fields": {
                        "value": float(file.read())
                    }
                }
                measurements.append(clock_point)

            core +=1
        return measurements

    def collect_clock_x86(self):
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

    parser = argparse.ArgumentParser()
    parser.add_argument("test", help="arguement for ci testing")
    args = parser.parse_args()



    client = InfluxDBClient(host="192.168.1.128",port=8086,database="telegraf")

    measurements = Measurements()

    if args.test is True:
        print("testing")
        try:
            client.write_points(measurements.collect_cpu_clock())
            client.write_points(measurements.collect_cpu_temp())
        except Exception:
            time.sleep(150)
            print("Exception occurred")

    if args.test is False:
        while True:
            try:
                client.write_points(measurements.collect_cpu_clock())
                client.write_points(measurements.collect_cpu_temp())
            except Exception:
                time.sleep(150)
                print("Exception occurred")

            time.sleep(10)

