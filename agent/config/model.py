# -*- coding: utf-8 -*-
from . import BASE_DIR

CNN_FEATURE_EXTRACTOR = BASE_DIR + '/model/alexnet_feature_extractor.pickle'
CAFFE_MODEL = BASE_DIR + '/model/bvlc_alexnet.caffemodel'
MODEL_TYPE = 'alexnet'

DEFAULT_MEAN_IMAGE = BASE_DIR + '/model/ilsvrc_2012_mean.npy'
