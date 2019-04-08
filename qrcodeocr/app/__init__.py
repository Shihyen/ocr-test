# -*- coding: utf-8 -*-
import argparse
import configparser
import logging.config
import os

# loading config
config = configparser.ConfigParser()
config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ini/config.ini'))
config.read(config_file)

# load logging
file_name = ("%s.%s.log" % (config['env']['source'], config['env']['env']))
logging.log_file_name = os.path.join(config['logging']['base_dir'], file_name)
logging_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ini/logging.ini'))
logging.config.fileConfig(logging_file)