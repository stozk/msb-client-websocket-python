# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
Authors: Daniel Stock

Licensed under the Apache License, Version 2.0
See the file "LICENSE" for the full license governing this code.
"""

import json
import copy

from .ComplexDataFormat import ComplexDataFormat
from .DataFormat import DataFormat
import datetime


class MetaDataDefinition:
    """Definition of functions to be provided via the MSB."""

    def __init__(
            self,
            name,
            type,
            description,
            dataFormat
    ):
        """Initializes a new MetaData object.
        """
        self.type = type
        self.name = name
        self.description = description
        self.dataFormat = dataFormat
