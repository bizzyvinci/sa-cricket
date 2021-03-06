import requests
from bs4 import BeautifulSoup
import mysql.connector as mc
import extraction
import sqlite3

# This script writes to the database the data extracted from extraction.py

# MySQL was used. If you're using the code, change 'user' and 'password' in mc.connect()
# Alternatively you can choose to plug to sqlite3. Just note that some function e.g 'str_to_date' would not work

# Connect to database
cnx = mc.connect(user='bisola', password='@1Bullshit', host='127.0.0.1', database='sa_cricket')
cursor = cnx.cursor()

def write_matches_by_year(start, stop=2020):
	'''
	Takes start and stop year(default=2020) as input
	Then extract the matches between those years and write to DB
	'''
	for year in range(start, stop+1):
		res = requests.get('https://stats.espncricinfo.com/ci/engine/records/team/match_results.html?class=2;id={};team=3;type=year'.format(year))
		res.raise_for_status
		soup = BeautifulSoup(res.text, 'lxml')
		matches = soup.find('table', 'engineTable').tbody.find_all('tr')

		c=0
		for tr in matches:
			write_full_match(tr)
			# Just to see how far we've gone
			c+=1
			print(c, 'match')

def write_full_match(tr):
	'''
	write match data to mat table in DB
	write bat data to bat table in DB and
	write bowl data to bowl table in DB
	'''

	m = tr.find_all('td')

	# Don't write for games without result
	winner = m[2].string
	if winner=='no result': 
		print('found no result')
		return False

	# Who is the opposition
	team1 = m[0].a['href'].split('/')[-1].split('.')[0]
	team2 = m[1].a['href'].split('/')[-1].split('.')[0]
	if team1=='3':
		opposition = int(team2)
	else:
		opposition = int(team1)

	ground = m[4].a['href'].split('/')[-1].split('.')[0]
	date = m[5].string
	match_id = m[6].a['href'].split('/')[-1].split('.')[0]
	odi_no = m[6].a.string.split(' # ')[1]

	# Let's see which row that's being worked on
	print(opposition, ground, date, match_id, odi_no)

	# convert numbers to python interger
	opposition = int(opposition)
	ground = int(ground)
	match_id = int(match_id)
	odi_no = int(odi_no)

	# Some dates are like 'Sep 18-19, 2004'.
	# To avoid error in sql str_to_date, I'll take the first e.g 'Sep 18, 2004' in the above case.	
	date = str(date)
	if '-' in date:
		x = date.split('-')
		y = x[1].split(',')
		date = x[0] + ',' + y[1]

	match_url = 'https://stats.espncricinfo.com/ci/engine/match/{}.html'.format(match_id)

	# Incase of 404 error, extraction.full_match_extraction would return False.
	try: 
		match, bat, bowl = extraction.full_match_extraction(match_url)
	except:
		print('Couldn\'t extract match and therefore excluded')
		return False	

	add_match = '''
					insert into mat
					(match_id, odi_no, opposition, ground, match_date, toss, series, result, match_days)
					values(%d, %d, %d, %d, str_to_date("%s", "%%M %%d, %%Y"), "%s", "%s", "%s", "%s");
				'''
	# Double quotes are added above for all %s to avoid error (because some strings have comma)
	add_bat = '''
				insert into bat
				values(%d, %d, %d, %d, %d, %d, %d, %f);
			  '''
	add_bowl = '''
				insert into bowl
				values(%d, %d, %f, %d, %d, %d, %f, %d, %d, %d, %d, %d);
			   '''
	
	# strings are bs4.navigableString object. Therefore, convert to normal python string
	match_data = (match_id, odi_no, opposition, ground, date, str(match[0]), str(match[1]), str(match[2]), str(match[3]))
	cursor.execute(add_match % match_data)
	cnx.commit()

	for b in bat:
		# It is important to convert the following to int or float before processing them into sql statement
		# However, issues of '-' apearing needs to be solved with the following
		for i in range(6):
			try: b[i] = int(b[i])
			except: b[i] = -99
		# :) why -99? Nothing really
		# I'll prefer nan but '' won't work.
		# -99 would cause outlier and disrupt analysis better than -1.
		# So I'll remember to handle nan	

		try: b[6] = float(b[6])
		except: b[6] = -99
		# To here

		bat_data = (b[0], match_id, b[1], b[2], b[3], b[4], b[5], b[6])
		cursor.execute(add_bat % bat_data)
		cnx.commit()

	for b in bowl:
		# Same as bat
		# I noticed some overs and econ were float. Initial plan was to save as float.
		# That doesn't make sense and to make things simpler, I'll use one for statement only.
		# Just incase float matters, I can edit extraction.py and rearrange the return or simply create a new list here.
		# e.g try a[i] = int(b[i])....; bowl_data = (int(b[0])..., float(b[1]))
		# I can already see errors b4 I finish typing but you'll surely figure out something
		for i in range(11):
			try: b[i] = int(b[i])
			except: b[i] = -99
		bowl_data = (b[0], match_id, b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8], b[9], b[10])
		cursor.execute(add_bowl % bowl_data)
		cnx.commit()

	return True

def write_player():
	'''
	Select unique players from bat and bowl table,
	extract their data using extraction module and 
	write to table player in DB
	'''

	select_batters = 'select distinct player from bat;'
	cursor.execute(select_batters)
	rows = cursor.fetchall()

	select_bowlers = 'select distinct player from bowl;'
	cursor.execute(select_bowlers)
	rows.extend(cursor.fetchall())

	#set(rows) removes duplicate for players in bat and bowl
	rows = set(rows)

	add_player = '''
					insert into player
					values(%d, "%s",  str_to_date("%s", "%%M %%d, %%Y"), "%s", "%s", "%s", "%s")
				 '''
	
	# Counter
	aim = len(rows)
	done = 1

	for player in rows:	
		player = player[0]	# Tuples were returned from select query e.g (35464,)
		print('working on player', player)
		player_url = 'https://www.espncricinfo.com/southafrica/content/player/{}.html'.format(player)
		b = extraction.extract_player(player_url)
		player_data = (player, str(b[0]), str(b[1]), str(b[2]), str(b[3]), str(b[4]), str(b[5]))
		cursor.execute(add_player % player_data)
		cnx.commit()
		print('added player', player)
		print(done, '/', aim, 'completed')
		done+=1

def write_ground():
	'''
	Select unique ground from mat table,
	extract their data using extraction module and 
	write to table ground in DB
	'''	
	select_query = 'select distinct ground from mat;'
	add_ground = '''
					insert into ground
					values(%d, "%s", "%s");
				 '''
	cursor.execute(select_query)
	rows = cursor.fetchall()

	# Counter
	aim = len(rows)
	done = 1

	for ground in rows:
		ground = ground[0] # Tuples were returned from select query
		print('working on ground', ground)
		ground_url = 'https://www.espncricinfo.com/ci/content/ground/{}.html'.format(ground)
		g = extraction.extract_ground(ground_url)
		ground_data = (ground, str(g[0]), str(g[1]))
		cursor.execute(add_ground % ground_data)
		cnx.commit()
		print('added ground', ground)
		print(done, '/', aim, 'completed')
		done+=1
	
	return True


def write_opposition():
	'''
	Select unique opposition from mat table,
	extract their data here and 
	write to table opposition in DB
	'''	
	team_name = {}
	team_rating = {}

	# Get all id and name
	res = requests.get('https://www.espncricinfo.com/story/_/id/18791072/all-cricket-teams-index')
	res.raise_for_status
	soup = BeautifulSoup(res.text, 'lxml')
	male_teams = soup.find('div', 'teams-section')
	team_link = male_teams.find_all('a', 'team-column')
	for team in team_link:
		team_id = int(team['href'].split('/')[-2])
		name = team.find('h5', 'header-title label').string
		team_name[team_id] = str(name)

	

	# Get ratings
	res = requests.get('https://www.espncricinfo.com/rankings/content/page/211271.html')
	res.raise_for_status
	soup = BeautifulSoup(res.text, 'lxml')
	icc = soup.find_all('table', 'StoryengineTable')[1]
	rows = icc.find_all('tr')
	#0 is the header and contains th instead of td. So to prevent error in the following for statement
	rows.pop(0) 
	for tr in rows:
		td = tr.find_all('td')
		name = td[1].string
		rating = int(td[-1].string)
		team_rating[name] = rating
	
	# get all distinct id from mat and save id, name and rating to opposition
	select_query = 'select distinct opposition from mat;'
	cursor.execute(select_query)
	rows = cursor.fetchall()
	add_opposition = 'insert into opposition values (%d, "%s", %d)'

	# Counter
	aim = len(rows)
	done = 1

	for team in rows:
		team = team[0] # Tuples were returned from select query
		print('working on team', team)

		# Kenya, Netherlands and Canada are not in record and therefore dealt with seperately
		if team==26:
			name = 'Kenya'
			rating = -99
		elif team==17:
			name = 'Canada'
			rating = -99
		elif team==15:
			name = 'Netherlands'
			rating = -99
		else:
			name = team_name[team]

			# The name of some countries appeared different accross the two pages e.g United Arab Emirates=UAE etc
			if name=='United States of America': name_id='USA'
			elif name=='United Arab Emirates': name_id='UAE'
			elif name=='Papua New Guinea': name_id='PNG'
			else: name_id=name

			rating = team_rating[name_id]
		#print(team, name, rating)
		cursor.execute(add_opposition % (team, name, rating))
		cnx.commit()
		print('added team', team)
		print(done, '/', aim, 'completed')
		done+=1

'''
# PROCEDURE
write_full_match(2000,2020)
write_player()
write_ground()
write_opposition()
'''
cursor.close()
cnx.close()