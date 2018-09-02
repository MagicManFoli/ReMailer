# ReMailer

Run this service for an email adress and all forwarded messages from XING are being decoded and send back automatically.
This Code will never return, so be prepared to kill it manually should the need arise.

Download this by "git clone"-ing this repository.

# Using with Pipenv:

Use "pipenv install [--python python3.7] in cloned folder to generate environment ( execute "export PIPENV_TIMEOUT=500" before restarting if you get a timeout on weaker systems)

Test with "pipenv run which python", this should point to a custom virtualenv (e.g. /home/pi/.local/share/virtualenvs/ReMailer-A3UyrjCG/bin), copy that path
If wanted start manually with "/prev/path/to/python main.py", this should use the previously stated python version

# Autostart (on Linux):
0. Start with previous chapter
1. Edit ReMailer.service to reflect your working directory ("~" in this example) and your custom python version.
2. Copy ReMailer.service "sudo cp ~/ReMailer/ReMailer.service /etc/systemd/system"
2.5 call "sudo systemctl daemon-reload" to reload the service file if you needed multiple tries.

// TODO: install pipenv even for systemd environment

3. Start Service manually to test everthing is working: "sudo systemctl start Remailer"
4. Check status: "systemctl status ReMailer.service"
5. Enable automatic execution: "sudo systemctl enable ReMailer"
