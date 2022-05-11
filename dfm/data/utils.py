"""Utilities script for data functions.

"""

from dateutil.parser import parse


def to_datetime(example, date_column="created_at"):
    """converts datasets columns to date time"""
    example[date_column] = parse(example[date_column])
    return example
