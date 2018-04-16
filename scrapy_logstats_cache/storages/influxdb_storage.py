import logging

from influxdb import InfluxDBClient
from scrapy.settings import Settings
from scrapy.spider import Spider
from twisted.internet import task

logger = logging.getLogger(__name__)


class InfluxDBCacheStorage:
    def __init__(self, settings: Settings):
        self.client = None
        self.dsn = settings.get('INFLUXDB_DSN')
        self.host = settings.get('INFLUXDB_HOST')
        self.port = settings.get('INFLUXDB_PORT')
        self.database = settings.get('INFLUXDB_DATABASE')
        self.measurement = settings.get('INFLUXDB_MEASUREMENT')
        self.interval = settings.getfloat('LOGSTATS_CACHE_INTERVAL') * 30
        # self.interval = settings.getfloat('LOGSTATS_CACHE_INTERVAL') * 3
        self.task = None

        self.logs_buffer = []

    def open_spider(self, spider: Spider):
        self.task = task.LoopingCall(self.get_client)
        self.task.start(self.interval)

        logger.debug('Using InfluxDB cache storage', extra={'spider': spider})

    def close_spider(self, spider: Spider):
        if self.task and self.task.running:
            self.store_buffer(self.logs_buffer)
            self.task.stop()
            logger.debug('Closing InfluxDB cache storage',
                         extra={'spider': spider})
            self.client.close()

    def store_log(self, log_data):
        if len(self.logs_buffer) > 100:
            self.store_buffer(self.logs_buffer)
        else:
            self._store_log(log_data)

    def store_buffer(self, logs_buffer):
        for item in logs_buffer:
            self.store_log(item)

    def _store_log(self, log_data):
        points = [{'measurement': self.measurement, **log_data}]
        try:
            result = self.client.write_points(points)
        except Exception as exc:
            logger.debug('{} happened when caching logstats to InfluxDB')
            self.logs_buffer.append(points)
        finally:
            return result

    def get_client(self):
        if not self.is_connected:
            if self.dsn:
                client = InfluxDBClient.from_dsn(self.dsn)
            else:
                client = InfluxDBClient(self.host, self.port, self.database)
            databases = set(i['name'] for i in client.get_list_database())
            if self.database not in databases:
                client.create_database(self.database)
            client.switch_database(self.database)
            self.client = client
            logger.info(
                "Reconnect to InfluxDB: {}".format(self.client._baseurl))
        else:
            logger.info(
                "Keep connecting to InfluxDB: {}".format(self.client._baseurl))

    @property
    def is_connected(self):
        if self.client:
            return self.client.ping()
        else:
            return False
