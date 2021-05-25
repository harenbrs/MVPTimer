#!/bin/bash

set -a; source .env; set +a

running=`screen -list | grep discord-mvptimer`

if [ -z "$running" ]; then
	screen -dLmS discord-mvptimer sh -c "$PYTHON bot.py"
fi
