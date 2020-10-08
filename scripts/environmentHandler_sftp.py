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
import time
import stat
import socket
import paramiko
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool
import logging
logger = logging.getLogger(__name__)
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

from environmentHandler import environmentHandlerInterface


class environmentHandler_sftp(environmentHandlerInterface):


    def __init__(self,conf):
        environmentHandlerInterface.__init__(self, conf)
        self._sftp_host_directories = {} # global cache of remote directories

    def list(self):
        """List pushed environment asynchronously on all SFTP servers."""

        logger.info("SFTP list: list environments on hosts %s", self.conf.sftp_hosts)

        pool = Pool()
        results = {}
        for host in self.conf.sftp_hosts:
           results[host] = pool.apply_async(self._sftp_list_host, [host, self.conf])
        pool.close()
        finished = 0
        while finished < len(results):
            finished = 0
            for result in results.values():
                if result.ready():
                    finished += 1
            logger.info("SFTP list: Finished host %d/%d", finished, len(results))
            time.sleep(1)
        # Build a hash with string of formatted result as keys and list of hosts
        # having this result as values.
        all_hosts_envs = {}
        for host, result in results.items():
            envs = result.get()  # list of tuples
            result_s = super()._formatted_list_results(envs)
            if result_s in all_hosts_envs:
                all_hosts_envs[result_s].append(host)
            else:
                all_hosts_envs[result_s] = [ host ]
        pool.join()
        for envs_s, hosts in all_hosts_envs.items():
            logger.info("SFTP list: hosts: %s environments:\n%s", ','.join(hosts), envs_s)

    def upload(self):
        logger.info("SFTP push: pushing data on hosts %s", self.conf.sftp_hosts)

        pool = Pool()
        results = {}
        for host in self.conf.sftp_hosts:
           results[host] = pool.apply_async(self._sftp_push_host, [host, self.conf])
        pool.close()
        finished = 0
        while finished < len(results):
            finished = 0
            for result in results.values():
                if result.ready():
                    finished += 1
            logger.info("SFTP push: Finished host %d/%d", finished, len(results))
            time.sleep(1)
        for host, result in results.items():
            result.get()
        pool.join()

    def download(self):
        raise NotImplementedError("TODO")

    @environmentHandlerInterface.arealoop
    def handle_area(self, area, **kwargs):
        logger.debug("SFTP push: copying area %s tarball", area)
        area_dest = os.path.join(self.conf.destination, area)
        self._sftp_upload(self.conf.archive_path(area), kwargs.get('sftp_client'), area_dest)

    def test(self):
        print(self.conf.mode)

    def _sftp_is_dir(self, sftp_client, path):
        if sftp_client not in self._sftp_host_directories.keys():
            self._sftp_host_directories[sftp_client] = []
        if path in self._sftp_host_directories[sftp_client]:
            return True
        try:
            is_dir = stat.S_ISDIR(sftp_client.stat(path).st_mode)
        except FileNotFoundError:
            is_dir = False
        if is_dir:
            self._sftp_host_directories[sftp_client].append(path)
        return is_dir

    def _sftp_list_children(self, sftp_client, path):
        children_attr = sftp_client.listdir_attr(path)
        files = []
        directories = []
        for child_attr in children_attr:
            name = child_attr.filename
            if stat.S_ISDIR(child_attr.st_mode):
                directories.append(name)
                # cache result
                if sftp_client not in self._sftp_host_directories.keys():
                    self._sftp_host_directories[sftp_client] = []
                full_path = os.path.join(path, name)
                if full_path not in self._sftp_host_directories[sftp_client]:
                    self._sftp_host_directories[sftp_client].append(name)
            else:
                files.append(name)
        return directories, files

    def _sftp_rmrf(self, sftp_client, path):
        self._sftp_host_directories[sftp_client] = []
        if self._sftp_is_dir(sftp_client, path):
            directories, files = self._sftp_list_children(sftp_client, path)
            for directory in directories:
                directory_path = os.path.join(path, directory)
                self._sftp_rmrf(sftp_client, directory_path)
            for filename in files:
                file_path = os.path.join(path, filename)
                sftp_client.remove(file_path)
            sftp_client.rmdir(path)
        else:
            try:
                sftp_client.remove(path)
                logger.debug("SFTP: Removing: %s" % path)
            except FileNotFoundError:
                logger.debug("SFTP: Try to remove a missing file: %s" % path)
        self._sftp_host_directories[sftp_client] = []

    def _sftp_mkdir(self, sftp_client, path, mode=0o755):
        if self._sftp_is_dir(sftp_client, path):
            return
        else:
            parent = os.path.dirname(path[:-1])
            self._sftp_mkdir(sftp_client, parent, mode)
        sftp_client.mkdir(path)
        sftp_client.chmod(path, mode)

    def _sftp_upload(self, source_path, sftp_client, destination_path, clean=True):
        upload_file_paths = self._list_upload_file_paths(source_path)

        for file_path in upload_file_paths:
            source_file_path, dest_file_path = self._get_full_paths(
                source_path, destination_path, file_path)
            # Create remote directory if necessary
            dest_dir_name = os.path.dirname(dest_file_path)
            self._sftp_mkdir(sftp_client, dest_dir_name)
            # Upload
            sftp_client.put(source_file_path, dest_file_path, confirm=False)
            # Set Perms
            sftp_client.chmod(dest_file_path, 0o644)

    def _sftp_connect(self, host, conf, verb):
        """Connect to SFTP server host. Verb is used in prefix of log messages."""
        key = paramiko.RSAKey.from_private_key_file(conf.sftp_private_key)
        username = conf.sftp_username

        try:
            transport = paramiko.Transport((host, 22))
            transport.connect(username=username, pkey=key)
        except socket.gaierror as e:
            logger.error("SFTP %s: Failed to connect to host %s", verb, host)
            logger.info("SFTP %s: Connection error: %s.", verb, e)
            return
        except paramiko.ssh_exception.SSHException as e:
            logger.error("SFTP %s: SSH failed to %s@%s", verb, username, host)
            logger.info("SFTP %s: SSH error: %s.", verb, e)
            return
        return paramiko.SFTPClient.from_transport(transport)

    def _sftp_push_host(self, host, conf):

        sftp_client = self._sftp_connect(host, conf, verb='push')

        logger.debug("SFTP push: Cleaning destination %s", conf.destination)
        self._sftp_rmrf(sftp_client, conf.destination)

        self.handle_area(self.conf.areas, sftp_client=sftp_client)

        logger.debug("SFTP push: copying private files")
        dir_files = os.path.join(conf.destination, 'files')
        self._sftp_upload(conf.dir_files_private, sftp_client, dir_files)
        logger.debug("SFTP push: copying puppet conf")
        self._sftp_upload(conf.conf_puppet, sftp_client, conf.destination)
        logger.debug("SFTP push: copying hiera conf")
        self._sftp_upload(conf.conf_hiera, sftp_client, conf.destination)
        logger.debug("SFTP push: copying private cluster nodes description")
        self._sftp_upload(conf.nodes_private, sftp_client, conf.destination)

    def _sftp_list_host(self, host, conf):
        """Returns a list of tuples with filename and mtime of pushed environments
           on a specific SFTP server."""
        sftp_client = self._sftp_connect(host, conf, verb='list')

        results = []
        for attr in sftp_client.listdir_iter(conf.destination_root):
            results.append((attr.filename,
                            datetime.utcfromtimestamp(attr.st_mtime) \
                              .strftime('%Y-%m-%d %H:%M:%S')))

        return sorted(results)

