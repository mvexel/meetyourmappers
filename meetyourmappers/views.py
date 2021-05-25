"""Flask views"""

from uuid import uuid4
import tempfile
import os
import logging
import shutil

import requests
from flask import render_template, request, jsonify, session

from meetyourmappers import app
from meetyourmappers.osm import MapperMetrics

OVERPASS_AREA_BASE = 3600000000

# Define logger
logging.basicConfig(
    filename=app.config["LOG_FILE"],
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.WARN)
logger = logging.getLogger()


@app.route("/", methods=["get"])
def index():
    """Main page view"""
    session["uid"] = str(uuid4())
    test_data = app.config["TEST_DATA"]
    if app.debug:
        session["result_file"] = test_data
    else:
        session["result_file"] = os.path.join(
            tempfile.gettempdir(),
            session["uid"] + ".csv")

    return render_template(
        "index.html", debug=app.debug,
        has_testdata=os.path.exists(test_data))


@app.route("/about", methods=["get"])
def about():
    """About view"""
    return render_template("about.html", debug=app.debug)


@app.route("/get_rel/<relation_id>", methods=["get"])
def get_area(relation_id):
    """Get data from Overpass based on relation id"""
    overpass_query = app.config["OVERPASS_REL_QUERY"].format(
        int(relation_id) + OVERPASS_AREA_BASE)
    resp = requests.post(
        app.config["OVERPASS_API_URL"],
        data=overpass_query)
    with open(session["result_file"], "wb") as file_handle:
        for block in resp.iter_content(1024):
            file_handle.write(block)
    logging.info("\t".join([relation_id, str(len(resp.content))]))
    return jsonify({
        "file": session["result_file"],
        "size": len(resp.content)})


@app.route("/get_box/", methods=["get"])
def get_box():
    """Get the data from Overpass"""
    
    session["use_altserver"] = request.args.get("altserver") == "1"
    north = request.args.get("n")
    south = request.args.get("s")
    east = request.args.get("e")
    west = request.args.get("w")

    metrics = MapperMetrics()
    metrics.retrieve_bbox(north, south, east, west)
    metrics.parse()
    print(metrics.users)
    print(metrics.totals)

    # session["osm_file_path"] = os.path.join(
    #     tempfile.gettempdir(),
    #     session["uid"] + ".csv")
    # overpass_query = app.config["OVERPASS_BOX_QUERY"].format(n=north, s=south, e=east, w=west)
    # print("sending to overpass: {}".format(overpass_query))
    # resp = requests.post(
    #     app.config["OVERPASS_API_URL"] if session["use_altserver"] else app.config["ALT_OVERPASS_API_URL"],
    #     data=overpass_query)
    # print("saving to {}".format(session["osm_file_path"]))
    # with open(session["osm_file_path"], "w") as file_handle:
    #     for block in resp.iter_content(1024):
    #         file_handle.write(block)
    # logging.info("\t".join([north, south, east, west, str(len(resp.content))]))
    return jsonify({
        "file": session["osm_file_path"],
        "size": 1})


@app.route("/process", methods=["get"])
def process_result():
    """After getting the result, save ans parse it, and return the metrics"""

    metrics = MapperMetrics()
    saved_file_path = ""
    download_filename = ""
    save_for_download = request.args.get("download") == "1"

    metrics.parse()
    print(metrics)

    # If raw CSV file download was requested, save it
    if save_for_download:
        download_filename = str(uuid4()) + ".csv"
        saved_file_path = os.path.join(
            app.config["DATA_DIR"],
            download_filename)
        shutil.move(session["result_file"], saved_file_path)
    elif not app.debug:
        logging.info("Removing temp file: %s", session["result_file"])
        os.remove(session["result_file"])

    return jsonify({
        "totals": metrics.totals,
        "users": metrics.users,
        "file": os.path.join(app.config["DATA_ALIAS"], download_filename)})
