#!/usr/bin/env python3
# vim: ts=4 sw=4 et

"""
Hits thespacedevs API to get list of upcoming launches.

Launches out of Vandenburg, California are surrounded with ***.

If the launch is within four hours, the webcast URL is included if available.
"""

from datetime import datetime, timezone
from dateutil import tz
from tabulate import tabulate
import requests

table = []
headers = ['Launch time', 'Description']
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
time_now = datetime.utcnow().replace(tzinfo=timezone.utc)

launches = requests.get(
        'https://ll.thespacedevs.com/2.2.0/launch/upcoming/?format=json&limit=20&mode=detailed',
        timeout=60,
).json()


#launches = requests.get(
#        'https://ll.thespacedevs.com/2.2.0/launch/upcoming/?format=json&limit=20&mode=detailed',
#        timeout=60,
#).text
#print(launches)
#
#exit()
for launch in launches['results']:
    # Convert launch time to local time
    utc_launch_time = datetime.strptime(launch['net'], TIME_FORMAT)
    local_launch_time = utc_launch_time.astimezone(tz.tzlocal())

    # Add *'s to launches from Vandenburg
    launch_name = launch['name']
    if 11 == launch['pad']['location']['id']:
        launch_name = f'***{launch_name}***'

    # Add webcast URL if launch is within 4 hours
    difference = utc_launch_time - time_now
    if difference.total_seconds() < 60 * 60 * 4: # 4 hours
        vid_urls = launch.get('vidURLs')
        #if vid_urls:
            #webcast_link = vid_urls[0]['url']
            #launch_name = f'{launch_name} {webcast_link}'
        for url in vid_urls:
            launch_name = f'{launch_name} {url["url"]}'

    # Detect RTLS landings
    rocket = launch.get('rocket')
    if rocket:
        launcher_stages = rocket.get('launcher_stage')
        if launcher_stages:
            for launcher_stage in launcher_stages:
                landing = launcher_stage.get('landing')
                if landing and landing['type']['id'] == 2:
                    launch_name = f'!!!{launch_name}'
                    break
                    

    # Add launch info to table output
    table.append([local_launch_time, launch_name])

print(tabulate(table, headers, tablefmt='simple'))
