# Analysis of South Africa cricket games

Predict South African player's performance in cricket games from 2017 to 2019.

Work still in progress. This is an implimentation of *cricket_journal.pdf*, but with South Africa (not india).

All the data was extracted from espncricinfo.com and saved in sqlite file `sa_cricket.db`. 

Games between 2017 and 2019 are analyzed and the procedure for extracting their data is as follows:
* Create database (*create_db.sql*)
* Write match by year from 2017 to 2019 (*write_to_db.py*)
* Write players, ground and opposition
* Select minimum odi debut in table `players` (2004 in this case). Run the following sql query
	* `select min(year(odi_debut)) from sa_cricket.player;`
* Write match from the minimum odi debut to 2016 (you can exclude players that are not in table `player` this time around)


