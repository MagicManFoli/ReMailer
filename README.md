# ReMailer

Run this service for an email adress and all forwarded messages from XING are being decoded and send back automatically.

Use "pipenv install [--python python3.7] in folder to generate environment (sometimes a second run is needed)

Test with "pipenv run which python", this should point to a custom virtualenv
Start manually with "pipenv run python main.py", this should use the previously stated python version



# Autostart (on Linux)
1. Edit ReMailer.service to reflect your working directory ("~" in this example)
2. Copy ReMailer.service "sudo cp ~/ReMailer/ReMailer.service /etc/systemd/system"

// TODO: install pipenv even for systemd environment

3. Start Service: "sudo systemctl start Remailer" // This can timeout on weaker systems
4. Check status: "systemctl status ReMailer.service"
5. Enable automatic execution: "sudo systemctl enable ReMailer"
