import os
import dotenv
import requests
import datetime as dt
import discord
import asyncio
import aiohttp

from asyncio.tasks import current_task
from discord import guild
from discord.ext import commands
from discord.ext import tasks

dotenv.load_dotenv()

# Discord
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
client = discord.Client(intents=intents)

# Env constants
DISCORD_TOKEN = str(os.getenv("DISCORD_TOKEN"))
BOOKING_CODE = str(os.getenv("BOOKING_CODE"))
PARTY_SIZE = str(os.getenv("PARTY_SIZE"))
SERVICE = str(os.getenv("SERVICE"))
BOOKING_CODE = str(os.getenv("BOOKING_CODE"))
USER_ID = int(os.getenv("USER_ID"))
GUILD = int(os.getenv("GUILD"))
CHANNEL = int(os.getenv("CHANNEL"))

# Dict to hold dates. Key will be the unique days, value will be a list of the times on said day
# format: {'2024-04-26': ['8:15pm'], '2024-05-01': ['4:00pm', '4:15pm', '8:00pm', '8:15pm', '8:30pm'], '2024-05-02': ['3:00pm', '3:15pm', '3:30pm', '3:45pm', '4:00pm', '4:15pm', '4:30pm', '4:45pm', '8:15pm', '8:30pm'], '2024-05-03': ['3:00pm']}
dates={}
# end_date=dt.date(2024, 6, 15)

# sleep time for each loop iteration through the available dates
sleep_time = 10 # minutes
rate_limit_sleep = 60 # seconds

@client.event
async def on_ready():
    """ Run on initialization of connection to Discord client
    """
    slow_count.start()

@tasks.loop(minutes = sleep_time)
async def slow_count():
    """ Call the check function on set time interval (default = 5 min)
    """
    if(slow_count.current_loop > -1):
        guild = client.get_guild(GUILD)
        await check()
        print(f"Sleeping for {sleep_time} minutes")

async def notify_discord(weekday, date, time):
    """Send notification to CHANNEL while pinging USER_ID

    Args:
        weekday (string): weekday (Monday, Tuesday, etc.)
        date (string): isodate formatted available day
        time (string): time on available day
    """
    guild = client.get_guild(GUILD)
    await guild.get_channel(CHANNEL).send(f"<@{USER_ID}> A new date was added for party size {PARTY_SIZE} for {SERVICE} on {weekday} {date} at {time}")


async def check():
    """Call the Casa Bonita API using the set parameters. Days are stored in a local data structure and if changes are added, the user will be notified on Discord
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }

    date = dt.date.today()
    semaphore = asyncio.Semaphore(1)

    while True:
        print(f"Checking availability for {date.strftime('%A')} {date}")
        RES_DATE = date.isoformat()
        url = f"https://casatix-api.casabonitadenver.com/api/v2/search?booking_code={BOOKING_CODE}&service={SERVICE}&res_date={RES_DATE}&party_size={PARTY_SIZE}"
        # print(url)

        flag = False
        await semaphore.acquire()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                try:
                    if response.status == 200:
                        data = await response.json()
                        if data['times_by_table_type']['default']:
                            if RES_DATE not in dates:
                                dates[RES_DATE] = []
                            for _time in data['times_by_table_type']['default']:
                                f_time = _time['time_display']
                                if f_time in dates[RES_DATE]:
                                    print(f"Reservation on {RES_DATE} at {f_time} already exists in local data")
                                    continue
                                else:
                                    dates[RES_DATE].append(f_time)
                                    print(f"Added {f_time} to {RES_DATE}")
                                    await notify_discord(date.strftime('%A'), RES_DATE, f_time)
                                # print(dates)

                    else:
                        print("Error:", response.status)
                        if response.status == 429:
                            print(f"Sleeping for {rate_limit_sleep} second(s) while rate limited")
                            await asyncio.sleep(rate_limit_sleep)
                            flag = True
                            semaphore.release()
                        elif response.status == 400:
                            print(f"{RES_DATE} does not exist in the calendar of dates yet")
                            break

                except requests.exceptions.RequestException as e:
                    print("Error:", e)

        if not flag:
            date += dt.timedelta(days=1)
            semaphore.release()

        # if date == end_date:
        #     break

if __name__ == '__main__':
    """Main
    """
    client.run(DISCORD_TOKEN)
