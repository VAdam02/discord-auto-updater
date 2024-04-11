import argparse
import os
import psutil
import re
import requests
import sys
import tarfile

installFolder = os.path.expanduser("~/bin/Discord")
tmpFolder = os.path.join(installFolder, "tmp")
minBatteryLevel = 50

def is_battery_ok():
    battery_status = psutil.sensors_battery()

    if battery_status.power_plugged:
        return True
    
    if battery_status.percent < minBatteryLevel:
        return False
    else:
        return True


def get_latest_version():
    try:
        response = requests.get("https://discord.com/api/v10/updates?platform=linux")
        response.raise_for_status()
        version = response.json()["name"]
        print(f"Latest version: {version}")
        return version
    except requests.exceptions.RequestException as e:
        print("Failed to fetch the latest version:", e)
        sys.exit(1)

def get_current_version():
    if not os.path.isfile(os.path.join(installFolder, "version")):
        return "0.0.0"
    with open(os.path.join(installFolder, "version"), "r") as file:
        version = file.read()
        print(f"Current version: {version}")
        return version

def download_version(version):
    try:
        response = requests.get(f"https://dl.discordapp.net/apps/linux/{version}/discord-{version}.tar.gz")

        if (response.status_code == 200):
            os.makedirs(tmpFolder, exist_ok=True)
            with open(os.path.join(tmpFolder, f"discord-{version}.tar.gz"), "wb") as file:
                file.write(response.content)
            print(f"Downloaded version {version}")
        else:
            print(f"Failed to download version {version} (status code: {response.status_code})")
            sys.exit(1)

        return f"discord-{version}.tar.gz"
    except Exception as e:
        print("Failed to download the latest version:", e)
        sys.exit(1)

def remove_current_version():
    try:
        for item in os.listdir(installFolder):
            itemPath = os.path.join(installFolder, item)
            if itemPath == tmpFolder:
                continue
            if os.path.isdir(itemPath):
                os.system(f"rm -rf {itemPath}")
            else:
                os.remove(itemPath)
        print("Current version removed")
    except Exception as e:
        print("Failed to remove the current version:", e)
        sys.exit(1)

def install_version(version, versionFile):
    try:
        with tarfile.open(os.path.join(tmpFolder, versionFile), "r:gz") as tar:
            rootFolder = tar.getnames()[0]
            tar.extractall(tmpFolder)
            os.system(f"mv {tmpFolder}/{rootFolder}/* {installFolder}")

        with open(os.path.join(installFolder, "version"), "w") as file:
            file.write(version)
        os.system(f"rm -r {tmpFolder}")
        print(f"{version} installed")
    except Exception as e:
        print("Failed to extract the {version} version:", e)
        sys.exit(1)

def register_software():
    desktopfile = list(filter(re.compile("[a-zA-Z]+[.]desktop").match, os.listdir(installFolder)))
    if len(desktopfile) != 1:
        print("Too much or no .desktop file present")
        sys.exit(1)
    desktopfile = desktopfile[0]

    values = {}
    with open(os.path.join(installFolder, desktopfile), "r") as file:
        for line in file:
            line = line.strip()
            if line == "[Desktop Entry]":
                continue
            key, value = line.strip().split('=')
            values[key] = value
    
    values["Exec"] = "/usr/bin/python3 " + os.path.abspath(__file__)
    values["Path"] = installFolder

    print(os.path.abspath(__file__))

    with open(os.path.join(os.path.expanduser("~/.local/share/applications"), desktopfile), "w") as file:
        file.write("[Desktop Entry]\n")
        for key, value in values.items():
            file.write(f"{key}={value}\n")

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--soft-update", action="store_true", help="Set this flag to only update if the battery level is above 50%")
args = parser.parse_args()

if args.soft_update and not is_battery_ok():
    print(f"Battery level is below {minBatteryLevel}%")
    sys.exit(1)

latestVersion = get_latest_version()
currentVersion = get_current_version()
if (latestVersion != currentVersion):
    latestVersinFile = download_version(latestVersion)
    remove_current_version()
    install_version(latestVersion, latestVersinFile)
    register_software()
    print("Discord successfully installed")
else:
    print("Discord not need to update")

if all(value == False for value in vars(args).values()):
    os.system(os.path.join(installFolder, "Discord"))