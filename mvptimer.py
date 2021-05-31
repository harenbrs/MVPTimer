import ast
from datetime import datetime, timedelta
import logging
import math
import pickle
import re
import sys
from time import sleep

from bs4 import BeautifulSoup
from dateutil import parser
import pytz
import requests


class MVPTimer:
    login_loc = '?module=account&action=login'
    logout_loc = '?module=account&action=logout'
    mvp_loc = '?module=ranking&action=mvp'
    mob_db_url = 'http://ratemyserver.net/mob_db.php?mob_id={mob_id}&small=1&back=1'
    
    def __init__(
        self,
        base_url,
        server,
        username,
        password,
        server_tz,
        local_tz,
        time_relative=True,
        max_minutes=60000,
        update_period=30,
        log_level=logging.INFO
    ):
        self.base_url = base_url
        self.server = server
        self.username = username
        self.password = password
        self.server_tz = pytz.timezone(server_tz)
        self.local_tz = pytz.timezone(local_tz)
        self.time_relative = time_relative
        self.max_minutes = max_minutes
        self.update_period = update_period
        
        try:
            with open('last_kills.repr', 'r') as f:
                self.last_kills = ast.literal_eval(f.read())
        except:
            self.last_kills = {}
        
        try:
            with open('respawn_windows.pkl', 'rb') as f:
                self.respawn_windows = pickle.load(f)
        except:
            self.respawn_windows = {}
        
        self.session = requests.Session()
        
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='[%H:%M:%S]')
        self.log = logging.getLogger()
        self.log.setLevel(log_level)
    
    def start(self, callback=print):
        self.login()
        
        try:
            while True:
                callback(self.update())
                
                sleep(self.update_period)
        finally:
            self.session.close()
    
    def update(self):
        self.parse_kills()
        timers = self.update_timers()
        return self.format_timers(timers)
    
    def login(self):
        self.session.post(
            self.base_url + self.login_loc,
            dict(server=self.server, username=self.username, password=self.password)
        )
    
    def parse_kills(self, relogin=False):
        if relogin:
            self.login()
        
        try:
            html = self.session.get(self.base_url + self.mvp_loc).content
        except:
            self.log.error("Error parsing kills:", sys.exc_info())
            return
        
        try:
            rows = (
                BeautifulSoup(html, 'html.parser')
                .find('table', attrs={'class': 'horizontal-table'})
                .find_all('tr')[1:]
            )
        except AttributeError:
            if relogin:
                raise
            else:
                return self.parse_kills(relogin=True)
        
        def parse_row(row):
            cells = row.find_all('td')
            time = cells[0].contents[0]
            player = cells[1].contents[0].strip()
            monster_name = cells[2].contents[1].text
            monster_id = cells[2].contents[1].attrs['href'].split('id=')[-1]
            map_name = cells[4].contents[0].strip()
            return time, player, monster_name, monster_id, map_name
        
        kills = [parse_row(row) for row in rows]
        
        monsters = sorted(set([k[2:] for k in kills]))
        
        for monster_name, monster_id, map_name in monsters:
            last_kill = [
                k[0] for k in kills if k[2:] == (monster_name, monster_id, map_name)
            ][0]
            self.last_kills[(monster_name, monster_id, map_name)] = last_kill
        
        with open('last_kills.repr', 'w') as f:
            f.write(repr(self.last_kills))
    
    def update_timers(self):
        now = datetime.now(self.server_tz)
        
        timer_lists = [[], [], []]
        
        for (monster_name, monster_id, map_name), last_kill in sorted(
            self.last_kills.items(), key=lambda x: x[1]
        ):
            respawn_window = self.get_respawn_window(monster_id, map_name)
            if respawn_window is None:
                continue
            
            dt = self.server_tz.localize(parser.parse(last_kill))
            minutes_since = (now - dt).total_seconds()/60
            
            if self.max_minutes is not None and minutes_since > self.max_minutes:
                continue
            
            time_open = dt + timedelta(seconds=60*min(respawn_window))
            time_close = dt + timedelta(seconds=60*max(respawn_window))
            
            if minutes_since > max(respawn_window):
                status = 0  # Respawn window complete
                time_data = time_close, minutes_since - max(respawn_window)
            elif minutes_since > min(respawn_window):
                status = 1  # Respawn window open
                time_data = time_close, minutes_since - max(respawn_window)
            else:
                status = 2  # Respawn window not reached
                time_data = time_open, minutes_since - min(respawn_window)
            
            timer_lists[status].append((time_data, f"{monster_name} ({map_name})"))
        
        return [sorted(l) for l in timer_lists]
    
    def format_timers(self, timers):
        msg = ""
        
        if timers[0]:
            msg += "Spawned:\n"
            for (time, minutes), name in timers[0]:
                if self.time_relative:
                    h, m = int(minutes//60), int(math.floor(minutes%60))
                    row = f"{h:3}h{m:2}m ago {name}"
                else:
                    row = "{} {}".format(
                        time.astimezone(self.local_tz).strftime("%H:%M"), name
                    )
                msg += "\n" + row
            msg += "\n"
        
        if timers[1]:
            msg += "\nSpawning:\n"
            for (time, minutes), name in timers[1]:
                if self.time_relative:
                    row = f"in <{int(math.ceil(abs(minutes)))}m {name}"
                else:
                    row = "<{} {}".format(
                        time.astimezone(self.local_tz).strftime("%H:%M"), name
                    )
                msg += "\n" + row
            msg += "\n"
        
        if timers[2]:
            msg += "\nWill spawn:\n"
            for (time, minutes), name in timers[2]:
                if self.time_relative:
                    h, m = int(abs(minutes)//60), int(math.floor(abs(minutes)%60))
                    row = f"in {h:2}h{m:2}m+ {name}"
                else:
                    row = "{}+ {}".format(
                        time.astimezone(self.local_tz).strftime("%H:%M"), name
                    )
                msg += "\n" + row
            msg += "\n"
        
        msg += (
            "\nLast update: "
            + datetime.now(self.server_tz).strftime("%d %b %Y %H:%M")
            + " "
            + self.server_tz.tzname(datetime.now())
            + "."
        )
        
        return msg
    
    def get_respawn_window(self, monster_id, map_name):
        if (monster_id, map_name) in self.respawn_windows:
            return self.respawn_windows[(monster_id, map_name)]
        
        try:
            window = self.fetch_respawn_window(monster_id, map_name)
        except ValueError:
            return None
        
        self.respawn_windows[(monster_id, map_name)] = window
        
        with open('respawn_windows.pkl', 'wb') as f:
            pickle.dump(self.respawn_windows, f)
        
        return window
    
    def fetch_respawn_window(self, monster_id, map_name):
        html = self.session.get(self.mob_db_url.format(mob_id=monster_id)).content
        soup = BeautifulSoup(html, 'html.parser')
        
        a = soup.find(href=re.compile(map_name))
        
        if a is None:
            return None
        
        return [
            int(mins)
            for mins in a.parent()[-1].text.split(' / ')[-1].split(' ')[0].split('~')
        ]


if __name__ == '__main__':
    from dotenv import dotenv_values
    
    config = dotenv_values()
    
    mvptimer = MVPTimer(
        base_url=config['BASE_URL'],
        server=config['SERVER'],
        username=config['USERNAME'],
        password=config['PASSWORD'],
        server_tz=config['SERVER_TZ'],
        local_tz=config['LOCAL_TZ'],
        time_relative=bool(int(config.get('TIME_RELATIVE', 0))),
        max_minutes=int(config.get('MAX_MINUTES', 60000)),
        update_period=int(config.get('UPDATE_PERIOD', 30))
    )
    
    mvptimer.start()
