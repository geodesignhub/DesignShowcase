from shapely.geometry.base import BaseGeometry
from shapely.geometry import shape, mapping, shape

import json
from shapely import speedups

class ShapelyEncoder(json.JSONEncoder):
    ''' Encodes JSON strings into shapes processed by SHapely'''
    def default(self, obj):
        if isinstance(obj, BaseGeometry):
            return mapping(obj)
        return json.JSONEncoder.default(self, obj)


class ShapelyDecoder(json.JSONDecoder):
    ''' Decodes JSON strings into shapes processed by SHapely'''
    def decode(self, json_string):
        def shapely_object_hook(obj):
            if 'coordinates' in obj and 'type' in obj:
                return shape(obj)
            return obj
        return json.loads(json_string, object_hook=shapely_object_hook)


def export_to_JSON(data):
    ''' Export a shapely output to JSON'''
    return json.dumps(data, sort_keys=True, cls=ShapelyEncoder)


def load_from_JSON(json_string):
    '''Read JSON and a create a SHapely Object '''
    return json.loads(json_string, cls=ShapelyDecoder)
