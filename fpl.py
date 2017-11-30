
import sys
import requests
from tabulate import tabulate

if len(sys.argv) < 3:
    print("USAGE: fpl.py group_id gameweek")
    sys.exit()
else:
    if not (sys.argv[1]).isnumeric() or not (sys.argv[2]).isnumeric():
        print("Group ID and Gameweek should be numericals")
        sys.exit()
    elif int(sys.argv[2]) > 38 or int(sys.argv[2]) < 1:
        print("Gameweek should be between 1 and 38")
        sys.exit()
    else:
        pass

print("Getting team and player data")
entire_data = requests.get('https://fantasy.premierleague.com/drf/bootstrap-static')
player_data = entire_data.json()['elements']
teams_data = entire_data.json()['teams']

teams = {}
for a in teams_data:
    teams[a['code']] = a['name']

players = {}
for a in player_data:
    row = {"name": a['web_name'], 'team': teams[a['team_code']]}
    players[a['id']] = row

print("Getting group data")
r = requests.get('https://fantasy.premierleague.com/drf/leagues-classic-standings/%s' % str(sys.argv[1]))
group_data = r.json()
in_data = group_data['standings']['results']

print("Getting squad picks data")
group_data = {}
winner = {"point": 0, "player": []}
for a in in_data:
    r1 = requests.get('https://fantasy.premierleague.com/drf/entry/%s/event/%s/picks' % (str(a['entry']), str(sys.argv[2])))
    row = {"manager": a['entry_name'], "rank": a['rank'], "player_name":
           a['player_name'], "main": [], "bench": []}
    if r1.status_code == 200:
        data = r1.json()
        for b in data['picks']:
            if(b['position'] < 12):
                row['main'].append(b['element'])
                if b['is_captain']:
                    row['captain'] = b['element']
                if b['is_vice_captain']:
                    row['vice_captain'] = b['element']
            else:
                row['bench'].append(b['element'])
                if b['is_captain']:
                    row['captain'] = b['element']
                if b['is_vice_captain']:
                    row['vice_captain'] = b['element']

        row['active_chip'] = data['active_chip']
        row['points'] = data['entry_history']['points']
        row['total_points'] = data['entry_history']['total_points']
        row['transfer_cost'] = data['entry_history']['event_transfers_cost']
        row['winner'] = ''
        row['actual_point'] = row['points'] - row['transfer_cost']

        # Look for highest point
        if row['actual_point'] > 0:
            if winner['point'] == row['actual_point']:
                winner['player'].append(a['entry'])
            elif winner['point'] < row['actual_point']:
                winner['point'] = row['actual_point']
                winner['player'] = [a['entry']]
            else:
                pass
        group_data[a['entry']] = row
    else:
        print("Are you sure the gameweek you entered is not a future one?")
        sys.exit()

# Assign Winners for the GW
for win in winner['player']:
    group_data[win]['winner'] = u'\u2713'

# Report Generation
# Main Data Source: group_data, players
data = []
for member in group_data:
    a = group_data[member]
    row = [a['manager'], a['player_name'], players[a['captain']]['name'],
           players[a['vice_captain']]['name'], a['active_chip'], a['points'],
           a['transfer_cost'], a['actual_point'], a['winner'], a['total_points']]
    data.append(row)

print(tabulate(data, ['Team', 'Manager', 'Captain', 'Vice Captain', 'Chips',
                      'GW Pts', 'Xfer Pts', 'Point', 'Winner', 'Total Pts']))
