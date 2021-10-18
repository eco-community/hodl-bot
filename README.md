# EcoHodlBot

A bot that can generate APY


## How HODL bot works
- users who want to stake need to write to the bot
- they will be asked if they want to begin staking and present with some choices
- if they opt-in staking they will be asked to HODL point and to not move them
- if they HODL points for the whole staking epoch they will earn % of APY
- if they started staking in between epochs their stake will be counted towards the next epoch
- bot will watch staking balance and if a user moves part of their points that part won't be counted


## How staking works
- staking is split into Epochs
- if users started staking in between epochs their stake will be counted in the next epoch
- in other words, a user needs to stake throughout the whole epoch to be eligible for rewards
- at the end of the epoch admins will be DMed with a list of users and rewards


## Installation
1. [Install Docker](https://docs.docker.com/engine/install/ubuntu/)
2. Copy and update settings in `.env.example`
3. Execute `docker-compose up -d`
4. Install requirements from `requirements.txt` for `>= Python 3.8`
5. Copy and update settings in `config.example.py`
6. Init database tables via `aerich upgrade`
7. Start bot via `python bot.py` or [via supervisord](http://supervisord.org/) or [systemd](https://es.wikipedia.org/wiki/Systemd)
8. Add a bot to the server with at least `68608` scope
