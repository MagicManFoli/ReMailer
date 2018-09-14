# ReMailer

Run this service for an email adress and all forwarded messages from XING (and other services later) are being decoded and send back automatically. 

**Use this with a backup-address! No guarantees that a mistake won't delete everything!**

Additional structures for other handlers are prepared, this program will grow with it's requirements.

*Feel free to add functionalities or post issues!*

## Installation & Usage

Download this by "git clone"-ing this repository. Follow the instructions below to start it.

Turn off `save_mode` to enable auto-deletion of processed mails. Edit `t_restart` to change check intervals.

*This Code will never return*, so be prepared to kill it manually should the need arise.

## Forwarding vs Filtering:

**Warning**: Mail-Providers differ in their behaviour. This program deals with two behaviours:

### Manual Forwarding:
#### Pro: 
Easy to use, fast, mobile, always available.

#### Con: 
1. Needs manual interaction.
2. Can cut off original messages. This behaviour is not universal but was observed with Gmail. 
3. Not always detected for handlers, detection currently depends on the searching behaviour of the host-adress & will only work in Gmail.

### Filtering(Gmail):   *Use this if possible!* 
#### Pro: 
Automatic, full & silent forwarding without human intervention. Easy to detect & filter.
#### Con: 
Cumbersome to setup, follow official Gmail Guide.

## Using Pipenv:

Use `pipenv install [--python python3.7]` in cloned folder to generate environment ( execute `export PIPENV_TIMEOUT=500` in bash before restarting if you get a timeout on weaker systems)

Test with `pipenv run which python`, this should point to a custom virtualenv (e.g. /home/pi/.local/share/virtualenvs/ReMailer-A3UyrjCG/bin), copy that path
If wanted start manually with `/prev/path/to/python main.py`, this should use the previously stated python version

## Autostart with Pipenv (on Linux):
0. Start with previous chapter
1. Edit ReMailer.service to reflect your working directory ("~" in this example) and your custom python version from before.
2. Copy ReMailer.service `sudo cp ~/ReMailer/ReMailer.service /etc/systemd/system`
(call `sudo systemctl daemon-reload` to reload the service file if you need multiple tries)
3. Start Service manually to test everthing is working: `sudo systemctl start Remailer`
4. Check status: `systemctl status ReMailer.service`
5. Enable automatic execution: `sudo systemctl enable ReMailer`
