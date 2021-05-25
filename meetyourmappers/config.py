"""Configuration"""

# Overpass API URLs
OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
ALT_OVERPASS_API_URL = "https://overpass.kumi.systems/api/interpreter"

# Overpass query templates
OVERPASS_REL_QUERY = """[out:csv(::type,::user,::uid,::version,::timestamp;false;",")];
area({osmid});
out meta;<;out meta;<;out meta;"""
OVERPASS_BOX_QUERY = """[bbox:{s},{w},{n},{e}][out:csv(::type,::user,::uid,::version,::timestamp;false;",")];
node;out meta;<;out meta;<;out meta;"""

# Filesystem path to store CSV files that folks want to download
DATA_DIR = "/tmp/data"

# Web server alias to the above file system path
DATA_ALIAS = "/download"

# Log file path
LOG_FILE = "log/requests.log"

TEST_DATA = "test/sample.csv"

# Secret key, change me
SECRET_KEY = "OVERRIDE ME WITH AN ENVVAR"

# debug mode
DEBUG = False
