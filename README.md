# Analysis of South Africa cricket games

Predict South African player's performance in cricket games from 2017 to 2019.

**Project is closed**. This is a small implementation of *cricket_journal.pdf*, but with South Africa (not india).
Exploratory analysis of game victories from 2000 to 2020 was also be performed.

Folders:
* data_mining: scripts for extracting and saving data
* notebook: notebooks for exploratory analysis and Machine learning
* dataset: datasets in csv and sql format

All the data has been extracted from [espncricinfo.com](https://www.espncricinfo.com/) and saved in sqlite file `sa_cricket.db`. 

The procedure for extracting their data is as follows:
* Create database (*create_db.sql*)
* write_full_match(2000,2020)
* write_player()
* write_ground()
* write_opposition()

Initial plan was:
* Create database (*create_db.sql*)
* Write match by year from 2017 to 2019 (*write_to_db.py*)
* Write players, ground and opposition
* Select minimum odi debut in table `players` (2004 in this case). Run the following sql query
	* `select min(year(odi_debut)) from sa_cricket.player;`
* Write match from the minimum odi debut to 2016 (you can exclude players that are not in table `player` this time around)

MySQL was the database used in the extraction. Alternatively, sqlite can be used too. Just note that some functions in MySQL are not in sqlite.

Note: I don't play or know cricket. So, if some of my decisions or logic seems funny, please let me know. 

And get ready to explain to a child. Just kidding. I'll do more research if your explanation is terrible. Thanks in advance.
