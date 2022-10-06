# Eth-Validator-Telegram-Bot
This bot watches validators and notifies the user via Telegram when misses happen. I got sick of the beaconchain app notifications - I do a lot in telegram already, and I wanted to only be notified if >1 attestation was missed. 1 is no big deal, more than 1 is likely an issue. This bot as a limit of 100 validators due to the beaconcha.in api.



Make sure to modify each setting in config.py.

First message botfather: https://telegram.me/botfather
Type /newbot and follow the prompts
Botfather will give you an HTTP API access token (adf42kjk4hj2khu42hkj:23jlh423jhkl42lkj432jlk) This is the BOT_TOKEN in config.py

Navigate to https://api.telegram.org/bot?????????????????:????????????????/getUpdates
Replace the ????:???? with your token
Message your bot and refresh the page. Data should shot up. Look for the Chat object and find the ID number. This is your CHAT_ID in config.py

For the BEACON_API, log in to a beaconcha.in account, and navigate to your settings>API to get your key.



I run the bot remotely on a free google cloud instance using these instructions:
(of course change the git clone address in the tutorial)

https://programmingforgood.medium.com/deploy-telegram-bot-on-google-cloud-platform-74f1f531f65e

I considered running it on my own machines, but if the internet goes out, that defeats the purpose!
You need python-telegram-bot which you can install with pip.



Bot usage (/help):
Type /start to start the monitoring bot.
Type /stop to stop the monitoring bot.
Type /report to see the total number of misses in the last 100 epochs.
Type /status to see when the last epoch data was imported.
