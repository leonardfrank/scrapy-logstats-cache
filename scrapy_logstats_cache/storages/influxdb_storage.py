import logging

from influxdb import InfluxDBClient
from scrapy.settings import Settings
from scrapy.spider import Spider

logger = logging.getLogger(__name__)


class InfluxDBCacheStorage:
    def __init__(self, settings: Settings):
        self.client = None
        self.dsn = settings.get('INFLUXDB_DSN')
        self.host = settings.get('INFLUXDB_HOST')
        self.port = settings.get('INFLUXDB_PORT')
        self.database = settings.get('INFLUXDB_DATABASE')

        self.measurement = settings.get('INFLUXDB_MEASUREMENT')

    def open_spider(self, spider: Spider):
        if self.dsn:
            client = InfluxDBClient.from_dsn(self.dsn)
        else:
            client = InfluxDBClient(self.host, self.port, self.database)
        databases = set(i['name'] for i in client.get_list_database())
        if self.database not in databases:
            client.create_database(self.database)
        client.switch_database(self.database)
        self.client = client

        logger.debug('Using InfluxDB cache storage', extra={'spider': spider})

    def close_spider(self, spider: Spider):
        logger.debug('Closing InfluxDB cache storage', extra={'spider': spider})
        self.client.close()

    def store_log(self, log_data):
        points = [{'measurement': self.measurement, **log_data}]
        self.client.write_points(points)
