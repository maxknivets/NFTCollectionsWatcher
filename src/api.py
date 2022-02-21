import requests
import logging
import time
from .marketplace import Marketplace

logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


class SolanaFloorAPI(Marketplace):

  def __init__(self, *args, **kwargs):
    super(SolanaFloorAPI, self).__init__(*args, **kwargs)
    self.find_collection()

  def find_collection(self):
    if self.collection_exists: return self.collection_official_name
    collections = requests.post("https://api.solanafloor.com/collections").json()
    for collection in collections:
      if self.collection_name == collection['name']:
        self.ensure_collection_existance(collection['name'], collection['name'])
        logger.info(f"found {self.collection_official_name} on {self.marketplace_name}")
        return self.collection_official_name
    return

  def update_floor_prices(self, timeout=5):
    try:
      collections = requests.post("https://api.solanafloor.com/collections").json()
      for collection in collections:
        if self.collection_name == collection['name']:
          self.previous_price = self.current_price
          self.current_price = collection['tokenFloor']
    except:
      logger.error(f'{self.marketplace_name} timed out')
      time.sleep(timeout)
      self.update_floor_prices(timeout*2)

  @property
  def marketplace_name(self):
    return "Solana Floor"


class MagicEdenAPI(Marketplace):
  def __init__(self, *args, **kwargs):
    super(MagicEdenAPI, self).__init__(*args, **kwargs)
    self.find_collection()

  def find_collection(self):
    if self.collection_exists: return self.collection_official_name
    collection_name = self.collection_name.replace(" ", "_").lower()
    try:
      all_collections = requests.get("https://api-mainnet.magiceden.io/all_collections").json()
      for collection in all_collections['collections']:
        if not self.auto_detect and collection_name == collection['symbol'].lower():
          self.ensure_collection_existance(collection['symbol'].lower(), collection['name'])
          logger.info(f"found {self.collection_official_name} on {self.marketplace_name}")
          return self.collection_official_name
        elif collection_name == collection['symbol'].lower() or collection['symbol'] in collection_name or collection_name in collection['symbol']:
          self.ensure_collection_existance(collection['symbol'].lower(), collection['name'])
          logger.info(f"found {self.collection_official_name} on {self.marketplace_name}")
          return self.collection_official_name
      return None
    except:
      return None

  def get_listings(self, timeout=5, query=5):
    query = '{"$match":{"collectionSymbol": ' + f'"{self.collection_name}"' + '},"$sort":{"takerAmount":1,"createdAt":-1},"$skip":0,"$limit":'+ str(query) + '}'
    try:
      listings = requests.get(f'https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q={query}').json().get('results')
      self.listings_cache = listings
      return listings
    except:
      logger.error(f'{self.marketplace_name} timed out')
      time.sleep(timeout)
      self.get_listings(timeout*2)

  def get_floor_info(self):
    return self.listings_cache[0]

  @property
  def floor_price(self):
    return self.listings_cache[0]['price']

  @property
  def marketplace_name(self):
    return "Magic Eden"


class DigitalEyesAPI(Marketplace):
  def __init__(self, *args, **kwargs):
    super(DigitalEyesAPI, self).__init__(*args, **kwargs)
    self.find_collection()

  def find_collection(self):
    if self.collection_exists: return self.collection_official_name
    try:
      all_collections = requests.get("https://us-central1-digitaleyes-prod.cloudfunctions.net/collection-retriever").json()
      for collection in all_collections:
        if not self.auto_detect and self.collection_name.lower() == collection['name'].lower():
          self.ensure_collection_existance(collection['name'].replace(" ", "%20"), collection['name'])
          logger.info(f"found {self.collection_official_name} on {self.marketplace_name}")
          return self.collection_official_name
        elif collection['name'].lower() in self.collection_name.lower() or self.collection_name.lower() in collection['name'].lower():
          self.ensure_collection_existance(collection['name'].replace(" ", "%20"), collection['name'])
          logger.info(f"found {self.collection_official_name} on {self.marketplace_name}")
          return self.collection_official_name
      return None
    except:
      return None

  def get_listings(self, timeout=5):
    try:
      listings = requests.get(f"https://us-central1-digitaleyes-prod.cloudfunctions.net/offers-retriever?collection={self.collection_name}&price=asc").json()['offers']
      self.listings_cache = listings
      return listings
    except:
      logger.error(f'{self.marketplace_name} timed out')
      time.sleep(timeout)
      self.get_listings(timeout*2)

  def get_floor_info(self):
    return self.listings_cache[0]

  @property
  def floor_price(self):
    return self.listings_cache[0]['price'] / 10**9

  @property
  def marketplace_name(self):
    return "Digital Eyes"


class SolanartAPI(Marketplace):
  def __init__(self, *args, **kwargs):
    super(SolanartAPI, self).__init__(*args, **kwargs)
    self.find_collection()

  def find_collection(self):
    if self.collection_exists: return self.collection_official_name
    try:
      all_collections = requests.get("https://qzlsklfacc.medianetwork.cloud/query_volume_all").json()
      collection_name = self.collection_name.replace(" ", "").lower()
      for collection in all_collections:
        if not self.auto_detect and collection_name == collection['collection']:
          self.ensure_collection_existance(collection['collection'], collection['collection'])
          logger.info(f"found {self.collection_official_name} on {self.marketplace_name}")
          return self.collection_name
        elif collection['collection'] in collection_name or collection_name in collection['collection']:
          self.ensure_collection_existance(collection['collection'], collection['collection'])
          logger.info(f"found {self.collection_official_name} on {self.marketplace_name}")
          return self.collection_name
      return None
    except:
      return None

  def get_listings(self, timeout=5):
    try:
      listings = requests.get(f'https://qzlsklfacc.medianetwork.cloud/nft_for_sale?collection={self.collection_name}').json()
      self.listings_cache = listings
      return listings
    except:
      logger.error(f'{self.marketplace_name} timed out')
      time.sleep(timeout)
      self.get_listings(timeout*2)

  def get_floor_info(self):
    return self.listings_cache[0]

  @property
  def floor_price(self):
    return self.listings_cache[0]['price']

  @property
  def marketplace_name(self):
    return "Solanart"


class AlphaArtAPI(Marketplace):
  def __init__(self, *args, **kwargs):
    super(AlphaArtAPI, self).__init__(*args, **kwargs)
    self.find_collection()

  def find_collection(self):
    if self.collection_exists: return self.collection_official_name
    try:
      all_collections = requests.get("https://apis.alpha.art/api/v1/collections?order=recent&strip=1&n=9999").json()
      collection_name = self.collection_name.replace(" ", "-").lower()
      for collection in all_collections['collections']:
        if not self.auto_detect and collection_name == collection['slug']:
          self.ensure_collection_existance(collection['slug'], collection['title'])
          logger.info(f"found {self.collection_official_name} on {self.marketplace_name}")
          return self.collection_name
        if collection_name == collection['slug'] or collection['slug'] in collection_name or collection_name in collection['slug']:
          self.ensure_collection_existance(collection['slug'], collection['title'])
          logger.info(f"found {self.collection_official_name} on {self.marketplace_name}")
          return self.collection_name
      return None
    except:
      return None

  def get_listings(self, timeout=5):
    data = '{"collectionId": "' + self.collection_name +'", "orderBy": "PRICE_LOW_TO_HIGH", "status": ["BUY_NOW"],"traits": []}'
    try:
      listings = requests.post(f'https://apis.alpha.art/api/v1/collection', data=str(data)).json()['tokens']
      self.listings_cache = listings
      return listings
    except:
      logger.error(f'{self.marketplace_name} timed out')
      time.sleep(timeout)
      self.get_listings(timeout*2)

  def get_floor_info(self):
    return self.listings_cache[0]

  @property
  def floor_price(self):
    return int(self.listings_cache[0]['price']) / 10**9

  @property
  def marketplace_name(self):
    return "Alpha Art"


class FTXAPI(Marketplace):
  def __init__(self, *args, **kwargs):
    super(FTXAPI, self).__init__(*args, **kwargs)
    self.find_collection()

  def find_collection(self):
    if self.collection_exists: return self.collection_official_name
    try:
      collection_name = self.collection_name
      collection_name = collection_name.replace(" ", "%20")
      if not self.auto_detect:
        collection = requests.get(f"https://ftx.us/api/nft/collection/{collection_name}").json()['result']
        if collection['floor_price'] or collection['total']:
          self.ensure_collection_existance(collection_name, collection['collection'])
          logger.info(f"found {self.collection_official_name} on {self.marketplace_name}")
          return self.collection_name
      else:
        all_collections = requests.get(f"https://ftx.us/api/nft/search_groups").json()['result']
        collection_name = self.collection_name

        for collection in all_collections:
          if collection.get('collection'):
            if collection_name.lower() == collection['collection'].lower() or collection['collection'].lower() in collection_name.lower() or collection_name.lower() in collection['collection'].lower():
              self.ensure_collection_existance(collection['collection'].replace(" ", "%20"), collection['collection'])
              logger.info(f"found {self.collection_official_name} on {self.marketplace_name}")
              return self.collection_name
      return None
    except:
      logger.info('Something went wrong')
      return None

  def get_listings(self, timeout=5):
    try:
      listings = requests.get(f"""
https://ftx.us/api/nft/nfts_filtered?startInclusive=0&endExclusive=10000000&nft_filter_string=%7B%22collection%22%3A%22{self.collection_name}%22%2C%22nftAuctionFilter%22%3A%22all%22%2C%22minPriceFilter%22%3Anull%2C%22maxPriceFilter%22%3Anull%2C%22seriesFilter%22%3A%5B%5D%2C%22traitsFilter%22%3A%7B%7D%2C%22mintSourceFilter%22%3Anull%2C%22include_not_for_sale%22%3Atrue%7D&sortFunc=offer_asc
      """).json().get('result').get('nfts')
      self.listings_cache = listings
      return listings
    except:
      logger.error(f'{self.marketplace_name} timed out')
      time.sleep(timeout)
      self.get_listings(timeout*2)

  def get_floor_info(self):
    return self.listings_cache[0]

  @property
  def floor_price(self):
    return self.listings_cache[0]['offerPrice'] if self.listings_cache[0]['offerPrice'] else 0
  
  @property
  def marketplace_name(self):
    return "FTX"
