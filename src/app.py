# -*- coding: utf-8 -*-

import os
import json
from flask import Flask
from flask import make_response
from flask import send_from_directory
from flask import abort
from flask import request
from flask import Response
from flask_cors import CORS
import config
import versions

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/tilesets/', methods=['GET'])
def get_tilesets():
    tilesets = os.listdir(config.tiles_dir)
    tileset_names = []
    for d in tilesets:
        if os.path.isdir(os.path.join(config.tiles_dir, d)):
            tileset_names.append(d)

    result_html = '<h1>Available tilesets:</h1><br/>'
    result_html += '<br/>'.join(tileset_names)
    return result_html


@app.route('/tilesets/<tileset>/', methods=['GET'])
def get_tile_info(tileset):
    info_path = os.path.join(config.tiles_dir, tileset)
    info_file = os.path.join(info_path, 'layer.json')
    if os.path.exists(info_file):
        return send_from_directory(info_path, 'layer.json')

    resp = Response(json.dumps(config.default_heightmap_layerinfo), mimetype='application/json')
    return resp


@app.route('/tilesets/<tileset>/layer.json', methods=['GET'])
def get_tile_infofile(tileset):
    info_path = os.path.join(config.tiles_dir, tileset)
    info_file = os.path.join(info_path, 'layer.json')
    if os.path.exists(info_file):
        return send_from_directory(info_path, 'layer.json')

    resp = Response(json.dumps(config.default_heightmap_layerinfo), mimetype='application/json')
    return resp


@app.route('/tilesets/<tileset>/<z>/<x>/<yfile>', methods=['GET'])
def get_file(tileset, z, x, yfile):
    terrain_path = os.path.join(config.tiles_dir, tileset, z, x)
    terrain_file = os.path.join(terrain_path, yfile)

    tile_version = request.args.get('v')
    if tile_version is not None:
        terrain_file = versions.get_versioned_terrain(tileset, tile_version, z, x, yfile)

    if os.path.exists(terrain_file):
        return serve_terrain_file(terrain_file)

    if int(z) == 0:
        return serve_terrain_file(config.default_mesh_tile)
    abort(404)


@app.route('/tilesets/<tileset>/merge_tileset', methods=['POST'])
def gen_merged_tileset(tileset):
    merge_url = request.args.get('url')
    max_level = request.args.get('max_level')
    # write_to_config(tileset, merge_url, max_level)


# def write_to_config(tileset, merge_url, max_level):
    # config_path = os.path.join(config.tiles_dir, 'mergeconfig.json')
    # if not os.path.exists(config_path):
    #     with open(config_path, 'w') as f:
    #         f.write('{}')
    # with open(config_path, 'w') as f:
    #     merge_config = json.load(f)
    #     if merge_config.has_key(tileset):
    #         tile_config = merge_config['tileset']
    #         if tile_config.has_key()



def serve_terrain_file(filepath):
    f = open(filepath)
    data = f.read()
    f.close()
    response = Response()
    response.data = data
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content-Encoding'] = 'gzip'
    response.headers['Content-Type'] = 'application/octet-stream'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)

