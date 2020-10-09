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
import shutil
from datetime import datetime

import logging
logger = logging.getLogger(__name__)
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

from hpcconfig import environmentHandler as eh

class environmentHandler_posix(eh.environmentHandlerInterface):

    def __init__(self,conf):
        eh.environmentHandlerInterface.__init__(self, conf)

    def list(self):
        """List pushed environments in POSIX directory."""

        logger.info("posix list: in %s", self.conf.destination_root)

        if not os.path.isdir(self.conf.destination_root):
            logger.info("posix list: no environment")
            return

        env_dirs = sorted(os.listdir(self.conf.destination_root))
        # build list of envs tuples (name, mtime)
        envs = [ (env_dir,
                  datetime.utcfromtimestamp(
                    os.stat(os.path.join(self.conf.destination_root, env_dir)).st_mtime) \
                    .strftime('%Y-%m-%d %H:%M:%S'))
                 for env_dir in env_dirs ]
        result_s = super()._formatted_list_results(envs)

        logger.info("posix list: available environment:\n%s", result_s)

    def upload(self):
        if not os.path.isdir(self.conf.destination):
            logger.debug("posix push: create destination dir %s", self.conf.destination)
            os.makedirs(self.conf.destination, exist_ok=True)

        self.handle_area(self.conf.areas)

        dir_files = os.path.join(self.conf.destination, 'files')
        if os.path.isdir(dir_files):
            logger.debug("posix push: removing push private files dir %s", dir_files)
            shutil.rmtree(dir_files)

        logger.debug("posix push: copying private files")
        # copytree() default copy_function is shutil.copy2() which does not manage
        # directories. When the file is a symlink, copytree() resolve the link and
        # directly call copy2() with the target of the link. It fails with errno 21
        # when the target is a directory. To avoid this bug, use an alternate copy
        # function conf_copy() to properly handle symlinks on directories.
        shutil.copytree(self.conf.dir_files_private, dir_files, copy_function=self.conf.copy_fun)
        logger.debug("posix push: copying puppet conf")
        shutil.copy(self.conf.conf_puppet, self.conf.destination)
        logger.debug("posix push: copying hiera conf")
        shutil.copy(self.conf.conf_hiera, self.conf.destination)
        logger.debug("posix push: copying private cluster nodes description")
        shutil.copy(self.conf.nodes_private, self.conf.destination)

        # Set permissions
        for root, dirs, files in os.walk(self.conf.destination):
            for dir_name in dirs:
                os.chmod(os.path.join(root, dir_name), self.conf.posix_dir_mode)
            for file_name in files:
                os.chmod(os.path.join(root, file_name), self.conf.posix_file_mode)

    def download(self):
        raise NotImplementedError("TODO")

    @eh.environmentHandlerInterface.arealoop
    def handle_area(self, area):
        logger.debug("posix push: copying area %s tarball", area)
        area_dest = os.path.join(self.conf.destination, area)
        os.makedirs(area_dest, exist_ok=True)
        shutil.copy(self.conf.archive_path(area), area_dest)

