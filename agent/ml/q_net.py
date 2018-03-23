# -*- coding: utf-8 -*-

import copy
import numpy as np
from chainer import cuda, FunctionSet, Variable
import chainer.functions as F

from config.log import APP_KEY
import logging
app_logger = logging.getLogger(APP_KEY)
npa = np.array

class QNet:
    # Hyper-Parameters
    gamma = 0.99  # Discount factor
    initial_exploration = 10**3  # Initial exploratoin. original: 5x10^4
    replay_size = 32  # Replay (batch) size
    target_model_update_freq = 10**4  # Target update frequancy. original: 10^4
    data_size = 10**5  # Data size of history. original: 10^6
    hist_size = 1  # original: 4

    def __init__(self, use_gpu, enable_controller, dim, epsilon, epsilon_delta, min_eps):
        self.use_gpu = use_gpu
        self.num_of_actions = len(enable_controller)
        self.enable_controller = enable_controller
        self.dim = dim
        self.epsilon = epsilon
        self.epsilon_delta = epsilon_delta
        self.min_eps = min_eps
        self.time = 0
        self.increaseTemp = 1.05
        self.decreaseTemp = 0.95
        app_logger.info("Initializing Q-Network...")

        hidden_dim = 256
        self.model = FunctionSet(
            l4=F.Linear(self.dim*self.hist_size, hidden_dim, wscale=np.sqrt(2)),
            q_value=F.Linear(hidden_dim, self.num_of_actions,
                             initialW=np.zeros((self.num_of_actions, hidden_dim),
                                               dtype=np.float32))
        )
        if self.use_gpu >= 0:
            self.model.to_gpu()

        self.model_target = copy.deepcopy(self.model)

    def q_func(self, state):
        h4 = F.relu(self.model.l4(state / 255.0))
        q = self.model.q_value(h4)
        return q

    def e_greedy(self, state, epsilon):
        s = Variable(state)
        q = self.q_func(s)
        q = q.data

        if np.random.rand() < epsilon:
            index_action = np.random.randint(0, self.num_of_actions)
            app_logger.info(" Random")
        else:
            if self.use_gpu >= 0:
                index_action = np.argmax(q.get())
            else:
                index_action = np.argmax(q)
            app_logger.info("#Greedy")
        return self.index_to_action(index_action), q

    def target_model_update(self):
        self.model_target = copy.deepcopy(self.model)

    def index_to_action(self, index_of_action):
        return self.enable_controller[index_of_action]

    def action_to_index(self, action):
        return self.enable_controller.index(action)

    def start(self, feature):
        self.state = np.zeros((self.hist_size, self.dim), dtype=np.uint8)
        self.state[0] = feature

        state_ = np.asanyarray(self.state.reshape(1, self.hist_size, self.dim), dtype=np.float32)
        if self.use_gpu >= 0:
            state_ = cuda.to_gpu(state_)

        # Generate an Action e-greedy
        action, q_now = self.e_greedy(state_, self.epsilon)
        return_action = action

        return return_action

    def update_model(self, replayed_experience):

        self.time += 1
        app_logger.info("step: {}".format(self.time))

    def update_temp(self, reward, temp):

        if temp >= 1 and reward >= 0:
            retTemp = temp * self.increaseTemp
        if temp <= 1 and reward < 0:
            retTemp = temp * self.decreaseTemp
        if (temp > 1 and reward < 0) or (temp < 1 and reward > 0):
            retTemp = 1

        self.time += 1
        app_logger.info("step: {}".format(self.time))

        return retTemp

    def step(self, features):
        if self.hist_size == 4:
            self.state = np.asanyarray([self.state[1], self.state[2], self.state[3], features], dtype=np.uint8)
        elif self.hist_size == 2:
            self.state = np.asanyarray([self.state[1], features], dtype=np.uint8)
        elif self.hist_size == 1:
            self.state = np.asanyarray([features], dtype=np.uint8)
        else:
            app_logger.error("self.DQN.hist_size err")

        state_ = np.asanyarray(self.state.reshape(1, self.hist_size, self.dim), dtype=np.float32)
        if self.use_gpu >= 0:
            state_ = cuda.to_gpu(state_)

        # Exploration decays along the time sequence
        if self.initial_exploration < self.time:
            self.epsilon -= self.epsilon_delta
            if self.epsilon < self.min_eps:
                self.epsilon = self.min_eps
            eps = self.epsilon
        else:  # Initial Exploation Phase
            app_logger.info("Initial Exploration : {}/{} steps".format(self.time, self.initial_exploration))
            eps = 1.0

        # Generate an Action by e-greedy action selection
        action, q_now = self.e_greedy(state_, eps)

        if self.use_gpu >= 0:
            q_max = np.max(q_now.get())
        else:
            q_max = np.max(q_now)

        return action, eps, q_max

    def decisionMaking(self, episode_feature, temp):
        if episode_feature[0][0] == False:
            index_action = np.random.randint(0, self.num_of_actions)
            app_logger.info(" Random")
        else:
            action_lst = np.zeros(self.num_of_actions)
            action_num = np.zeros(self.num_of_actions)
            calc_lst = []
            for i in range(1000):
                for j in range(self.num_of_actions):
                    if episode_feature[3][i] == self.index_to_action(j) and episode_feature[0][i] == True:
                        action_lst[j] += episode_feature[4][i]
                        action_num[j] += 1
            action_lst = action_lst / action_num
            for i in range(len(action_lst)):
                if action_lst[i] == action_lst[i]:
                    calc_lst.append(action_lst[i])
                else:
                    calc_lst.append(0)

            e = np.exp(npa(calc_lst) / temp)
            dist = e / np.sum(e)
            rand = np.random.rand()
            softmaxVal = 0
            boo = False
            for i in range(len(dist)):
                softmaxVal += dist[i]
                if softmaxVal >= rand and boo == False:
                    index_action = i
                    boo = True
        return self.index_to_action(index_action)
