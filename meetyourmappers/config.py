OVERPASS_API_URL = 'https://overpass-api.de/api/interpreter'
OVERPASS_MAP_QUERY = '(node(area:{});<;);(._;>;);out meta;'
# filesystem path to store XML files that folks want to download
DATA_DIR = '/var/www/data'
# web server alias to the above file system path
DATA_ALIAS = '/download'
LOG_FILE = '/var/log/meetyourmappers/requests.log'
TEST_DATA = 'testdata/Buncombe.xml'

SECRET_KEY = 'owfoiwnef aiefliuaehlifamewlfihaeilw '
DEBUG = False
