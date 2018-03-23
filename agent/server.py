# -*- coding: utf-8 -*-
import argparse
import cPickle as pickle
import io
import os

import brica1
import cherrypy
import msgpack
import numpy as np
from PIL import Image
from PIL import ImageOps

from cognitive import interpreter
from ml.cnn_feature_extractor import CnnFeatureExtractor

from config import BRICA_CONFIG_FILE
from config.model import CNN_FEATURE_EXTRACTOR, CAFFE_MODEL, MODEL_TYPE

import logging
import logging.config
from config.log import CHERRYPY_ACCESS_LOG, CHERRYPY_ERROR_LOG, LOGGING, APP_KEY, INBOUND_KEY, OUTBOUND_KEY
from cognitive.service import AgentService
from tool.result_logger import ResultLogger

logging.config.dictConfig(LOGGING)

inbound_logger = logging.getLogger(INBOUND_KEY)
app_logger = logging.getLogger(APP_KEY)
outbound_logger = logging.getLogger(OUTBOUND_KEY)


def unpack(payload, depth_image_count=1, depth_image_dim=32*32):
    dat = msgpack.unpackb(payload)

    image = []
    for i in xrange(depth_image_count):
        image.append(Image.open(io.BytesIO(bytearray(dat['image'][i]))))

    depth = []
    for i in xrange(depth_image_count):
        d = (Image.open(io.BytesIO(bytearray(dat['depth'][i]))))
        depth.append(np.array(ImageOps.grayscale(d)).reshape(depth_image_dim))

    reward = dat['reward']
    observation = {"image": image, "depth": depth}

    return reward, observation


def unpack_reset(payload):
    dat = msgpack.unpackb(payload)
    reward = dat['reward']
    success = dat['success']
    failure = dat['failure']
    elapsed = dat['elapsed']
    finished = dat['finished']

    return reward, success, failure, elapsed, finished

use_gpu = int(os.getenv('GPU', '-1'))
depth_image_dim = 32 * 32
depth_image_count = 1
image_feature_dim = 256 * 6 * 6
image_feature_count = 1
feature_output_dim = (depth_image_dim * depth_image_count) + (image_feature_dim * image_feature_count)


class Root(object):
    def __init__(self, **kwargs):
        if os.path.exists(CNN_FEATURE_EXTRACTOR):
            app_logger.info("loading... {}".format(CNN_FEATURE_EXTRACTOR))
            self.feature_extractor = pickle.load(open(CNN_FEATURE_EXTRACTOR))
            app_logger.info("done")
        else:
            self.feature_extractor = CnnFeatureExtractor(use_gpu, CAFFE_MODEL, MODEL_TYPE, image_feature_dim)
            pickle.dump(self.feature_extractor, open(CNN_FEATURE_EXTRACTOR, 'w'))
            app_logger.info("pickle.dump finished")

        self.agent_service = AgentService(BRICA_CONFIG_FILE, self.feature_extractor)
        self.result_logger = ResultLogger()

    @cherrypy.expose()
    def flush(self, identifier):
        self.agent_service.initialize(identifier)

    @cherrypy.expose
    def create(self, identifier):
        body = cherrypy.request.body.read()
        reward, observation = unpack(body)

        inbound_logger.info('reward: {}, depth: {}'.format(reward, observation['depth']))
        feature = self.feature_extractor.feature(observation)
        self.result_logger.initialize()
        result = self.agent_service.create(reward, feature, identifier)

        outbound_logger.info('action: {}'.format(result))

        return str(result)

    @cherrypy.expose
    def step(self, identifier):
        body = cherrypy.request.body.read()
        reward, observation = unpack(body)

        inbound_logger.info('reward: {}, depth: {}'.format(reward, observation['depth']))

        result = self.agent_service.step(reward, observation, identifier)
        self.result_logger.step()
        outbound_logger.info('result: {}'.format(result))
        return str(result)

    @cherrypy.expose
    def reset(self, identifier):
        body = cherrypy.request.body.read()
        reward, success, failure, elapsed, finished = unpack_reset(body)

        inbound_logger.info('reward: {}, success: {}, failure: {}, elapsed: {}'.format(
            reward, success, failure, elapsed))

        result = self.agent_service.reset(reward, identifier)
        self.result_logger.report(success, failure, finished)

        outbound_logger.info('result: {}'.format(result))
        return str(result)

def main(args):
    cherrypy.config.update({'server.socket_host': args.host, 'server.socket_port': args.port, 'log.screen': False,
                            'log.access_file': CHERRYPY_ACCESS_LOG, 'log.error_file': CHERRYPY_ERROR_LOG})
    cherrypy.quickstart(Root())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LIS Backend')
    parser.add_argument('--host', default='localhost', type=str, help='Server hostname')
    parser.add_argument('--port', default=8765, type=int, help='Server port number')
    args = parser.parse_args()

    main(args)
