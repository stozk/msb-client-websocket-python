# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
Authors: Daniel Stock

Licensed under the Apache License, Version 2.0
See the file "LICENSE" for the full license governing this code.
"""

from .MetaData import MetaData


class TypeDescription(MetaData):
    """Definition of functions to be provided via the MSB."""

    def __init__(
            self,
            type,
            id,
            location,
            selector="/",
            value=None
    ):
        """Initializes a new MetaData object.
        """
        super().__init__(value, selector)
        self.id = id
        self.location = location
        self.type = type
