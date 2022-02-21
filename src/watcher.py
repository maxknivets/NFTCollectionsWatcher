import time
import logging
import threading
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from .constants import DEFAULT_INTERVAL, DEFAULT_PLOT_DELAY, DEFAULT_MESSAGE_DELAY
from .api import SolanaFloorAPI, MagicEdenAPI, DigitalEyesAPI, SolanartAPI, FTXAPI, AlphaArtAPI


logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def search_collections_and_start_watchers(update, context, watchers, collection_name, manual=[], solfloor=False):
  if solfloor:
    solanafloor = SolanaFloorAPI(collection_name=collection_name)
    if solanafloor.collection_exists:
      update.effective_chat.send_message(f"Found {collection_name} on Solana Floor.")
      cw = CollectionWatcher(solanafloor=solanafloor)
      cw.default_interval=600
      cw.start_collection_watcher(update, context)
      watchers[collection_name.lower()] = cw
      return
  found_marketplaces = ""
  marketplaces = {
    'Magic Eden': (MagicEdenAPI, 'magic_eden'),
    'Digital Eyes': (DigitalEyesAPI, 'digital_eyes'),
    'Solanart': (SolanartAPI, 'solanart'),
    # 'FTX': (FTXAPI, 'ftx'),
    'Alpha Art': (AlphaArtAPI, 'alpha_art'),
  }
  confirmed_marketplaces = {}
  cl = ""
  for idx, (key, marketplace) in enumerate(marketplaces.items()):
    name = marketplace[1]
    marketplace = marketplace[0](collection_name=collection_name or manual[idx])
    if marketplace.collection_exists:
      cl = marketplace.collection_official_name
      confirmed_marketplaces[name] = marketplace
      found_marketplaces += (f"Found {cl} on {marketplace.marketplace_name}. \n")
    else:
      confirmed_marketplaces[name] = None
  if not found_marketplaces:
    update.effective_chat.send_message("No collections found.")
  else:
    update.effective_chat.send_message(found_marketplaces)
    cw = CollectionWatcher(**confirmed_marketplaces)
    cw.start_collection_watcher(update, context)
    watchers[cl.lower()] = cw


class CollectionWatcher(object):
  def __init__(self, solanafloor=None, magic_eden=None, digital_eyes=None, solanart=None, ftx=None, alpha_art=None):
    self.run = False
    self.default_interval = DEFAULT_INTERVAL
    self.plotting_delay = DEFAULT_PLOT_DELAY
    self.message_delay = DEFAULT_MESSAGE_DELAY
    self.message_start_time = datetime.now() - timedelta(minutes=self.message_delay)
    self.plot_start_time = datetime.now()
    self.watcher_stopped = False
    self.solanafloor = solanafloor
    self.magic_eden = magic_eden
    self.digital_eyes = digital_eyes
    self.solanart = solanart
    self.ftx = None
    self.alpha_art = alpha_art
    self.marketplaces = [solanafloor, magic_eden, digital_eyes, solanart, ftx, alpha_art]

  def start_collection_watcher(self, update, context):
    thread = threading.Thread(target=self.watcher, args=(update, context))
    thread.daemon = True
    thread.start()

  def watcher(self, update, context):
    try:
      while True and not self.watcher_stopped:
        for marketplace in self.available_marketplaces: marketplace.update_floor_prices()
        if datetime.now() > self.message_start_time + timedelta(minutes=self.message_delay):
          if self.prepare_message():
            self.message_start_time = datetime.now()
            update.effective_chat.send_message(self.prepare_message())
        if datetime.now() > self.plot_start_time + timedelta(minutes=self.plotting_delay):
          self.plot_start_time = datetime.now()
          self.plot(update, context)
          for marketplace in self.available_marketplaces:
            marketplace.prices_history = []
        time.sleep(self.default_interval)
    except BaseException as e:
      logger.error(f"{self.available_marketplaces[0].collection_official_name} watcher stopped. Restarting in a minute. \n{e}")
      time.sleep(60)
      self.watcher(update, context)

  def prepare_message(self):
    try:
      cheapest_marketplace_price = min([marketplace.current_price for marketplace in self.available_marketplaces])
      for marketplace in self.available_marketplaces:
        m = marketplace
        if m.current_price != 0:
          m.prices_history.append({"price": m.current_price, "date": datetime.now()}) 
        if m.current_price != cheapest_marketplace_price:
          continue
        if m.current_price != m.previous_price and m.current_price != 0:
          change_is_positive = True if m.current_price > m.previous_price else False
          change_sign = "📈" if change_is_positive else "📉"
          sign = "+" if change_is_positive else ""
          percentage = ((m.current_price - m.previous_price) / m.current_price) * 100
          return f'{change_sign} {m.collection_official_name}: {m.previous_price} -> {m.current_price} ({sign}{round(percentage, 2)}%) ({m.marketplace_name})'
    except BaseException as e:
      logger.error(f"{e}")
      return

  def plot(self, update, context):
    for marketplace in self.available_marketplaces:
      x = [date["date"] for date in marketplace.prices_history]
      y = [date["price"] for date in marketplace.prices_history]
      plt.plot(x, y)
    plt.title(self.available_marketplaces[0].collection_official_name)
    plt.legend([marketplace.marketplace_name for marketplace in self.available_marketplaces])
    plt.savefig('foo.png')
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id, photo=open('foo.png', 'rb'))
    plt.clf()

  @property
  def available_marketplaces(self):
    return list(filter(None, self.marketplaces))
