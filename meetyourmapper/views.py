from meetyourmapper import app
from flask import render_template, request, jsonify, session
from uuid import uuid4
import requests
import tempfile
import os 
from meetyourmapper import osm

OVERPASS_AREA_BASE = 3600000000

overpass_api_url = 'https://overpass-api.de/api/interpreter'
overpass_map_query = '(node(area:{});<;);out meta;'

@app.route('/', methods=['get'])
def index():
	session['uid'] = str(uuid4())
	return render_template('index.html')

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

@app.route('/process/<relation_id>', methods=['get'])
def process_result(relation_id):
	print(session['osm_file_path'])
	h = osm.UserHandler()
	h.apply_file(session['osm_file_path'])
	os.remove(session['osm_file_path'])
	return jsonify(h.users)