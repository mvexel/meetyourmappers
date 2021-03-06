from meetyourmappers import app
from flask import render_template, request, jsonify, session
from uuid import uuid4
import requests
import tempfile
import os
from meetyourmappers import osm
import logging
import shutil

OVERPASS_AREA_BASE = 3600000000
OSM_FILE_PATH_KEY = 'osm_file_path'

OVERPASS_REL_QUERY = '(node(area:{});<;);(._;>;);out meta;'
OVERPASS_BOX_QUERY = '(node({s}, {w}, {n}, {e});<;);(._;>;);out meta;'

logging.basicConfig(
    filename=app.config['LOG_FILE'],
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)

logger = logging.getLogger()


@app.route('/', methods=['get'])
def index():
    session['uid'] = str(uuid4())
    test_data = app.config['TEST_DATA']
    if app.debug:
        session[OSM_FILE_PATH_KEY] = test_data
    return render_template(
        'index.html', debug=app.debug,
        has_testdata=os.path.exists(test_data))


@app.route('/about', methods=['get'])
def about():
    return render_template('about.html', debug=app.debug)


@app.route('/get_rel/<relation_id>', methods=['get'])
def get_area(relation_id):
    session[OSM_FILE_PATH_KEY] = os.path.join(
        tempfile.gettempdir(),
        session['uid'] + '.xml')
    q = app.config['OVERPASS_MAP_QUERY'].format(
        int(relation_id) + OVERPASS_AREA_BASE)
    resp = requests.post(
        app.config['OVERPASS_API_URL'],
        data=q)
    with open(session[OSM_FILE_PATH_KEY], 'wb') as fh:
        for block in resp.iter_content(1024):
            fh.write(block)
    logging.info("\t".join([relation_id, str(len(resp.content))]))
    return jsonify({
        'file': session[OSM_FILE_PATH_KEY],
        'size': len(resp.content)})


@app.route('/get_box/', methods=['get'])
def get_box():
    overpass_endpoint = request.args.get('server')
    n = request.args.get('n')
    s = request.args.get('s')
    e = request.args.get('e')
    w = request.args.get('w')
    session['osm_file_path'] = os.path.join(
        tempfile.gettempdir(),
        session['uid'] + '.xml')
    q = OVERPASS_BOX_QUERY.format(n=n, s=s, e=e, w=w)
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
    h.apply_file(session[OSM_FILE_PATH_KEY])
    if save_for_download:
        download_filename = str(uuid4()) + '.osm.xml'
        saved_file_path = os.path.join(
            app.config['DATA_DIR'],
            download_filename)
        shutil.move(session[OSM_FILE_PATH_KEY], saved_file_path)
    elif not app.debug:
        logging.info("Removing temp file: {}".format(
            session[OSM_FILE_PATH_KEY]))
        os.remove(session[OSM_FILE_PATH_KEY])
    return jsonify({
        'totals': h.totals,
        'users': h.users,
        'file': os.path.join(app.config['DATA_ALIAS'], download_filename)})
