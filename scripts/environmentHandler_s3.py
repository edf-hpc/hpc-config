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
import hashlib
import boto
import boto.s3
import boto.s3.connection
import shutil
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool

import logging
logger = logging.getLogger(__name__)
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

from environmentHandler import environmentHandlerInterface

class environmentHandler_s3(environmentHandlerInterface):

    def __init__(self,conf):
        environmentHandlerInterface.__init__(self, conf)

    def list(self):
        """List pushed environments in Ceph/S3 Bucket."""

        logger.info("S3 list: listing environments in bucket %s", self.conf.s3_bucket_name)

        bucket = self._bucket_conn_s3(self.conf)

        logger.info("S3 list: get remote objects list")
        objs = bucket.list(prefix=self.conf.destination_root)
        envs = []
        for obj in objs:
            name_members = obj.name.split('/')
            if len(name_members) == 3:
                envs.append((name_members[1], obj.last_modified))
        print(envs)
        result_s = super()._formatted_list_results(envs)

        logger.info("S3 list: available environments:\n%s", result_s)

    def upload(self):
        logger.info("S3 push: pushing data in bucket %s", self.conf.s3_bucket_name)

        bucket = self._bucket_conn_s3(self.conf)

        logger.info("S3 push: get remote objects list")
        obj_md5s = self._s3_list_md5(bucket, self.conf.destination)

        touched_objects = []

        self.handle_area(self.conf.areas, obj_md5s=obj_md5s, bucket=bucket, touched_objects=touched_objects)


        logger.info("S3 push: copying private files")
        dir_files = os.path.join(self.conf.destination, 'files')
        lst = self._s3_upload(self.conf.dir_files_private, bucket, dir_files, object_md5s=obj_md5s)
        touched_objects = list(set(touched_objects + lst))
        logger.info("S3 push: copying puppet conf")
        lst = self._s3_upload(self.conf.conf_puppet, bucket, self.conf.destination, object_md5s=obj_md5s)
        touched_objects = list(set(touched_objects + lst))
        logger.info("S3 push: copying hiera conf")
        lst = self._s3_upload(self.conf.conf_hiera, bucket, self.conf.destination, object_md5s=obj_md5s)
        touched_objects = list(set(touched_objects + lst))
        logger.info("S3 push: copying private cluster nodes description")
        lst = self._s3_upload(self.conf.nodes_private, bucket, self.conf.destination, object_md5s=obj_md5s)
        touched_objects = list(set(touched_objects + lst))

        logger.info("S3 push: Removing old files")
        self._s3_remove_old_objects(bucket, obj_md5s, touched_objects)

    def download(self):
        raise NotImplementedError("TODO")

    @environmentHandlerInterface.arealoop
    def handle_area(self, area, **kwargs):
        logger.info("S3 push: copying area %s tarball", area)
        area_dest = os.path.join(self.conf.destination, area)
        lst = self._s3_upload(self.conf.archive_path(area), kwargs.get('bucket'), area_dest, object_md5s=kwargs.get('obj_md5s'))
        touched_objects = kwargs.get('touched_objects')
        touched_objects = list(set(touched_objects + lst))

    def _s3_upload_file(self, source_file_path,
                        bucket,
                        destination_file_path,
                        object_md5s=None):
        #max size in bytes before uploading in parts. between 1 and 5 GB recommended
        max_size = 20 * 1000 * 1000
        #size of parts when uploading in parts
        part_size = 6 * 1000 * 1000

        if object_md5s is None:
            oject_md5s = {}

        # Check if the file has changed
        if destination_file_path in object_md5s.keys():
            remote_md5 = object_md5s[destination_file_path]
        else:
            remote_key = bucket.get_key(destination_file_path)
            if remote_key is not None:
                remote_md5 = remote_key.etag[1:-1]
            else:
                remote_md5 = None
        local_md5 = hashlib.md5(open(source_file_path, 'rb').read()).hexdigest()
        if remote_md5 == local_md5:
            logger.debug("S3 upload: MD5 Match for file %s", source_file_path)
            return
        else:
            logger.debug("S3 upload: MD5 Mismatch for file %s (%s != %s)",
                         source_file_path,
                         remote_md5,
                         local_md5)


        # Determine upload method
        filesize = os.path.getsize(source_file_path)
        if filesize > max_size:
            logger.debug("S3 upload: multipart upload for %s", source_file_path)
            mp = bucket.initiate_multipart_upload(destination_file_path,
                                                  policy='public-read')
            fp = open(source_file_path, 'rb')
            fp_num = 0
            while fp.tell() < filesize:
                fp_num += 1
                logger.debug("S3 upload: uploading part %i", fp_num)
                mp.upload_part_from_file(fp, fp_num, size=part_size)

            mp.complete_upload()
        else:
            logger.debug("S3 upload: singlepart upload for %s", source_file_path)
            k = boto.s3.key.Key(bucket)
            k.key = destination_file_path
            bytes_written = k.set_contents_from_filename(source_file_path,
                                                         policy='public-read')
            logger.debug("S3 upload: %d/%d bytes written for %s",
                         bytes_written, filesize, source_file_path)


    def _s3_upload(self, source_path,
                   bucket,
                   destination_path,
                   clean=True,
                   object_md5s=None):
        upload_file_paths = self._list_upload_file_paths(source_path)

        if object_md5s is None:
            object_md5s = {}
        pool = ThreadPool()
        results = {}

        dirs = []
        touched_objects = []


        # Upload the files
        for file_path in upload_file_paths:
            source_file_path, dest_file_path = self._get_full_paths(
                source_path, destination_path, file_path)

            # Create remote directory if necessary
            dest_dir_name = os.path.dirname(dest_file_path) + "/"
            while dest_dir_name not in dirs \
                    and dest_dir_name not in object_md5s.keys() \
                    and bucket.get_key(dest_dir_name) is None:
                logger.debug("S3 upload: Creating directory %s", dest_dir_name)
                dest_dir = bucket.new_key(dest_dir_name)
                dest_dir.set_contents_from_string('', policy='public-read')
                dirs.append(dest_dir_name)
                touched_objects.append(dest_dir_name)
                # Continue with parent
                dest_dir_name = os.path.dirname(dest_dir_name[:-1]) + "/"

            results[dest_file_path] = pool.apply_async(
                self._s3_upload_file,
                [source_file_path, bucket, dest_file_path, object_md5s]
            )
            touched_objects.append(dest_file_path)

        pool.close()
        finished = 0
        while finished < len(results):
            finished = 0
            for result in results.values():
                if result.ready():
                    finished += 1
            logger.info("S3 push: Transfered files %d/%d", finished, len(results))
            time.sleep(1)
        for dest_file_path, result in results.items():
            result.get()
        pool.join()
        return touched_objects

    def _s3_list_md5(self, bucket, prefix):
        keys = bucket.list(prefix=prefix)
        md5s = {}
        for key in keys:
            md5s[key.name] = key.etag[1:-1]
        return md5s

    def _s3_remove_old_objects(self, bucket, old_object_md5s, new_objects):
        """
            Remove all objects from the old list not in the new list.
        """
        key_names = []
        for object_name in old_object_md5s.keys():
            if object_name not in new_objects:
                if not object_name.endswith("/"):
                    logger.debug("S3 push: Removing old file: %s", object_name)
                    key_names.append(object_name)
                    continue
                empty=True
                for file_name in new_objects:
                    if file_name.startswith(object_name):
                        empty=False
                if empty:
                    logger.debug("S3 push: Removing old dir: %s", object_name)
                    key_names.append(object_name)
        logger.info("S3 push: %d files to remove.", len(key_names))
        result = bucket.delete_keys(key_names)
        error_count = len(result.errors)
        deleted_count = len(result.deleted)
        logger.debug("S3 push: %d deleted, %s errors", deleted_count, error_count)
        if error_count > 0:
            logger.error("S3 push: Failed to delete %d old keys", error_count)

    def _s3_rmrf(bucket, prefix):
        keys = bucket.list(prefix=prefix)
        pool = ThreadPool()
        results = []
        counter = 1
        key_group = []
        for key in keys:
            key_group.append(key)
            counter += 1
            if counter == 1000:
                results.append(
                    pool.apply_async(bucket.delete_keys, [key_group])
                )
                key_group=[]
                counter = 1
        results.append(
            pool.apply_async(bucket.delete_keys, [key_group])
        )
        pool.close()
        pool.join()
        deleted = 0
        errors = 0
        for result in results:
            report = result.get()
            deleted += len(report.deleted)
            errors += len(report.errors)
        logger.info("S3 push: Deleted %d keys, %d errors", deleted, errors)

    def _bucket_conn_s3(self, conf):
        """Connect to S3 server and return the bucket."""
        conn = boto.connect_s3(
            aws_access_key_id=conf.s3_access_key,
            aws_secret_access_key=conf.s3_secret_key,
            host=conf.s3_host,
            port=conf.s3_port,
            is_secure=False,
            calling_format=boto.s3.connection.OrdinaryCallingFormat(),
        )
        bucket = conn.get_bucket(conf.s3_bucket_name)
        bucket.set_acl('public-read')
        return bucket

