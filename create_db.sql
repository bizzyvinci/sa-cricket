create database sa_cricket;

use sa_cricket;

create table mat(
    match_id int not null,
    odi_no int,
    opposition int,
    ground int,
    match_date date,
    toss varchar(1000),
    series varchar(1000),
    result varchar(1000),
    match_days varchar(1000),
    primary key(match_id)
);

create table player(
	player_id int not null,
    name varchar(100),
    odi_debut date,
    playing_role varchar(100),
    batting_style varchar(100),
    bowling_style varchar(100),
    fielding_position varchar(100),
    primary key(player_id)
);

create table bat(
	player int not null,
    mat int not null,
    runs int,
    ball int,
    M int,
    _4s int,
    _6s int,
    strike_rate decimal(5,2),
    primary key(player, mat)
);

create table bowl(
	player int not null,
    mat int not null,
    overs float(4,2),
    M int,
    runs int,
    wicket int,
    econ decimal(5,2),
    _0s int,
    _4s int,
    _6s int,
    wide int,
    no_ball int,
    primary key(player, mat)
);

create table ground(
	ground_id int not null,
    ground_name varchar(300),
    country varchar(100),
    primary key(ground_id)
);

create table opposition(
    opp_id int not null,
    opp_name varchar(30),
    rating int,
    primary key(opp_id)
);