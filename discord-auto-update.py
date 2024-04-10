import os
import requests
import sys
import tarfile

installFolder = os.path.expanduser("~/bin/Discord")
tmpFolder = os.path.join(installFolder, "tmp")

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

def download_version(version):
    try:
        response = requests.get(f"https://dl.discordapp.net/apps/linux/{version}/discord-{version}.tar.gz")

        if (response.status_code == 200):
            os.makedirs(f"{tmpFolder}", exist_ok=True)
            with open(f"{tmpFolder}/discord-{version}.tar.gz", "wb") as file:
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

        with open(f"{installFolder}/version", "w") as file:
            file.write(version)
        os.system(f"rm -r {tmpFolder}")
        print(f"{version} installed")
    except Exception as e:
        print("Failed to extract the {version} version:", e)
        sys.exit(1)

latestVersion = get_latest_version()
latestVersinFile = download_version(latestVersion)
remove_current_version()
install_version(latestVersion, latestVersinFile)
print("Discord successfully installed")