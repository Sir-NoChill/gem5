# Copyright (c) 2021 The Regents of The University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from collections import defaultdict
from datetime import datetime
from typing import (
    Dict,
    List,
    Optional,
    Union,
)

from .group import Group
from .statistic import Statistic
from .timeconversion import TimeConversion


class SimStat(Group):
    """
    Contains all the statistics for a given simulation.
    """

    def __init__(
        self,
        creation_time: Optional[datetime] = None,
        time_conversion: Optional[TimeConversion] = None,
        simulated_begin_time: Optional[Union[int, float]] = None,
        simulated_end_time: Optional[Union[int, float]] = None,
        **kwargs: Dict[str, Union[Group, Statistic, List[Group]]],
    ):
        super().__init__(
            creation_time=creation_time,
            time_conversion=time_conversion,
            simulated_begin_time=simulated_begin_time,
            simulated_end_time=simulated_end_time,
            **kwargs,
        )

    @classmethod
    def from_string(cls, s: str) -> dict:
        """
        Parses the stats.txt file back into a dictionary of statistics.

        Due to the bizarre json serialization of the SerializableStat
        class, deserialization does not work by default. In order
        to return the collected statistics from a multisim run,
        we need to parse the stats.txt file.
        """

        # Construct the nested dictionary
        def nested_dict():
            return defaultdict(nested_dict)

        def remove_spaces(l):
            while "" in l:
                l.remove("")
            return l

        # Initialize the stats
        stats = nested_dict()

        for line in s.split("\n"):
            # remove newlines and delimiting lines
            if line == "" or line.startswith("-"):
                continue

            kv_set = line.split(" ")
            remove_spaces(kv_set)

            try:
                if "%" in kv_set[2]:
                    # Parse distributions
                    key, value = kv_set[0], [kv_set[1], kv_set[2], kv_set[3]]
                else:
                    # Parse single values
                    key, value = kv_set[0], kv_set[1]
            except IndexError:
                print(f"Failed to parse line '{line}'")
                continue

            # Break into substats
            sections = key.split(".")

            acc = stats
            for section in sections[:-1]:
                acc = acc[section]

            acc[sections[-1]] = value

        return stats
