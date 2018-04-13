import logging
from scrapy.spider import Spider
from scrapy.settings import Settings
from influxdb import InfluxDBClient

logger = logging.getLogger(__name__)


class InfluxDBCacheStorage:
    def __init__(self, setttings: Settings):
        self.client = None
        self.dsn = setttings.get('INFLUXDB_DSN')
        self.host = setttings.get('INFLUXDB_HOST')
        self.port = setttings.get('INFLUXDB_PORT')
        self.database = setttings.get('INFLUXDB_DATABASE')

        self.measurement = setttings.get('INFLUXDB_MEASUREMENT')

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
