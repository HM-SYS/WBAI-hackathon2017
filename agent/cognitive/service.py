# coding: utf-8

import interpreter
import brica1
import numpy as np

import logging
import logging.config
from config.log import APP_KEY

app_logger = logging.getLogger(APP_KEY)


class AgentService:
    def __init__(self, config_file, feature_extractor):
        self.feature_extractor = feature_extractor
        self.nb = interpreter.NetworkBuilder()
        f = open(config_file)
        self.nb.load_file(f)
        self.agents = {}
        self.schedulers = {}
        self.v1_components = {}     # primary visual cortex
        self.vvc_components = {}    # visual what path
        self.bg_components = {}     # basal ganglia
        self.ub_components = {}     # Umataro box
        self.fl_components = {}     # frontal lobe
        self.mo_components = {}     # motor output
        self.rb_components = {}     # reward generator

    def initialize(self, identifier):
        agent_builder = interpreter.AgentBuilder()
        # create agetns and schedulers
        self.agents[identifier] = agent_builder.create_agent(self.nb)
        modules = agent_builder.get_modules()
        self.schedulers[identifier] = brica1.VirtualTimeScheduler(self.agents[identifier])

        # set components
        self.v1_components[identifier] = modules['WBAH2017WBRA.Isocortex#V1'].get_component(
                                                                'WBAH2017WBRA.Isocortex#V1')
        self.vvc_components[identifier] = modules['WBAH2017WBRA.Isocortex#VVC'].get_component(
                                                                'WBAH2017WBRA.Isocortex#VVC')
        self.bg_components[identifier] = modules['WBAH2017WBRA.BG'].get_component(
                                                                'WBAH2017WBRA.BG')
        self.ub_components[identifier] = modules['WBAH2017WBRA.UB'].get_component(
                                                                'WBAH2017WBRA.UB')
        self.fl_components[identifier] = modules['WBAH2017WBRA.Isocortex#FL'].get_component(
                                                                'WBAH2017WBRA.Isocortex#FL')
        self.mo_components[identifier] = modules['WBAH2017WBRA.MO'].get_component(
                                                                'WBAH2017WBRA.MO')
        self.rb_components[identifier] = modules['WBAH2017WBRA.RB'].get_component(
                                                                'WBAH2017WBRA.RB')

        # set feature_extractor
        self.vvc_components[identifier].set_model(self.feature_extractor)

        # set interval of each components
        self.vvc_components[identifier].interval = 1000
        self.bg_components[identifier].interval = 1000
        self.ub_components[identifier].interval = 1000
        self.mo_components[identifier].interval = 1000
        self.fl_components[identifier].interval = 1000

        # set offset
        self.vvc_components[identifier].offset = 1000
        self.bg_components[identifier].offset = 2000
        self.fl_components[identifier].offset = 3000
        self.ub_components[identifier].offset = 4000
        self.mo_components[identifier].offset = 5000

        # set sleep
        self.vvc_components[identifier].sleep = 4000
        self.bg_components[identifier].sleep = 4000
        self.ub_components[identifier].sleep = 4000
        self.mo_components[identifier].sleep = 4000
        self.fl_components[identifier].sleep = 4000

        self.schedulers[identifier].update()


    def create(self, reward, feature, identifier):
        if identifier not in self.agents:
            self.initialize(identifier)

        # agent start
        self.bg_components[identifier].get_in_port('Isocortex#VVC-BG-Input').buffer = feature
        action = self.bg_components[identifier].start()
        self.fl_components[identifier].last_action = action
        self.ub_components[identifier].last_state = feature

        if app_logger.isEnabledFor(logging.DEBUG):
            app_logger.debug('feature: {}'.format(features))

        return action

    def step(self, reward, observation, identifier):
        if identifier not in self.agents:
            return str(-1)
        self.v1_components[identifier].get_out_port('Isocortex#V1-Isocortex#VVC-Output').buffer = observation
        self.rb_components[identifier].get_out_port('RB-Isocortex#FL-Output').buffer = np.array([reward])
        self.rb_components[identifier].get_out_port('RB-BG-Output').buffer = np.array([reward])
        self.schedulers[identifier].step(5000)

        action = self.mo_components[identifier].get_in_port('Isocortex#FL-MO-Input').buffer[0]

        return action

    def reset(self, reward, identifier):
        if identifier not in self.agents:
            return str(-1)
        action = self.mo_components[identifier].get_in_port('Isocortex#FL-MO-Input').buffer[0]
        self.ub_components[identifier].end(action, reward)
        self.ub_components[identifier].output(self.ub_components[identifier].last_output_time)
        self.bg_components[identifier].input(self.bg_components[identifier].last_input_time)
        self.bg_components[identifier].end(reward)

        return action
