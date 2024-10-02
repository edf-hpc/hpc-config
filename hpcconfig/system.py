#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 EDF SA
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

import platform
try:
    import distro
except:
    pass

def os_distribution():
    try:
        return platform.dist()[0]
    except:
        return distro.name().lower()

def os_major_version():
    try:
        return int(platform.dist()[1].split('.')[0])
    except:
        return int(distro.version().split('.')[0])
