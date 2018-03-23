# coding: utf-8

import numpy as np
from chainer import cuda
import pickle


class Experience:
    gamma = 0.86
    tsn_file = open( 'network_x10000_color_ICA.tsn', 'rb' )
    sfa_network = pickle.load( tsn_file )
    def __init__(self, use_gpu=0, data_size=10**4, replay_size=32, hist_size=1, initial_exploration=10**3, dim=10240):
        self.threshold = 0.3
        self.placeCellThreshold = 0.4
        self.placeCell_dim = 32
        self.image_dim = 6 * 6
        self.feature_size = 256
        self.use_gpu = use_gpu
        self.data_size = data_size
        self.replay_size = replay_size
        self.hist_size = hist_size
        self.initial_exploration = initial_exploration
        self.dim = dim
        self.episodeLst = [np.zeros((self.data_size, self.hist_size, self.feature_size * self.image_dim), dtype=np.float32),
                  np.zeros(self.data_size, dtype=np.uint8),
                  np.zeros((self.data_size, 1), dtype=np.float32),
                  np.zeros((self.data_size, 1), dtype=np.bool),
                  np.zeros(((self.data_size, self.hist_size, self.placeCell_dim)), dtype=np.float32)]

        self.returnFeature = [np.zeros((self.data_size/10, 1), dtype=np.bool),
                  np.zeros((self.data_size/10, 1), dtype=np.float32),
                  np.zeros((self.data_size/10, self.hist_size, self.feature_size * self.image_dim), dtype=np.float32),
                  np.zeros(self.data_size/10, dtype=np.uint8),
                  np.zeros((self.data_size/10, 1), dtype=np.float32),
                  np.zeros((self.data_size/10, self.hist_size, self.placeCell_dim), dtype=np.float32)]

        self.qFeature = [np.zeros((self.data_size/10, 1), dtype=np.bool),
                  np.zeros((self.data_size/10, 1), dtype=np.float32),
                  np.zeros((self.data_size, self.hist_size, self.placeCell_dim), dtype=np.float32)]

    def episodeStock(self, time, state, last_placeCell, action, reward, episode_end_flag):
        data_index = time % self.data_size
        imgFeatureState = state[0 : self.image_dim * self.feature_size]
        normalFeatureState = imgFeatureState / np.max(imgFeatureState)
        network_result = self.sfa_network.execute( last_placeCell )
        normalNr = (network_result - np.min(network_result))/ (np.max(network_result) - np.min(network_result))

        self.episodeLst[0][data_index] = normalFeatureState
        self.episodeLst[1][data_index] = action
        self.episodeLst[2][data_index] = reward
        self.episodeLst[3][data_index] = episode_end_flag
        self.episodeLst[4][data_index] = normalNr

    def conceptualization(self, state_dash, placeCell):
        imgFeatureState_dash = state_dash[0 : self.image_dim * self.feature_size]
        normalState_dash  = imgFeatureState_dash / np.max(imgFeatureState_dash)
        placeCell_result = self.sfa_network.execute( placeCell )
        placeCellNr = (placeCell_result - np.min(placeCell_result))/ (np.max(placeCell_result) - np.min(placeCell_result))
        cnt = 0
        cnt1 = 0
        self.returnFeature = [np.zeros((self.data_size/10, 1), dtype=np.bool),
                  np.zeros((self.data_size/10, 1), dtype=np.float32),
                  np.zeros((self.data_size/10, self.hist_size, self.feature_size * self.image_dim), dtype=np.float32),
                  np.zeros(self.data_size/10, dtype=np.uint8),
                  np.zeros((self.data_size/10, 1), dtype=np.float32),
                  np.zeros((self.data_size/10, self.hist_size, self.placeCell_dim), dtype=np.float32)]

        for i in xrange(self.data_size):
            squares = (self.episodeLst[0][i][0] - normalState_dash)**2
            sum_of_sqrt = np.sqrt(np.sum(squares))
            placeCellSquares = (self.episodeLst[4][i][0] - placeCellNr)**2
            placeCell_sum_of_sqrt = np.sqrt(np.sum(placeCellSquares))
            if (1 / (1 + sum_of_sqrt)) > self.threshold and (1 / (1 + placeCell_sum_of_sqrt)) > self.placeCellThreshold:
                self.returnFeature[0][cnt] = True
                self.returnFeature[1][cnt] = 1 / (1 + sum_of_sqrt)
                self.returnFeature[2][cnt] = self.episodeLst[0][i][0]
                self.returnFeature[3][cnt] = self.episodeLst[1][i]
                self.returnFeature[4][cnt] = self.episodeLst[2][i]
                cnt += 1
            if (1 / (1 + placeCell_sum_of_sqrt)) > self.placeCellThreshold:
                self.qFeature[0][cnt] = True
                self.qFeature[1][cnt] = self.episodeLst[2][i]
                self.qFeature[2][cnt] = self.episodeLst[4][i][0]
                cnt1 += 1
        return self.returnFeature, self.qFeature

    def valueUpdate(self, time, reward):
        data_index = (time) % self.data_size
        cnt = 0
        if reward > 0 and (self.episodeLst[2][data_index] - self.episodeLst[2][data_index - 1]) > 0 :
            for i in reversed(range(data_index)):
                if i == 0 or self.episodeLst[3][i] == True:
                    break
                else:
                    self.episodeLst[2][i] = reward * (self.gamma ** cnt)
                    cnt += 1
            self.episodeLst[3][data_index] = True
