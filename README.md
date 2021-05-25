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

 89h51m ago Mistress (mjolnir_04)
 65h46m ago Pharaoh (in_sphinx5)
 40h 6m ago Gopinich (mosk_dun03)
 17h53m ago Dracula (gef_dun01)
  0h32m ago Moonlight Flower (pay_dun04)
  0h19m ago Osiris (moc_pryd04)
  0h11m ago Amon Ra (moc_pryd06)
  0h 2m ago Turtle General (tur_dun04)

Will spawn:

in  0h27m+ Hatii (xmas_fild01)
in  0h28m+ Golden Thief Bug (prt_sewb4)
in  0h31m+ Eddga (pay_fild11)
in  0h34m+ Phreeoni (moc_fild17)
in  0h42m+ Orc Lord (gef_fild10)
in  3h25m+ Tao Gunka (beach_dun)
in  6h32m+ Eddga (gld_dun01)

Last update: 25 May 2021 17:35 UTC.
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

To stop:

```
$ ./stop.sh
```