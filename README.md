# NFTCollectionsWatcher #

A Telegram bot that watches over an NFT collection on several marketplaces at once. Also plots said collections' prices for better statistical analysis.
Fair bit of warning, the project is at least 4 months old. Some of the APIs might not work (SolanaFloor.com still works though).

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

## Using the bot ##
To start using the bot, just send it a `/start` or `/help` message.
This bot currently supports 4 platforms: Magic Eden, DigitalEyes, Solanart, and Alpha Art.
Keep in mind that not every marketplace supports each NFT collection available.

Here's a list of currently supported commands:
`/add` to add a collection to monitor.
`/addmanually` to add a colleciton manually. You'll have to specify the name for each platform.
`/addsolfloor` to add the collection on solanafloor. Good for tracking popular collections. Their APIs update prices hourly.
`/remove` to remove a colleciton.
`/list` to view collections.
`/setinterval` to change the polling frequency in seconds.
`/setplottingdelay` to change the frequency of plot creation.
`/setmessagedelay` to change the frequency of message sending.
`/checknow` to send the collection floor message instantly
`/plotnow` to plot collection history instantly

## License ##
Yada yada it's all open source

## PRs are welcome! ##