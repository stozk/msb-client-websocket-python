# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
Authors: Daniel Stock

Licensed under the Apache License, Version 2.0
See the file "LICENSE" for the full license governing this code.
"""

from .MetaData import MetaData


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
        self.dataFormat = dataFormat
        self.isArray = isArray
        self.typeDescription = typeDescription
        self._class = "CustomMetaData"
