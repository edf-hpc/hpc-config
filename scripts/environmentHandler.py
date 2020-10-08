#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 EDF SA
# Contact:
#       CCN - HPC <dsp-cspit-ccn-hpc@edf.fr>
#       1, Avenue du General de Gaulle
#       92140 Clamart
#
# Authors: CCN - HPC <dsp-cspit-ccn-hpc@edf.fr>
#
# This file is part of hpc-config.
#
# hpc-config is free software: you can redistribute in and/or
# modify it under the terms of the GNU General Public License,
# version 2, as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with hpc-config. If not, see
# <http://www.gnu.org/licenses/>.

import os
from abc import ABCMeta, abstractmethod 
from functools import wraps
import logging
logger = logging.getLogger(__name__)
import sys

class environmentHandlerInterface(metaclass=ABCMeta):

    def __init__(self,conf):
        self.conf = conf

    def arealoop(func):
        @wraps(func)
        def ret_func(self, areas, **kwargs):
            for area in areas:
                func(self, area, **kwargs)
        return ret_func

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def upload(self):
        pass

    @abstractmethod
    def download(self):
        pass

    @staticmethod
    def _formatted_list_results(envs):
        """Compose multiline string of formatted results w/ list comprehension
           on a list of tuples (filename, mtime as string)."""
        return '\n'.join([ "  - %-20s [%s]" % (env[0], env[1])
                       for env in envs ])

    def _list_upload_file_paths(self, source_path):
        logger.debug('Upload path: %s', source_path)
        # List files to upload
        upload_file_paths = []
        if os.path.isfile(source_path):
            relative_path = os.path.basename(source_path)
            upload_file_paths.append(relative_path)
        for (current_dir, subdirs, filenames) in os.walk(source_path, followlinks=True):
            for filename in filenames:
                absolute_path = os.path.join(current_dir, filename)
                # remove the source path and first /
                relative_path = absolute_path[(len(source_path)+1):]
                upload_file_paths.append(relative_path)
        return upload_file_paths

    def _get_full_paths(self, source_path, destination_path, file_path):
        # Determine file paths
        if os.path.isfile(source_path):
            source_file_path = source_path
        else:
            source_file_path = os.path.join(source_path, file_path)
        logger.debug("Source file path is: %s (%s, %s)", source_file_path, source_path, file_path)
        dest_file_path = os.path.join(destination_path, file_path)
        logger.debug("Dest file path is: %s (%s, %s)", dest_file_path, destination_path, file_path)
        return source_file_path, dest_file_path

class environmentHandlerFactory(object):

    def __new__(cls ,conf):
        if conf.mode == 'posix':
            from environmentHandler_posix import environmentHandler_posix
            return environmentHandler_posix(conf)
        elif conf.mode == 'sftp':
            from environmentHandler_sftp import environmentHandler_sftp
            return environmentHandler_sftp(conf)
        elif conf.mode == 's3':
            from environmentHandler_s3 import environmentHandler_s3
            return environmentHandler_s3(conf)
        else:
            raise NotImplementedError("invalid configuration mode provided", conf.mode)

