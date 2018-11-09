# -*- coding: utf-8 -*-
import os
import struct
import gzip
import requests
import numpy

import GlobalGeodetic
import config




g = GlobalGeodetic.GlobalGeodetic(True, 64)


def get_versioned_terrain(tileset, tile_version, z, x, yfile):
    base_url = 'http://52.80.138.89:8000/tilesets/newchinaterrain/'
    base_maxzoom = 14

    # tileset extent
    (ts_minx, ts_maxx, ts_miny, ts_maxy) = (111.8354101416683477, 111.9772674665320835, 26.8916309661356223, 27.0008512804983205)

    y = int(yfile.split('.')[0])
    # tile extent
    (t_minx, t_miny, t_maxx, t_maxy) = g.TileBounds(x, y, z)

    if intersects(t_minx, t_maxx, t_miny, t_maxy,
                  ts_minx, ts_maxx, ts_miny, ts_maxy):
        return merge_terrain(tileset, tile_version, z, x, y, base_url, base_maxzoom)
    else:
        return os.path.join(config.tiles_dir, tileset, str(z), str(x), yfile)


def merge_terrain(tileset, tile_version, z, x, y, base_url, base_maxzoom):

    if z <= base_maxzoom:
        other_url = '{0}/{1}/{2}/{3}.terrain'.format(base_url, z, x, y)
        r = requests.get(other_url)
        remote_grid, remote_mask = decode_terrain(r.content)

        with gzip.open(os.path.join(config.tiles_dir, tileset, str(z), str(x), str(y) + '.terrain'), 'rb') as f:
            high_grid, high_mask = decode_terrain(f.read())
            merged_grid = merge_terrain_grid(high_grid, remote_grid)
            if z < base_maxzoom:
                high_mask = remote_mask




    return True


def merge_terrain_grid(grid_high, grid_low):
    index_y, index_x = numpy.where(grid_high == 0)
    for i in len(index_y):
        grid_high[index_y[i]][index_x[i]] = grid_low[index_y[i]][index_x[i]]
    return grid_high

def decode_terrain(terrainbuffer):
    n = numpy.frombuffer(terrainbuffer, dtype=numpy.int16)
    n1 = numpy.split(n, [4225])
    mask_int = n[4225]
    mask_decode = struct.pack('<H', mask_int)
    child_flag, water_mask = struct.unpack('<BB', mask_decode)
    des = n1[0].reshape(65, 65)
    des = (des / 5) - 1000
    return des, child_flag, water_mask


def intersects(xmin1, xmax1, ymin1, ymax1, xmin2, xmax2, ymin2, ymax2):
    x_overlap = value_in_range(xmin1, xmin2, xmax2) or value_in_range(xmin2, xmin1, xmax1)
    y_overlap = value_in_range(ymin1, ymin2, ymax2) or value_in_range(ymin2, ymin1, ymax1)
    #return x_overlap and y_overlap
    return True


def contains(xmin1, xmax1, ymin1, ymax1, xmin2, xmax2, ymin2, ymax2):
    x_contains = value_in_range(xmin1, xmin2, xmax2) and value_in_range(xmax1, xmin2, xmax2)
    y_contains = value_in_range(ymin1, ymin2, ymax2) and value_in_range(ymax1, ymin2, ymax2)
    return x_contains and y_contains


def value_in_range(value, min_value, max_value):
    return max_value <= value >= min_value


# get_versioned_terrain('dama', '1', 13, 13281, '5320.terrain')
