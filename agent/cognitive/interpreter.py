#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
interpreter.py
=====

This module contains the class `NetworkBuilder` and `AgentkBuilder` which interprets
the contents of BriCA language files.

"""

# BriCA Language Interpreter for V1 (Interpreter version 1)
#  Originally licenced for WBAI (wbai.jp) under the Apache License (?)
#  Created: 2016-01-31

# TODO: import, subports

import json
import os
import sys

import brica1

import logging
from config.log import APP_KEY

app_logger = logging.getLogger(APP_KEY)

debug = False  # True


class NetworkBuilder:
    """
    The BriCA language interpreter.
    - reads BriCA language files.
    """
    unit_dic = {}  # Map: BriCA unit name ⇒ unit object
    super_modules = {}  # Super modules
    #    base_name_space=""  # Base Name Space

    module_dictionary = {}
    sub_modules = {}
    __ports = {}
    __connections = {}
    __comments = {}
    __network = {}
    __super_sub_modules = {}  # Super & Sub modules
    __load_files = []

    def __init__(self):
        """
        NetworkBuilder Create a new `NetworkBuilder` instance.
        Args:
          None.
        Returns:
          NetworkBuilder: a new `NetworkBuilder` instance.
        """
        unit_dic = {}
        module_dictionary = {}
        super_modules = {}
        sub_modules = {}
        __ports = {}
        __connections = {}
        __comments = {}
        __load_files = []

    def load_file(self, file_object):
        """
        Load a BriCA language json file.
        Args:
          A file object
        Returns:
          success:True, failure:False
        """
        self.__load_files.append(os.path.abspath(file_object.name))
        dir_name = os.path.dirname(file_object.name)
        try:
            jsn = json.load(file_object)
        except:
            app_logger.error("File could not be read!")
            return False

        if "Header" not in jsn:
            app_logger.error("Header must be specified!")
            return False
        header = jsn["Header"]

        if "Import" in header:
            import_files = header["Import"]
            for import_file in import_files:
                if "/" != import_file[0]:  # not full path
                    import_file = dir_name + "/" + import_file
                if not os.path.isfile(import_file):
                    app_logger.error("JSON file {} not found!".format(import_file))
                    return False
                if os.path.abspath(import_file) in self.__load_files:
                    app_logger.error("Import file {} has been read!".format(import_file))
                    continue
                f = open(import_file)
                if self.load_file(f) is False:
                    return False

        if "Name" not in header:
            app_logger.error("Header name must be specified!")
            return False

        if "Base" not in header:
            app_logger.error("Base name space must be specified!")
            return False
        self.base_name_space = header["Base"].strip()

        if "Type" not in header:
            app_logger.error("Type must be specified!")
            return False
        self.__type = header["Type"]

        if "Comment" in header:
            self.__comments["Header." + header["Name"]] = header["Comment"]

        if self.__set_modules(jsn) is False:
            return False

        if self.__set_ports(jsn) is False:
            return False

        if self.__set_connections(jsn) is False:
            return False

        return True

    def get_network(self):
        """
        Args:
          None
        return:
          the network created by load_file(self, file_object)
        """
        return {"ModuleDictionary": self.module_dictionary, "SuperModules": self.super_modules,
                "SubModules": self.sub_modules, "Ports": self.__ports, "Connections": self.__connections,
                "Comments": self.__comments}

    def check_consistency(self):
        """
        Args:
          None
        return:
          true iff no fatal inconsistency in the network
          function:
          see the consistency check section below.
        """
        for module_name in self.module_dictionary:
            if module_name not in self.unit_dic:
                if app_logger.isEnabledFor(logging.DEBUG):
                    app_logger.debug("Creating {}.".format(module_name))
                self.unit_dic[module_name] = brica1.Module()  # New Module instance

        # SuperModules of consistency check
        for module, superModule in self.super_modules.items():
            if superModule not in self.module_dictionary:
                app_logger.error("Super Module {} is not defined!".format(superModule))
                return False
            # Loop check
            if self.__loop_check(superModule, module):
                app_logger.error("Loop detected while trying to add {} as a subunit to {}!".format(module, superModule))
                return False

        # SubModules of consistency check
        for superModule, subModules in self.sub_modules.items():
            for subModule in subModules:
                if subModule not in self.module_dictionary:
                    app_logger.error("Sub Module {} is not defined!".format(subModule))
                    return False
                # Loop check
                if self.__loop_check(superModule, subModule):
                    app_logger.error("Loop detected while trying to add {} as a subunit to {}!".format(
                        superModule, subModule))
                    return False

        # Port of consistency check
        for module_name in self.module_dictionary:
            ports = self.module_dictionary[module_name]["Ports"]
            if len(ports) == 0:
                app_logger.error("The specified module {} does not have the port!".format(module_name))
                return False
            for port in ports:
                if not module_name + "." + port in self.__ports:
                    app_logger.error("The specified module {} does not have the port!".format(module_name))
                    return False

        for port_name, v in self.__ports.items():
            # Fatal if the specified modules have not been defined.
            if "Module" not in v:
                app_logger.error("Module is not defined in the port {}!".format(port_name))
                return False

            module_name = v["Module"]
            if module_name not in self.module_dictionary:
                app_logger.error("Specified module {} is not defined in the port {}!".format(module_name, port_name))
                return False

            # Fatal if the shape has not been defined.
            if "Shape" not in v:
                app_logger.error("Shape is not defined in the port {}!".format(port_name))
                return False

            length = v["Shape"]
            if length < 1:
                app_logger.error("Incorrect length of Shape for the port {}!".format(port_name))
                return False

            # Fatal if the specified modules do not have the port, abort with a message.
            module = self.module_dictionary[module_name]
            pv = port_name.split(".")
            last_port_name = pv[len(pv) - 1]
            if last_port_name not in module["Ports"]:
                app_logger.error("Port {} is not defined in the module {}!".format(last_port_name, module_name))
                return False

            module = self.unit_dic[module_name]
            if v["IO"] == "Input":
                module.make_in_port(last_port_name, length)
                if app_logger.isEnabledFor(logging.DEBUG):
                    app_logger.debug("Creating an input port {} (length {}) to {}.".format(
                        last_port_name, length, module_name))
            elif v["IO"] == "Output":
                module.make_out_port(last_port_name, length)
                if app_logger.isEnabledFor(logging.DEBUG):
                    app_logger.debug("Creating an output port {} (length {}) to {}.".format(
                        last_port_name, length, module_name))

        # Connection of consistency check
        for k, v in self.__connections.items():
            # Fatal if the specified ports have not been defined.
            if not v[0] in self.__ports:
                app_logger.error("The specified port {} is not defined in connection {}.".format(v[0], k))
                return False
            if not v[1] in self.__ports:
                app_logger.error("The specified port {} is not defined in connection {}.".format(v[1], k))
                return False

            tp = v[0].split(".")
            to_port = tp[len(tp) - 1]
            fp = v[1].split(".")
            from_port = fp[len(fp) - 1]
            to_unit = self.__ports[v[0]]["Module"]
            from_unit = self.__ports[v[1]]["Module"]

            # if from_unit & to_unit belong to the same level
            if ((from_unit not in self.__super_sub_modules) and (to_unit not in self.__super_sub_modules)) or \
                    (from_unit in self.__super_sub_modules and to_unit in self.__super_sub_modules and (
                                self.__super_sub_modules[from_unit] == self.__super_sub_modules[to_unit])):
                try:
                    fr_port_obj = self.unit_dic[from_unit].get_out_port(from_port)
                    to_port_obj = self.unit_dic[to_unit].get_in_port(to_port)
                    if fr_port_obj.buffer.shape != to_port_obj.buffer.shape:
                        app_logger.error("Port dimension unmatch!")
                        return False
                    # Creating a connection
                    brica1.connect((self.unit_dic[from_unit], from_port), (self.unit_dic[to_unit], to_port))
                    if app_logger.isEnabledFor(logging.DEBUG):
                        app_logger.debug("Creating a connection from {} of {} to {} of {}".format(
                            from_port, from_unit, to_port, to_unit))
                except:
                    app_logger.error("adding a connection from {} to {} on the same level"
                                     " but not from an output port to an input port!".format(from_unit, to_unit))
                    return False
            # else if from_unit is the direct super module of the to_unit
            elif to_unit in self.__super_sub_modules and self.__super_sub_modules[to_unit] == from_unit:
                try:
                    fr_port_obj = self.unit_dic[from_unit].get_in_port(from_port)
                    to_port_obj = self.unit_dic[to_unit].get_in_port(to_port)
                    if fr_port_obj.buffer.shape != to_port_obj.buffer.shape:
                        app_logger.error("Port dimension unmatch!")
                        return False
                    # Creating a connection (alias)
                    self.unit_dic[to_unit].alias_in_port(self.unit_dic[from_unit], from_port, to_port)
                    if app_logger.isEnabledFor(logging.DEBUG):
                        app_logger.debug("Creating a connection (alias) from {} of {} to {} of {}.".format(
                            from_port, from_unit, to_port, to_unit
                        ))
                except:
                    app_logger.error("Error adding a connection from the super module {} to {} "
                                     "but not from an input port to an input port!".format(from_unit, to_unit))
                    return False
            # else if to_unit is the direct super module of the from_unit
            elif from_unit in self.__super_sub_modules and self.__super_sub_modules[from_unit] == to_unit:
                try:
                    fr_port_obj = self.unit_dic[from_unit].get_out_port(from_port)
                    to_port_obj = self.unit_dic[to_unit].get_out_port(to_port)
                    if fr_port_obj.buffer.shape != to_port_obj.buffer.shape:
                        app_logger.error("Port dimension unmatch!")
                        return False
                    # Creating a connection (alias)
                    self.unit_dic[from_unit].alias_out_port(self.unit_dic[to_unit], to_port, from_port)
                    if app_logger.isEnabledFor(logging.DEBUG):
                        app_logger.debug("Creating a connection (alias) from {} of {} to {} of {}.".format(
                            from_port, from_unit, to_port, to_unit
                        ))
                except:
                    app_logger.error("Error adding a connection from {} to its super module {} "
                                     "but not from an output port to an output port!".format(from_unit, to_unit))
                    return False
            # else connection level error!
            else:
                app_logger.error("Trying to add a connection between units {} and {} in a remote level!".format(
                    from_unit, to_unit
                ))
                return False

        return True

    def check_grounding(self):
        """
        Args:
          None
        return:
          true iff the network is grounded, i.e., every module at the bottom of the hierarchy
          has a component specification.
        """
        for module_name, v in self.module_dictionary.items():
            implclass = v["ImplClass"]
            if implclass != "":
                if app_logger.isEnabledFor(logging.DEBUG):
                    app_logger.debug("Use the existing ImplClass {} for {}.".format(implclass, module_name))
                try:
                    component_instance = eval(implclass + '()')  # New ImplClass instance
                except:
                    v = implclass.rsplit(".", 1)
                    mod_name = v[0]
                    class_name = v[1]
                    try:
                        mod = __import__(mod_name, globals(), locals(), [class_name], -1)
                        Klass = getattr(mod, class_name)
                        component_instance = Klass()
                    except:
                        app_logger.error("Module {} at the bottom not grounded as a Component!".format(module_name))
                        return False
                try:
                    module = self.unit_dic[module_name]
                    module.add_component(module_name, component_instance)
                    for port in module.in_ports:
                        length = module.get_in_port(port).buffer.shape[0]
                        component_instance.make_in_port(port, length)
                        component_instance.alias_in_port(module, port, port)
                    for port in module.out_ports:
                        length = module.get_out_port(port).buffer.shape[0]
                        component_instance.make_out_port(port, length)
                        component_instance.alias_out_port(module, port, port)
                except:
                    app_logger.error("Module {} at the bottom not grounded as a Component!".format(module_name))
                    return False
        return True

    def __set_modules(self, jsn):
        """ Add modules from the JSON description
        Args:
          None
        Returns:
          None
        """
        if "Modules" in jsn:
            modules = jsn["Modules"]
            for module in modules:
                if self.__set_a_module(module) is False:
                    return False
        else:
            app_logger.warning("No Modules in the language file.")

        return True

    def __set_a_module(self, module):
        if "Name" not in module:
            app_logger.error("Module name must be specified!")
            return False

        module_name = module["Name"].strip()
        if module_name == "":
            app_logger.error("Module name must be specified!")
            return False
        module_name = self.__prefix_base_name_space(module_name)  # Prefixing the base name space

        defined_module = None
        if module_name in self.module_dictionary:
            defined_module = self.module_dictionary[module_name]

        ports = []
        if "Ports" in module:
            ports = module["Ports"]
        # Multiple registration
        if defined_module:
            for p in defined_module["Ports"]:
                if p not in ports:
                    ports.append(p)

        implclass = ""
        if "ImplClass" in module:
            # if an implementation class is specified
            implclass = module["ImplClass"].strip()
        elif self.__type == "C":
            app_logger.error("ImplClass is necessary if the type C in the module {}!".format(module_name))
            return False
        # Multiple registration
        if defined_module:
            if implclass == "":
                implclass = defined_module["ImplClass"]
            else:
                if defined_module["ImplClass"] != "":
                    app_logger.warning("ImplClass {} of {} is replaced with {}.".format(
                        defined_module["ImplClass"], module_name, implclass))

        self.module_dictionary[module_name] = {"Ports": ports, "ImplClass": implclass}

        supermodule = ""
        if "SuperModule" in module:
            supermodule = module["SuperModule"].strip()
            supermodule = self.__prefix_base_name_space(supermodule)
        if supermodule != "":
            # Multiple registration
            if module_name in self.super_modules:
                app_logger.warning("Super module {} of {} is replaced with {}.".format(
                    self.super_modules[module_name], module_name, supermodule))
            self.super_modules[module_name] = supermodule
            self.__super_sub_modules[module_name] = supermodule

        if "SubModules" in module:
            for submodule in module["SubModules"]:
                if submodule != "":
                    submodule = self.__prefix_base_name_space(submodule)
                    if module_name not in self.sub_modules:
                        self.sub_modules[module_name] = []
                    self.sub_modules[module_name].append(submodule)
                    self.__super_sub_modules[submodule] = module_name

        if "Comment" in module:
            self.__comments["Modules." + module_name] = module["Comment"]

        return True

    def __prefix_base_name_space(self, name):
        if name.find(".") < 0:
            return self.base_name_space + "." + name
        else:
            return name

    def __loop_check(self, superunit, subunit):
        if superunit == subunit:
            return True
        val = superunit
        while val in self.__super_sub_modules:
            val = self.__super_sub_modules[val]
            if val == subunit:
                return True

        return False

    def __set_ports(self, jsn):
        """ Add ports from the JSON description
        Args:
          None
        Returns:
          None
        """
        if "Ports" in jsn:
            ports = jsn["Ports"]
            for port in ports:
                if self.__set_a_port(port) is False:
                    return False
        else:
            app_logger.warning("No Ports in the language file.")

        return True

    def __set_a_port(self, port):
        if "Name" in port:
            port_name = port["Name"].strip()
        else:
            app_logger.error("Name not specified while adding a port!")
            return False

        if "Module" in port:
            port_module = port["Module"].strip()
            port_module = self.__prefix_base_name_space(port_module)
        else:
            app_logger.error("Module not specified while adding a port!")
            return False
        port_name = port_module + "." + port_name

        defined_port = None
        if port_name in self.__ports:
            defined_port = self.__ports[port_name]

        # Multiple registration
        if defined_port:
            if port_module != defined_port["Module"]:
                app_logger.error("Module {} defined in the port {} is already defined as a module {}.".format(
                    port_module, port_name, self.__ports[port_name]["Module"]))
                return False

        if "Type" in port:
            port_type = port["Type"].strip()
            if port_type != "Input" and port_type != "Output":
                app_logger.error("Invalid port type {}!".format(port_type))
                return False
            elif defined_port and port_type != defined_port["IO"]:
                app_logger.error("The port type of port {} differs from previously defined port type!".format(
                    port_name))
                return False
        else:
            app_logger.error("Type not specified while adding a port!")
            return False

        if "Shape" in port:
            shape = port["Shape"]
            if len(shape) != 1:
                app_logger.error("Shape supports only one-dimensional vector!")
                return False
            if not isinstance(shape[0], int):
                app_logger.error("The value of the port is not a number!")
                return False
            if int(shape[0]) < 1:
                app_logger.error("Port dimension < 1!")
                return False
            self.__ports[port_name] = {"IO": port_type, "Module": port_module, "Shape": shape[0]}
        else:
            self.__ports[port_name] = {"IO": port_type, "Module": port_module}

        if "Comment" in port:
            self.__comments["Ports." + port_name] = port["Comment"]

        return True

    def __set_connections(self, jsn):
        """ Add connections from the JSON description
        Args:
          None
        Returns:
          None
        """
        if "Connections" in jsn:
            connections = jsn["Connections"]
            for connection in connections:
                if self.__set_a_connection(connection) is False:
                    return False
        else:
            if self.__type != "C":
                app_logger.warning("No Connections in the language file.")

        return True

    def __set_a_connection(self, connection):
        if "Name" in connection:
            connection_name = connection["Name"]
        else:
            app_logger.error("Name not specified while adding a connection!")
            return False

        defined_connection = None
        if connection_name in self.__connections:
            defined_connection = self.__connections[connection_name]

        if "FromModule" in connection:
            from_unit = connection["FromModule"]
            from_unit = self.__prefix_base_name_space(from_unit)
        else:
            app_logger.error("FromModule not specified while adding a connection!")
            return False
        if "FromPort" in connection:
            from_port = connection["FromPort"]
        else:
            app_logger.error("FromPort not specified while adding a connection!")
            return False
        if "ToModule" in connection:
            to_unit = connection["ToModule"]
            to_unit = self.__prefix_base_name_space(to_unit)
        else:
            app_logger.error("ToModule not specified while adding a connection!")
            return False
        if "ToPort" in connection:
            to_port = connection["ToPort"]
        else:
            app_logger.error("ToPort not specified while adding a connection!")
            return False

        # Multiple registration
        if defined_connection and defined_connection[0] != to_unit + "." + to_port:
            app_logger.error("Defined port {}.{} is different from the previous ones in connection {}!".format(
                to_unit, to_port, connection_name))
            return False
        if defined_connection and defined_connection[1] != from_unit + "." + from_port:
            app_logger.error("Defined port {}.{} is different from the previous ones in connection {}!".format(
                from_unit, from_port, connection_name))
            return False

        if "Comment" in connection:
            self.__comments["Connections." + connection_name] = connection["Comment"]

        self.__connections[connection_name] = (to_unit + "." + to_port, from_unit + "." + from_port)
        return True


class AgentBuilder:
    """
    The BriCA language interpreter.
    - creates a BriCA agent based on the file contents.
    """

    def __init__(self):
        self.INCONSISTENT = 1
        self.NOT_GROUNDED = 2
        self.COMPONENT_NOT_FOUND = 3
        self.unit_dic = None

    '''
    def create_agent(self, scheduler, network):
        if network.check_consistency() == False:
            return self.INCONSISTENT

        if network.check_grounding() == False:
            return self.NOT_GROUNDED

        for module, super_module in network.super_modules.items():
            if super_module in network.module_dictionary:
                network.unit_dic[super_module].add_submodule(module, network.unit_dic[module])
                if debug:
                    print "Adding a module " + module + " to " + super_module + "."

        # Main logic
        top_module = brica1.Module()
        for unit_key in network.unit_dic.keys():
            if not unit_key in network.super_modules:
                if isinstance(network.unit_dic[unit_key], brica1.Module):
                    top_module.add_submodule(unit_key, network.unit_dic[unit_key])
                    if debug:
                        print "Adding a module " + unit_key + " to a BriCA agent."
        agent = brica1.Agent(scheduler)
        agent.add_submodule("__Runtime_Top_Module", top_module)
        self.unit_dic = network.unit_dic
        return agent
    '''

    def create_agent(self, network):
        if network.check_consistency() is False:
            return self.INCONSISTENT

        if network.check_grounding() is False:
            return self.NOT_GROUNDED

        for module, super_module in network.super_modules.items():
            if super_module in network.module_dictionary:
                network.unit_dic[super_module].add_submodule(module, network.unit_dic[module])
                if app_logger.isEnabledFor(logging.DEBUG):
                    app_logger.debug("Adding a module {} to {}.".format(module, super_module))

        # Main logic
        top_module = brica1.Module()
        for unit_key in network.unit_dic.keys():
            if unit_key not in network.super_modules:
                if isinstance(network.unit_dic[unit_key], brica1.Module):
                    top_module.add_submodule(unit_key, network.unit_dic[unit_key])
                    if app_logger.isEnabledFor(logging.DEBUG):
                        app_logger.debug("Adding a module {} to a BriCA agent.".format(unit_key))
        # agent = brica1.Agent(scheduler)
        agent = brica1.Agent()
        agent.add_submodule("__Runtime_Top_Module", top_module)
        self.unit_dic = network.unit_dic
        return agent

    def get_modules(self):
        return self.unit_dic
