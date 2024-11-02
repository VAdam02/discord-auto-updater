import os
import sys
import subprocess

installFolder = os.path.expanduser("/usr/share/discord")
updaterFolder = os.path.join(installFolder, "updater")
serviceFolder = "/etc/systemd/system"
desktopFile = "/usr/share/applications/discord.desktop"
user = "discord-auto-update"

def create_user():
    os.system("sudo useradd -r -s /bin/false discord-auto-update")

def create_install_folder():
    os.system(f"sudo mkdir -p {installFolder}")
    os.system(f"sudo mkdir -p {updaterFolder}")
    os.system(f"sudo mkdir -p /home/{user}")

def create_desktop_file():
    os.system(f"sudo touch {desktopFile}")

def copy_files():
    os.system(f"sudo cp discord-auto-update.py {updaterFolder}/discord-auto-update.py")
    os.system(f"sudo cp discord-auto-update.service {serviceFolder}/discord-auto-update.service")
    
def add_service():
    os.system("sudo systemctl daemon-reload")
    os.system("sudo systemctl enable discord-auto-update")

def update_permissions():
    os.system(f"sudo chown -R {user}:{user} {installFolder}")
    os.system(f"sudo chmod -R 755 {installFolder}")
    os.system(f"sudo chown {user}:{user} {desktopFile}")
    os.system(f"sudo chmod 644 {desktopFile}")
    os.system(f"sudo chown {user}:{user} /home/{user}")
    os.system(f"sudo chmod 644 /home/{user}")

def install_dependencies():
    try:
        subprocess.run("sudo -u discord-auto-update /bin/bash -c 'pip install psutil; exit'", shell=True, check=True)
        print("psutil installed successfully for discord-auto-update user.")
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        sys.exit(1)

def run_service():
    os.system(f"sudo systemctl start discord-auto-update")

try:
    create_user()
    create_install_folder()
    create_desktop_file()
    copy_files()
    add_service()
    update_permissions()
    install_dependencies()
    run_service()
except Exception as e:
    print(f"Failed to install Discord: {e}")
    sys.exit(1)
