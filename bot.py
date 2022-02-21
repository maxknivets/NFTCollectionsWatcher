import os
import logging


from telegram.ext import (
  Updater,
  CommandHandler,
)
from src.watcher import search_collections_and_start_watchers


logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
watchers = {}


def help(update, context):
  update.effective_chat.send_message("""
This bot currently supports 5 platforms: Magic Eden, DigitalEyes, Solanart, FTX US, and Alpha Art.
Keep in mind that not every marketplace supports each NFT collection available.
/add to add a collection to monitor.
/addmanually to add a colleciton manually. You'll have to specify the name for each platform.
/addsolfloor to use add the collection on solfloor. Good for tracking popular collections. Their APIs update prices hourly.
/remove to remove a colleciton.
/list to view collections.
/setinterval to change the polling frequency in seconds.
/setplottingdelay to change the frequency of plot creation.
/setmessagedelay to change the frequency of message sending.
/checknow to send the collection floor message instantly
/plotnow to plot collection history instantly
  """)


def add_collection(update, context):
  if len(context.args) == 0:
    update.effective_chat.send_message("Usage: /add <NFT Collection Name> ")
    return
  
  if not watchers.get(" ".join(context.args).lower()): 
    update.effective_chat.send_message("Browsing through NFT collections...")
    search_collections_and_start_watchers(update, context, watchers, " ".join(context.args))
  else:
    update.effective_chat.send_message("Collection already added")


def add_collection_manually(update, context):
  if len(context.args) == 0:
    update.effective_chat.send_message("""
Usage: /addmanual <NFT Collection Name>:<NFT Collection Name>:<NFT Collection Name>:<NFT Collection Name>:<NFT Collection Name>
Order: Magic Eden, Digital Eyes, Solanart, FTX US, Alpha Art
If you don't want to add a certain marketplace, just add it as a "-".
""")
    return
  if not watchers.get(" ".join(context.args).lower()): 
    marketplaces = []
    for collection in " ".join(context.args).lower().split(":"):
      if collection.replace(" ", "") == '-': continue
      marketplaces.append(collection)
    update.effective_chat.send_message("Browsing through NFT collections...")
    search_collections_and_start_watchers(update, context, watchers, None, marketplaces)
  else:
    update.effective_chat.send_message("Collection already added")


def add_sol_floor(update, context):
  if len(context.args) == 0:
    update.effective_chat.send_message("Usage: /add <NFT Collection Name> ")
    return

  if not watchers.get(" ".join(context.args).lower()): 
    update.effective_chat.send_message("Browsing through NFT collections...")
    search_collections_and_start_watchers(update, context, watchers, " ".join(context.args), None, True)
  else:
    update.effective_chat.send_message("Collection already added")


def list_collections(update, context):
  collections = "Available collections: \n"
  for key, _ in watchers.items():
    collections += key + '\n'
  update.effective_chat.send_message(collections)


def remove_collection(update, context):
  if len(context.args) == 0:
    update.effective_chat.send_message("Usage: /remove <NFT Collection Name>. To view collections use /list.")
  else:
    collection_name = " ".join(context.args).lower()
    if watchers.get(collection_name):
      collection = watchers[collection_name]
      collection.watcher_stopped = True
      del watchers[collection_name]
      update.effective_chat.send_message(f"{collection_name} collection removed")
    else:
      update.effective_chat.send_message(f"{collection_name} collection is not being watched")


def set_interval(update, context):
  if len(context.args) == 0:
    update.effective_chat.send_message(f"Usage: /setinterval <seconds>")
  else:
    for key, cw in watchers.items():
      cw.default_interval = int(context.args[0])
    update.effective_chat.send_message(f"Checkup interval for all watchers set to {context.args[0]} seconds")


def set_plotting_delay(update, context):
  if len(context.args) == 0:
    update.effective_chat.send_message(f"Usage: /setplottingdelay <minutes>")
  else:
    for key, cw in watchers.items():
      cw.plotting_delay = int(context.args[0])
    update.effective_chat.send_message(f"Plotting interval for all watchers set to {context.args[0]} minutes")


def set_message_delay(update, context):
  if len(context.args) == 0:
    update.effective_chat.send_message(f"Usage: /setmessagedelay <minutes>")
  else:
    for key, cw in watchers.items():
      cw.message_delay = int(context.args[0])
    update.effective_chat.send_message(f"Message delay for all watchers set to {context.args[0]} minutes")


def check_now(update, context):
  if len(context.args) == 0:
    update.effective_chat.send_message("Usage: /checknow <NFT Collection Name>")
  else:
    watcher = watchers.get(" ".join(context.args).lower())
    if watcher:
      message = watcher.prepare_message()
      if message:
        update.effective_chat.send_message(message)
      else:
        logger.error('no message to be prepared')
    else:
      logger.error('no watcher found')


def plot_now(update, context):
  if len(context.args) == 0:
    update.effective_chat.send_message("Usage: /plotnow <NFT Collection Name>")
  else:
    watcher = watchers.get(" ".join(context.args).lower())
    if watcher:
      watcher.plot(update, context)


def main():
  updater = Updater(os.environ.get('TOKEN'))

  dispatcher = updater.dispatcher

  dispatcher.add_handler(CommandHandler("start", help))
  dispatcher.add_handler(CommandHandler("help", help))
  dispatcher.add_handler(CommandHandler("add", add_collection))
  dispatcher.add_handler(CommandHandler("addmanual", add_collection_manually))
  dispatcher.add_handler(CommandHandler("addsolfloor", add_sol_floor))
  dispatcher.add_handler(CommandHandler("list", list_collections))
  dispatcher.add_handler(CommandHandler("remove", remove_collection))
  dispatcher.add_handler(CommandHandler("setinterval", set_interval))
  dispatcher.add_handler(CommandHandler("setplottingdelay", set_plotting_delay))
  dispatcher.add_handler(CommandHandler("setmessagedelay", set_message_delay))
  dispatcher.add_handler(CommandHandler("checknow", check_now))
  dispatcher.add_handler(CommandHandler("plotnow", plot_now))
  dispatcher.add_handler(CommandHandler("untilnext", set_message_delay))

  # dispatcher.add_handler(CommandHandler("collection"), collection)
  # conv_handler = ConversationHandler(
  #     entry_points=[CommandHandler('collection', )],
  #     states={
  #         BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
  #         BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
  #         BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
  #     },
  #     fallbacks=[CommandHandler('cancel', cancel)],
  # )
  updater.start_polling()
  updater.idle()


if __name__ == '__main__':
  main()