# Discord MVP timer bot

## Requirements
- Python 3
- FluxCP with recent MVP kill list
- Discord bot token with sufficient channel permissions

## Installation

```
$ git clone https://github.com/harenbrs/MVPTimer.git
$ cd MVPTimer
$ pip install -r requirements.txt
```

Populate `.env` file (ensure using quotes for values `"containing spaces"`):

```
PYTHON=/path/to/venv/bin/python  # path to Python binary, for use with virtual environments
BASE_URL=...                     # URL of FluxCP
SERVER=...                       # Server name, used in FluxCP's login form
USERNAME=...                     # FluxCP username
PASSWORD=...                     # FluxCP password
SERVER_TZ=UTC                    # Timezone used in the MVP ranking
LOCAL_TZ=Europe/Dublin           # Timezone to display locally
TOKEN=...                        # Discord bot token
GUILD_NAME=...                   # Discord "guild" (server) name
CHANNEL_NAME=...                 # Discord channel name
TIME_RELATIVE=1                  # Whether to display relative time strings ("in ...", "... ago")
MAX_MINUTES=60000                # Hide MVPs last killed more than this many minutes ago
UPDATE_PERIOD=30                 # Update period in seconds
```

## Usage (terminal):

```
$ python mvptimer.py
Spawned:

 85h16m ago Pharaoh (in_sphinx5)
 59h35m ago Gopinich (mosk_dun03)
 37h23m ago Dracula (gef_dun01)
 18h37m ago Orc Lord (gef_fild10)
 17h 1m ago Amon Ra (moc_pryd06)
 16h55m ago Turtle General (tur_dun04)
 16h21m ago Moonlight Flower (pay_dun04)
 15h54m ago Tao Gunka (beach_dun)
 13h44m ago Osiris (moc_pryd04)
 13h 3m ago Samurai Specter (ama_dun03)
 12h47m ago Eddga (gld_dun01)
 12h38m ago Doppelganger (gef_dun02)
  5h22m ago Golden Thief Bug (prt_sewb4)
  4h19m ago Eddga (pay_fild11)
  4h13m ago Hatii (xmas_fild01)

Spawning:

in <9m Orc Hero (gef_fild14)

Will spawn:

in  1h 3m+ Phreeoni (moc_fild17)
in 15h 0m+ Orc Hero (gef_fild02)

Last update: 26 May 2021 13:04 UTC.
```

## Usage (Discord):

```
$ ./start.sh
```

The Discord bot is now running in a `screen` session:

```
$ screen -ls
There is a screen on:
	5945.discord-mvptimer	(05/25/21 15:56:07)	(Detached)
```

<div align="center">
<img src="https://user-images.githubusercontent.com/1812261/119664692-80e08100-be2b-11eb-8078-50d1dca5aeca.png" width="500">
</div>

To stop:

```
$ ./stop.sh
```