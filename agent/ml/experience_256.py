# coding: utf-8

import numpy as np
from chainer import cuda


class Experience:
    def __init__(self, use_gpu=0, data_size=10**4, replay_size=32, hist_size=1, initial_exploration=10**3, dim=10240):

        self.image_dim = 6 * 6
        self.feature_size = 256
        self.threshold = 0.3
        self.use_gpu = use_gpu
        self.data_size = data_size
        self.replay_size = replay_size
        self.hist_size = hist_size
        # self.initial_exploration = 10
        self.initial_exploration = initial_exploration
        self.dim = dim

        self.d = [np.zeros((self.data_size, self.hist_size, self.dim), dtype=np.uint8),
                  np.zeros(self.data_size, dtype=np.uint8),
                  np.zeros((self.data_size, 1), dtype=np.int8),
                  np.zeros((self.data_size, self.hist_size, self.dim), dtype=np.uint8),
                  np.zeros((self.data_size, 1), dtype=np.bool)]

        self.episodeLst = [np.zeros((self.data_size, self.hist_size, self.feature_size * self.image_dim), dtype=np.float32),
                  np.zeros(self.data_size, dtype=np.uint8),
                  np.zeros((self.data_size, 1), dtype=np.int8),
                  np.zeros((self.data_size, 1), dtype=np.bool)]


    def stock(self, time, state, action, reward, state_dash, episode_end_flag):
        data_index = time % self.data_size
        if episode_end_flag is True:
            self.d[0][data_index] = state
            self.d[1][data_index] = action
            self.d[2][data_index] = reward
        else:
            self.d[0][data_index] = state
            self.d[1][data_index] = action
            self.d[2][data_index] = reward
            self.d[3][data_index] = state_dash
        self.d[4][data_index] = episode_end_flag

    def episodeStock(self, time, state, action, reward, state_dash, episode_end_flag):
        data_index = time % self.data_size
        cnt = 0
        j = 0
        data_index = time % self.data_size
        imgFeatureState = state[0 : self.image_dim * self.feature_size]
        imgFeatureState_dash = state_dash[0 : self.image_dim * self.feature_size]

        #lst = np.zeros(self.image_dim)
        #lst_dash = np.zeros(self.image_dim)

        #featureState = np.zeros(self.feature_size)
        #featureState_dash = np.zeros(self.feature_size)

        #for i in range(len(imgFeatureState)):
        #    if (i + 1) % self.image_dim == 0:
        #        lst[cnt] = imgFeatureState[i]
        #        lst_dash[cnt] = imgFeatureState_dash[i]
        #        #print(lst)
        #        featureState[j] = max(lst)
        #        #print(lst_dash)
        #        featureState_dash[j] = max(lst_dash)
        #        lst = np.zeros(self.image_dim)
        #        lst_dash = np.zeros(self.image_dim)
        #        cnt = 0
        #        j = j + 1
        #    else:
        #        lst[cnt] = imgFeatureState[i]
        #        lst_dash[cnt] = imgFeatureState_dash[i]
        #        cnt = cnt + 1

        normalFeatureState = imgFeatureState / np.max(imgFeatureState)
        normalState_dash  = imgFeatureState_dash / np.max(imgFeatureState_dash)
        self.episodeLst[0][data_index] = normalFeatureState
        self.episodeLst[1][data_index] = action
        self.episodeLst[2][data_index] = reward
        self.episodeLst[3][data_index] = episode_end_flag
        cnt = 0
        returnFeature = {}
        addLst = [np.zeros(self.image_dim * self.feature_size, dtype=np.float32), np.zeros(1, dtype=np.uint8), np.zeros(1, dtype=np.int8)]
        for i in xrange(self.data_size):
            squares = (self.episodeLst[0][i][0] - normalState_dash)**2
            sum_of_sqrt = np.sqrt(np.sum(squares))
            if (1 / (1 + sum_of_sqrt)) > self.threshold:
                if cnt == 0:

                    addLst[0] = self.episodeLst[0][i][0]
                    addLst[1] = self.episodeLst[1][i]
                    addLst[2] = self.episodeLst[2][i]
                    returnFeature = addLst
                    cnt = 1
                else:
                    addLst[0] = self.episodeLst[0][i][0]
                    addLst[1] = self.episodeLst[1][i]
                    addLst[2] = self.episodeLst[2][i]
                    returnFeature.append(addLst)
        if cnt == 0:
            returnFeature = "none"
        return returnFeature

    def replay(self, time):
        replay_start = False
        if self.initial_exploration < time:
            replay_start = True
            # Pick up replay_size number of samples from the Data
            if time < self.data_size:  # during the first sweep of the History Data
                replay_index = np.random.randint(0, time, (self.replay_size, 1))
            else:
                replay_index = np.random.randint(0, self.data_size, (self.replay_size, 1))

            s_replay = np.ndarray(shape=(self.replay_size, self.hist_size, self.dim), dtype=np.float32)
            a_replay = np.ndarray(shape=(self.replay_size, 1), dtype=np.uint8)
            r_replay = np.ndarray(shape=(self.replay_size, 1), dtype=np.float32)
            s_dash_replay = np.ndarray(shape=(self.replay_size, self.hist_size, self.dim), dtype=np.float32)
            episode_end_replay = np.ndarray(shape=(self.replay_size, 1), dtype=np.bool)
            for i in xrange(self.replay_size):
                s_replay[i] = np.asarray(self.d[0][replay_index[i]], dtype=np.float32)
                a_replay[i] = self.d[1][replay_index[i]]
                r_replay[i] = self.d[2][replay_index[i]]
                s_dash_replay[i] = np.array(self.d[3][replay_index[i]], dtype=np.float32)
                episode_end_replay[i] = self.d[4][replay_index[i]]

            if self.use_gpu >= 0:
                s_replay = cuda.to_gpu(s_replay)
                s_dash_replay = cuda.to_gpu(s_dash_replay)

            return replay_start, s_replay, a_replay, r_replay, s_dash_replay, episode_end_replay

        else:
            return replay_start, 0, 0, 0, 0, False

    def end_episode(self, time, last_state, action, reward):
        self.stock(time, last_state, action, reward, last_state, True)
        replay_start, s_replay, a_replay, r_replay, s_dash_replay, episode_end_replay = \
            self.replay(time)

        return replay_start, s_replay, a_replay, r_replay, s_dash_replay, episode_end_replay
