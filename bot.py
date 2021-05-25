import asyncio
from datetime import datetime
import math
import sys

import discord

from mvptimer import MVPTimer


class DiscordMVPTimer(MVPTimer):
    def __init__(self, *args, token, guild_name, channel_name, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.client = discord.Client()
        self.on_ready = self.client.event(self.on_ready)
        self.client.loop.create_task(self.update_task())
        
        self.token = token
        self.guild_name = guild_name
        self.channel_name = channel_name
        
        self.channel = None
        self.message = None
        self.last_message = None
    
    def start(self):
        self.login()
        
        self.log.info(f"Website: logged in as {self.username}")
        
        self.client.run(self.token)
    
    async def update_task(self):
        await self.client.wait_until_ready()
        
        self.log.info("Discord: client ready")
        
        while self.message is None:
            await asyncio.sleep(1)
        
        try:
            while not self.client.is_closed():
                message = self.update()
                await self.publish(message)
                await asyncio.sleep(self.update_period)
        finally:
            self.session.close()
    
    async def publish(self, message):
        if message != self.last_message:
            try:
                await self.message.edit(content=message)
                self.last_message = message
            except:
                self.log.error("Error publishing message", sys.exc_info())
    
    def format_timers(self, timers):
        msg = "_ _"
        
        if timers[0]:
            msg += "\n:white_check_mark: Spawned:\n```"
            for (time, minutes), name in timers[0]:
                if self.time_relative:
                    h, m = int(minutes//60), int(math.floor(minutes%60))
                    row = f"{h:3}h{m:2}m ago {name}"
                else:
                    row = "{} {}".format(
                        time.astimezone(self.local_tz).strftime("%H:%M"), name
                    )
                msg += "\n" + row
            msg += "\n```"
        
        if timers[1]:
            msg += "\n:warning: Spawning:\n```"
            for (time, minutes), name in timers[1]:
                if self.time_relative:
                    row = f"in <{int(math.ceil(abs(minutes)))}m {name}"
                else:
                    row = "<{} {}".format(
                        time.astimezone(self.local_tz).strftime("%H:%M"), name
                    )
                msg += "\n" + row
            msg += "\n```"
        
        if timers[2]:
            msg += "\n:stop_sign: Will spawn:\n```"
            for (time, minutes), name in timers[2]:
                if self.time_relative:
                    h, m = int(abs(minutes)//60), int(math.floor(abs(minutes)%60))
                    row = f"in {h:2}h{m:2}m+ {name}"
                else:
                    row = "{}+ {}".format(
                        time.astimezone(self.local_tz).strftime("%H:%M"), name
                    )
                msg += "\n" + row
            msg += "\n```"
        
        msg += (
            "\nLast update: "
            + datetime.now(self.server_tz).strftime("%d %b %Y %H:%M")
            + " "
            + self.server_tz.tzname(datetime.now())
            + "."
        )
        
        return msg
    
    async def on_ready(self):
        self.log.info(f"Discord: logged in as {self.client.user.name}")
        
        for c in self.client.get_all_channels():
            if c.guild.name == self.guild_name and c.name == self.channel_name:
                self.log.info(
                    f"Discord: selected guild: {c.guild.name}, channel: {c.name}"
                )
                self.channel = self.client.get_channel(c.id)
                break
        else:
            raise ValueError(
                f"channel {self.channel_name} not found on server {self.guild_name}"
            )
        
        def is_me(m):
            return m.author == self.client.user
        
        async for m in self.channel.history():
            if is_me(m):
                self.message = m
                self.log.info("Discord: found own message")
            else:
                self.log.info(f"Discord: found message by {m.author}")
        
        if self.message is None:
            self.log.info("Discord: sending initial message")
            self.message = await self.client.send_message(self.channel, "_ _")
        
        deleted = await self.channel.purge(limit=100, check=is_me, before=self.message)
        self.log.info(f"Discord: deleted {len(deleted)} message(s)")


if __name__ == '__main__':
    from dotenv import dotenv_values
    
    config = dotenv_values()
    
    bot = DiscordMVPTimer(
        base_url=config['BASE_URL'],
        server=config['SERVER'],
        username=config['USERNAME'],
        password=config['PASSWORD'],
        server_tz=config['SERVER_TZ'],
        local_tz=config['LOCAL_TZ'],
        time_relative=bool(int(config.get('TIME_RELATIVE', 0))),
        max_minutes=int(config.get('MAX_MINUTES', 60000)),
        update_period=int(config.get('UPDATE_PERIOD', 30)),
        token=config['TOKEN'],
        guild_name=config['GUILD_NAME'],
        channel_name=config['CHANNEL_NAME']
    )
    
    bot.start()
