# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
Authors: Daniel Stock

Licensed under the Apache License, Version 2.0
See the file "LICENSE" for the full license governing this code.
"""

import datetime

from enum import Enum


class TypeDescriptor(str, Enum):
    """Enum of all supported type desciptors."""
    ECLASS = 'ECLASS'
    CDD = 'CDD'
    ETIM = 'ETIM'
    UNSPC = 'UNSPC'
    AAS = 'AAS'
    CUSTOM = 'CUSTOM'
    FINGERPRINT = 'FINGERPRINT'
