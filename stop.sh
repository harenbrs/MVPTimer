#!/bin/bash

running=`screen -list | grep discord-mvptimer`

if [ -n "$running" ]; then
	screen -S discord-mvptimer -p 0 -X stuff $'\cC'
fi

