import logging

logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


class Marketplace(object):
  def __init__(self, collection_name="", auto_detect=True, stop=False):
    if collection_name:
      self.collection_name = collection_name
      self.collection_official_name = collection_name
      self.collection_exists = False
      self.previous_price = 0
      self.current_price = 0
      self.watcher_stopped = stop
      self.auto_detect = auto_detect
      self.listings_cache = []
      self.prices_history = []

  def ensure_collection_existance(self, collection_name, collection_official_name):
    self.collection_name = collection_name
    self.collection_official_name = collection_official_name
    self.collection_exists = True

  def update_floor_prices(self):
    self.get_listings()
    if self.floor_price > 0:
      self.previous_price = self.current_price
      self.current_price = self.floor_price
