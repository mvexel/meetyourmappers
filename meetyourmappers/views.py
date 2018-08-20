from meetyourmappers import app
from flask import render_template, request, jsonify, session
from uuid import uuid4
import requests
import tempfile
import os
from meetyourmappers import osm
import logging

OVERPASS_AREA_BASE = 3600000000

overpass_api_url = 'https://overpass-api.de/api/interpreter'
overpass_rel_query = '(node(area:{});<;);(._;>;);out meta;'
overpass_box_query = '(node({s}, {w}, {n}, {e});<;);(._;>;);out meta;'
# filesystem path to store XML files that folks want to download
data_dir = '/var/www/data'
# web server alias to the above file system path
data_alias = '/download'
log_file = '/var/log/meetyourmappers/requests.log'

logging.basicConfig(
    filename=log_file,
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)

logger = logging.getLogger()


@app.route('/', methods=['get'])
def index():
    session['uid'] = str(uuid4())
    if app.debug:
        session['osm_file_path'] = 'testdata/Buncombe.xml'
    return render_template('index.html', debug=app.debug)


@app.route('/about', methods=['get'])
def about():
    return render_template('about.html', debug=app.debug)


@app.route('/get_rel/<relation_id>', methods=['get'])
def get_area(relation_id):
    overpass_endpoint = request.args.get('server')
    session['osm_file_path'] = os.path.join(
        tempfile.gettempdir(),
        session['uid'] + '.xml')
    q = overpass_rel_query.format(int(relation_id) + OVERPASS_AREA_BASE)
    resp = requests.post(
        overpass_endpoint,
        data=q)
    with open(session['osm_file_path'], 'wb') as fh:
        for block in resp.iter_content(1024):
            fh.write(block)
    logging.info("\t".join([relation_id, str(len(resp.content))]))
    return jsonify({
        'file': session['osm_file_path'],
        'size': len(resp.content)})


@app.route('/get_box', methods=['get'])
def get_box():
    overpass_endpoint = request.args.get('server')
    n = request.args.get('n')
    s = request.args.get('s')
    e = request.args.get('e')
    w = request.args.get('w')
    session['osm_file_path'] = os.path.join(
        tempfile.gettempdir(),
        session['uid'] + '.xml')
    q = overpass_box_query.format(n=n, s=s, e=e, w=w)
    resp = requests.post(
        overpass_endpoint,
        data=q)
    with open(session['osm_file_path'], 'wb') as fh:
        for block in resp.iter_content(1024):
            fh.write(block)
    logging.info("\t".join([n, s, e, w, str(len(resp.content))]))
    return jsonify({
        'file': session['osm_file_path'],
        'size': len(resp.content)})


@app.route('/process', methods=['get'])
def process_result():
    saved_file_path = ""
    download_filename = ""
    save_for_download = request.args.get('download') == '1'
    h = osm.UserHandler()
    h.apply_file(session['osm_file_path'])
    if save_for_download:
        download_filename = str(uuid4()) + '.osm.xml'
        saved_file_path = os.path.join(data_dir, download_filename)
        os.rename(session['osm_file_path'], saved_file_path)
    else:
        logging.info("Removing temp file: {}".format(session['osm_file_path']))
        os.remove(session['osm_file_path'])
    return jsonify({
        'totals': h.totals,
        'users': h.users,
        'file': os.path.join(data_alias, download_filename)})
