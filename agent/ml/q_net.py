# -*- coding: utf-8 -*-

import copy
import numpy as np
from chainer import cuda, FunctionSet, Variable, optimizers
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

        self.optimizer = optimizers.RMSpropGraves(lr=0.00025, alpha=0.95, momentum=0.95, eps=0.0001)
        self.optimizer.setup(self.model.collect_parameters())

        # History Data :  D=[s, a, r, s_dash, end_episode_flag]
        self.d = [np.zeros((self.data_size, self.hist_size, self.dim), dtype=np.uint8),
                  np.zeros(self.data_size, dtype=np.uint8),
                  np.zeros((self.data_size, 1), dtype=np.int8),
                  np.zeros((self.data_size, self.hist_size, self.dim), dtype=np.uint8),
                  np.zeros((self.data_size, 1), dtype=np.bool)]

    def forward(self, state, action, reward, state_dash, episode_end):
        num_of_batch = state.shape[0]
        s = Variable(state)
        s_dash = Variable(state_dash)

        q = self.q_func(s)
        tmp = self.q_func_target(s_dash)  # Q(s',*)
        if self.use_gpu >= 0:
            tmp = list(map(np.max, tmp.data.get()))  # max_a Q(s',a)
        else:
            tmp = list(map(np.max, tmp.data))  # max_a Q(s',a)

        max_q_dash = np.asanyarray(tmp, dtype=np.float32)
        if self.use_gpu >= 0:
            target = np.asanyarray(q.data.get(), dtype=np.float32)
        else:
            target = np.array(q.data, dtype=np.float32)

        for i in xrange(num_of_batch):
            if not episode_end[i][0]:
                tmp_ = reward[i] + self.gamma * max_q_dash[i]
            else:
                tmp_ = reward[i]

            action_index = self.action_to_index(action[i])
            target[i, action_index] = tmp_

        # TD-error clipping
        if self.use_gpu >= 0:
            target = cuda.to_gpu(target)
        td = Variable(target) - q  # TD error
        td_tmp = td.data + 1000.0 * (abs(td.data) <= 1)  # Avoid zero division
        td_clip = td * (abs(td.data) <= 1) + td/abs(td_tmp) * (abs(td.data) > 1)

        zero_val = np.zeros((self.replay_size, self.num_of_actions), dtype=np.float32)
        if self.use_gpu >= 0:
            zero_val = cuda.to_gpu(zero_val)
        zero_val = Variable(zero_val)
        loss = F.mean_squared_error(td_clip, zero_val)
        return loss, q

    def q_func(self, state):
        h4 = F.relu(self.model.l4(state / 255.0))
        q = self.model.q_value(h4)
        return q

    def q_func_target(self, state):
        h4 = F.relu(self.model_target.l4(state / 255.0))
        q = self.model_target.q_value(h4)
        return q

    def e_greedy(self, state, epsilon):
        s = Variable(state)
        q = self.q_func(s)
        q = q.data

        if np.random.rand() < epsilon:
            index_action = np.random.randint(0, self.num_of_actions)
            app_logger.info(" Random_e_greesy "+str(index_action))
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
        app_logger.info("step(model): {}".format(self.time))

    def update_temp(self, reward, temp):

        if temp <= 1 and reward >= 0:
            retTemp = temp * self.decreaseTemp
        if temp >= 1 and reward < 0:
            retTemp = temp * self.increaseTemp
        if (temp < 1 and reward < 0) or (temp > 1 and reward >= 0):
            retTemp = 1

        self.time += 1
        app_logger.info("step(temp): {}".format(self.time))

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
            app_logger.info(" Random_decisionMaking "+str(index_action))
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

            e = np.exp((npa(calc_lst) / temp)*-1)
            dist = e / np.sum(e)
            rand = np.random.rand()
            softmaxVal = 0
            boo = False
            for i in range(len(dist)):
                softmaxVal += dist[i]
                if softmaxVal >= rand and boo == False:
                    index_action = i
                    boo = True
        return self.index_to_action(index_action), calc_lst, temp, action_num
