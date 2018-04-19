import logging
from datetime import datetime

from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured
from scrapy.settings import SETTINGS_PRIORITIES
from scrapy.settings import Settings
from scrapy.signals import spider_closed
from scrapy.signals import spider_opened
from scrapy.spiders import Spider
from scrapy.utils.misc import load_object
from twisted.internet import task

from ..settings import default_settings
from ..storages.influxdb_storage import InfluxDBCacheStorage
from ..utils import unfreeze_settings

logger = logging.getLogger(__name__)


class LogStatsCache:
    """Log basic scraping stats periodically"""

    def __init__(self, settings: Settings, stats, interval: float = 60.0):
        self.stats = stats
        self.interval: float = interval
        self.multiplier: float = 60.0 / self.interval
        self.task = None

        with unfreeze_settings(settings) as settings:
            settings.setmodule(
                module=default_settings,
                priority=SETTINGS_PRIORITIES['default'])

        storage_cls = load_object(settings['LOGSTATS_CACHE_STORAGE'])
        self.storage: InfluxDBCacheStorage = storage_cls(settings)

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        settings = crawler.settings
        stats = crawler.stats

        if any((not settings.getbool('LOGSTATS_CACHE_ENABLED'),
                not settings.get('LOGSTATS_CACHE_INTERVAL'),
                not settings.get('LOGSTATS_CACHE_STORAGE'))):
            raise NotConfigured

        interval = settings.getfloat('LOGSTATS_CACHE_INTERVAL')
        obj = cls(settings, stats, interval)

        crawler.signals.connect(obj.spider_opened, signal=spider_opened)
        crawler.signals.connect(obj.spider_closed, signal=spider_closed)
        return obj

    def spider_opened(self, spider: Spider):
        self.pagesprev = 0
        self.itemsprev = 0

        self.storage.open_spider(spider)

        self.task = task.LoopingCall(self.log, spider)
        self.task.start(self.interval)

    def log(self, spider: Spider):
        items = self.stats.get_value('item_scraped_count', 0)
        pages = self.stats.get_value('response_received_count', 0)

        irate = (items - self.itemsprev) * self.multiplier
        prate = (pages - self.pagesprev) * self.multiplier

        self.pagesprev, self.itemsprev = pages, items

        msg = ("Crawled %(pages)d pages (at %(pagerate)d pages/min), "
               "scraped %(items)d items (at %(itemrate)d items/min)")
        log_args = {'pages': pages, 'pagerate': prate,
                    'items': items, 'itemrate': irate}
        logger.info(msg, log_args, extra={'spider': spider})

        ts = datetime.utcnow().isoformat()

        log_data = {
            'tags': {'spider': spider.name},
            'time': ts,
            'fields': log_args
        }

        self.storage.store_log(log_data)

    def spider_closed(self, spider: Spider):
        if self.task and self.task.running:
            self.storage.close_spider(spider)
            self.task.stop()
