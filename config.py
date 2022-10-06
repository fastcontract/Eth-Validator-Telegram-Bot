VALIDATORS = [X,X,X,X,X,X]
BOT_TOKEN = ""
CHAT_ID = XXXXXXXXXX
BEACON_API = ""

#I recommend setting the notify threshold higher than 2.
#Sometimes the beacon API doesnt update fast enough on a new epoch and marks a validator as missed.
#It then later updates it the next epoch when it was a successful attestation.
#That is why the beaconchain website actually lags 1 epoch behind when displaying attestations.
NOTIFY_ON_SEQ_MISSES = 3
