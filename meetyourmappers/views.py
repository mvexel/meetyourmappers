from meetyourmappers import app
from flask import render_template, request, jsonify, session
from uuid import uuid4
import requests
import tempfile
import os 
from meetyourmappers import osm
from uuid import uuid4

OVERPASS_AREA_BASE = 3600000000

overpass_api_url = 'https://overpass-api.de/api/interpreter'
overpass_map_query = '(node(area:{});<;);out meta;'
data_dir = '/var/www/meetyourmappers/data'  # filesystem path to store XML files that folks want to download, 
data_alias = '/download' # web server alias to the above file system path

@app.route('/', methods=['get'])
def index():
	session['uid'] = str(uuid4())
	if app.debug:
		session['osm_file_path'] = 'testdata/Buncombe.xml'
	return render_template('index.html', debug=app.debug)

@app.route('/retrieve/<relation_id>', methods=['get'])
def get_area(relation_id):	
	session['osm_file_path'] = os.path.join(tempfile.gettempdir(), session['uid'] + '.xml')
	q = overpass_map_query.format(int(relation_id) + OVERPASS_AREA_BASE)
	resp = requests.post(
		overpass_api_url,
		data=q)
	with open(session['osm_file_path'], 'wb') as fh:
		for block in resp.iter_content(1024):
			fh.write(block)
	return jsonify({
		'file': session['osm_file_path'],
		'size': len(resp.content)})

@app.route('/process', methods=['get'])
def process_result():
	saved_file_path = ""
	save_for_download = request.args.get('download') == '1'
	h = osm.UserHandler()
	h.apply_file(session['osm_file_path'])
	if save_for_download:
		saved_file_path = os.path.join(data_alias, (str(uuid4()) + '.osm.xml'))
		os.rename(session['osm_file_path'], saved_file_path)
	elif app.debug:
		os.remove(session['osm_file_path'])
	return jsonify({'totals': h.totals, 'users': h.users, 'file': saved_file_path})