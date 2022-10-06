#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from time import sleep
import json
from requests import get
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import VALIDATORS, NOTIFY_ON_SEQ_MISSES, BOT_TOKEN, CHAT_ID, BEACON_API


validators = VALIDATORS
id = CHAT_ID
current_epoch = -1
str_validators = [str(int) for int in validators]
flag = 1
timerun = 0

def callback_auto_message(context):
    """Start the main monitoring queue job"""
    global current_epoch
    global timerun
    url = "https://beaconcha.in/api/v1/validator/"+",".join(str_validators)+"/attestations?apikey="+BEACON_API
    propurl = "https://beaconcha.in/api/v1/validator/"+",".join(str_validators)+"/proposals?apikey="+BEACON_API
    req = get(url)
    u = json.loads(req.text)
    while current_epoch == u["data"][0]["epoch"] and flag == 1:
        sleep(60)
        req = get(url)
        u = json.loads(req.text)
        if current_epoch != u["data"][0]["epoch"]:
            continue
        elif flag == 0:
            return
    timerun = datetime.datetime.now()
    current_epoch = u["data"][0]["epoch"]   
    propreq = get(propurl)
    p = json.loads(propreq.text)

    checklen = len(validators) * NOTIFY_ON_SEQ_MISSES

    misslist = []
    for i in u["data"][:checklen]:
        if i["inclusionslot"] == 0:
            misslist.append(i["validatorindex"])

    brokenvalidators = list(set([x for x in misslist if misslist.count(x) > NOTIFY_ON_SEQ_MISSES-1]))
    
    if brokenvalidators:
        if len(brokenvalidators) > 5:
            context.bot.send_message(id, text="Validator(s) " + ",".join(map(str, brokenvalidators[:5])) + " (+" + str(len(brokenvalidators[:5])) +
                                     " more) missed " + str(NOTIFY_ON_SEQ_MISSES) + " attestations in a row @ epoch " + str(current_epoch) +
                                     " https://beaconcha.in/validator/" + str(brokenvalidators[0]))
        else:
            context.bot.send_message(id, text="Validator(s) " + ",".join(map(str, brokenvalidators)) + " missed " + str(NOTIFY_ON_SEQ_MISSES) +
                                     " attestations in a row @ epoch " + str(current_epoch) +
                                     " https://beaconcha.in/validator/" + str(brokenvalidators[0]))

    try:
        for prop in p["data"]:
            if prop["epoch"] == current_epoch and prop["exec_timestamp"]:
                context.bot.send_message(id, text="\U00002728 \U00002728 Validator " + str(prop["proposer"]) +
                                         " has proposed a new block! \U00002728 \U00002728 \nhttps://beaconcha.in/slot/" + str(prop["slot"]))
            elif prop["epoch"] == current_epoch and not prop["exec_timestamp"]:
                context.bot.send_message(id, text="\U0000203C \U0000203C VALIDATOR " + str(prop["proposer"]) +
                                         " MISSED A PROPOSAL \U0000203C \U0000203C \nhttps://beaconcha.in/slot/" + str(prop["slot"]))
    except:
        pass

        
def start_auto_messaging(update, context):
    """add queue job to check for missed attestations"""
    global flag
    flag = 1
    chat_id = id
    context.bot.send_message(chat_id=chat_id, text="Starting attestation monitoring!")
    context.job_queue.run_once(callback_auto_message, 1, context=chat_id, name=str(chat_id))
    context.job_queue.run_repeating(callback_auto_message, 360, context=chat_id, name=str(chat_id))


def stop_notify(update, context):
    """Stop the monitoring from running until started again"""
    global flag
    flag = 0
    chat_id = id
    context.bot.send_message(chat_id=chat_id, text="Stopping attestation monitoring!")
    job = context.job_queue.get_jobs_by_name(str(chat_id))
    job[0].schedule_removal()

    
def help(update, context):
    """Send a help message with all possible commands"""
    context.bot.send_message(id, text="Type /start to start the monitoring bot.\n"
                                        "Type /stop to stop the monitoring bot.\n"
                                        "Type /report to see the total number of misses in the last 100 epochs.\n"
                                        "Type /status to see when the last epoch data was imported.")


def report(update, context):
    """Send a message with the total number of misses in the last 100 epochs"""
    url1 = "https://beaconcha.in/api/v1/validator/"+",".join(str_validators)+"/attestations?apikey="+BEACON_API
    req1 = get(url1)
    u1 = json.loads(req1.text)
    misslistreport = []
    for i in u1["data"][len(validators):]:
        if i["inclusionslot"] == 0:
            misslistreport.append(i["validatorindex"])
    try:
        context.bot.send_message(id, text="In the last 100 epochs (about 10 hours) you've missed " +
                                 str(len(misslistreport)) + " attestations across all monitored validators, most recently " + str(misslistreport[0]) +
                                 " https://beaconcha.in/validator/" + str(misslistreport[0]))
    except:
        context.bot.send_message(id, text="No attestations have been missed in the last 100.")


def status(update, context):
    """Send a message with bot info"""
    try:
        now = datetime.datetime.now()
        elapsedTime = now - timerun
        diff = divmod(elapsedTime.total_seconds(), 60)
        if flag == 1:
            context.bot.send_message(id, text="The bot is currently STARTED\n" +
                                     "The last epoch imported was " + str(current_epoch) +
                                     "\nWhich was imported at " + str(timerun.strftime("%Y-%m-%d %I:%M:%S %p")) +
                                     "\nOr " + str(int(diff[0])) + " minutes and " + str(int(diff[1])) + " seconds ago.")
            
        else:
            context.bot.send_message(id, text="The bot is currently STOPPED\n" +
                                     "The last epoch imported was " + str(current_epoch) +
                                     "\nWhich was imported at " + str(timerun.strftime("%Y-%m-%d %I:%M:%S %p")) +
                                     "\nOr " + str(int(diff[0])) + " minutes and " + str(int(diff[1])) + " seconds ago.")
    except:
        context.bot.send_message(id, text="The bot hasn't imported anything yet!")


def main():
    """Start the bot"""
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_auto_messaging))
    dp.add_handler(CommandHandler("stop", stop_notify))
    dp.add_handler(CommandHandler("report", report))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("status", status))
    
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
