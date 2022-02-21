# NFTCollectionsWatcher #

A Telegram bot that watches over an NFT collection on several marketplaces at once. Also plots said collections' prices for better statistical analysis.

## Setup ##
(This guide assumes the bot is being hosted on a server)

1. Install requirements via `make install` or `pip3 install -r requirements.txt`
2. (If you haven't) Create a Telegram Bot https://core.telegram.org/bots#3-how-do-i-create-a-bot
3. Create an env file with the Telegram Bot API key: `echo "TOKEN=<BOT_TOKEN>" >> config.env`
4. Test installation via `make start`


This project has NOT been daemonized yet. If needed, make a PR to change that. Otherwise use [$nohup](https://stackoverflow.com/questions/2975624/how-to-run-a-python-script-in-the-background-even-after-i-logout-ssh) or [screen](https://linuxize.com/post/how-to-use-linux-screen/).

```sh
# Screen guide 
screen -dmS bot
screen -r bot
make start
```

## License ##
Yada yada it's all open source