# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
Authors: Daniel Stock

Licensed under the Apache License, Version 2.0
See the file "LICENSE" for the full license governing this code.
"""
import json
from datetime import datetime

from .ComplexDataFormat import ComplexDataFormat
from .DataFormat import DataFormat
from .DataType import DataType, convertDataType
from .MetaData import MetaData
import copy


class CustomMetaData(MetaData):
    """Definition of functions to be provided via the MSB."""

    def __init__(
            self,
            name,
            description,
            typeDescription=None,
            selector="/",
            value=None,
            dataFormat=None,
            isArray=False
    ):
        """Initializes a new MetaData object.
        """
        super().__init__(value, selector)
        self.name = name
        self.description = description
        self.isArray = isArray
        self.typeDescription = typeDescription
        self._class = "CustomMetaData"
        if (
            isinstance(dataFormat, DataFormat)
            or isinstance(dataFormat, ComplexDataFormat)
        ):
            # make a deep copy of the root dataformat
            self.dataFormat = copy.deepcopy(dataFormat).getDataFormat()
                # and add all nested data formats
            for df_key in list(dataFormat.nested_cdf.keys()):
                if df_key not in self.dataFormat:
                    self.dataFormat[df_key] = dataFormat.nested_cdf[df_key].dataFormat[df_key]
                self.df = dataFormat
        elif isinstance(dataFormat, DataType):
            self.dataFormat = DataFormat(dataFormat, isArray).getDataFormat()
            self.df = convertDataType(dataFormat)
        elif type(dataFormat) == type(datetime):
            self.dataFormat = DataFormat(dataFormat, isArray).getDataFormat()
            self.df = datetime.datetime
        elif dataFormat is None:
            self.dataFormat = None
            self.df = None
        else:
            # also support the definition of hte dattaformat as json object
            try:
                # check is the dataformat already a valid json object
                if "dataObject" in dataFormat:
                    json_object = dataFormat
                # otherwise check if it is a valid json string that can loaded as json object
                else:
                    json_object = json.loads(dataFormat)
                    # check if it json specifies simple data format
                    # otherwise it is a complex on and used without changes
                    if "dataObject" not in json_object:
                        json_object = {"dataObject": json_object}
                self.dataFormat = json_object
            except Exception:
                self.dataFormat = DataFormat(dataFormat, isArray).getDataFormat()
            self.df = dataFormat