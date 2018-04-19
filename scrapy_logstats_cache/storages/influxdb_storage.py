import logging

from influxdb import InfluxDBClient
from scrapy.settings import Settings
from scrapy.spiders import Spider
from twisted.internet import task

from ..utils import is_version

logger = logging.getLogger(__name__)


class InfluxDBCacheStorage:
    def __init__(self, settings: Settings):
        self.client = None
        self.task = None
        self.logs_buffer = []
        self.dsn = settings.get('LOGSTATSCACHE_INFLUXDB_DSN')
        self.host = settings.get('LOGSTATSCACHE_INFLUXDB_HOST')
        self.port = settings.get('LOGSTATSCACHE_INFLUXDB_PORT')
        self.database = settings.get('LOGSTATSCACHE_INFLUXDB_DATABASE')
        self.measurement = settings.get('LOGSTATSCACHE_INFLUXDB_MEASUREMENT')
        self.interval = settings.getfloat('LOGSTATS_CACHE_INTERVAL') * 30

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

    def store_log(self, log_data: dict):
        if len(self.logs_buffer) > 100:
            self.store_buffer(self.logs_buffer)
        else:
            self._store_log(log_data)

    def store_buffer(self, logs_buffer: list):
        for item in logs_buffer:
            self._store_log(item)

    def _store_log(self, log_data: dict):
        points = [{'measurement': self.measurement, **log_data}]
        try:
            self.client.write_points(points)
        except Exception as exc:
            logger.info('An exception occurred when caching '
                        'logstats to InfluxDB: {}'.format(exc))
            self.logs_buffer.append(points)

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
            logger.debug(
                "Reconnect to InfluxDB: {}".format(self.client._baseurl))
        else:
            logger.debug(
                "Keep connecting to InfluxDB: {}".format(self.client._baseurl))

    @property
    def is_connected(self) -> bool:
        if self.client:
            result = self.client.ping()
            return is_version(result)
        return False
