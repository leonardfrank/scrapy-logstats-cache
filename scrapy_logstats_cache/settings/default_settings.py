LOGSTATS_CACHE_ENABLED = True
LOGSTATS_CACHE_INTERVAL = 60  # 60s

# ------------------------------------------------------------------------------
# InfluxDB Logstats Storage
# ------------------------------------------------------------------------------
LOGSTATSCACHE_INFLUXDB_STORAGE = 'scrapy_logstats_cache.storages.influxdb_storage.InfluxDBCacheStorage'
LOGSTATSCACHE_INFLUXDB_DSN = None
LOGSTATSCACHE_INFLUXDB_HOST = 'localhost'
LOGSTATSCACHE_INFLUXDB_PORT = 8086
LOGSTATSCACHE_INFLUXDB_DATABASE = 'scrapy'
LOGSTATSCACHE_INFLUXDB_MEASUREMENT = 'spider'
# LOGSTATSCACHE_INFLUXDB_USERNAME = 'username'
# LOGSTATSCACHE_INFLUXDB_PASSWORD = 'password'

# ------------------------------------------------------------------------------
# OTHERDB Logstats Storage TO BE ADDED
# ------------------------------------------------------------------------------


LOGSTATS_CACHE_STORAGE = LOGSTATSCACHE_INFLUXDB_STORAGE
