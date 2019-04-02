# Main Overpass API URL
OVERPASS_API_URL = 'https://overpass-api.de/api/interpreter'

# Overpass query templates
OVERPASS_MAP_QUERY = '(node(area:{});<;);(._;>;);out meta;'
OVERPASS_BOX_QUERY = '(node({s}, {w}, {n}, {e});<;);(._;>;);out meta;'

# Filesystem path to store XML files that folks want to download
DATA_DIR = '/tmp/data'

# Web server alias to the above file system path
DATA_ALIAS = '/download'
LOG_FILE = '/tmp/requests.log'
TEST_DATA = 'testdata/Buncombe.xml'

# Secret key, change me
SECRET_KEY = 'OVERRIDE ME WITH AN ENVVAR'

# debug mode
DEBUG = False
