#!/usr/bin/env python3.11
from dataclasses import dataclass

# These are the codes for Flex (spare) blocks
# Semester 1 and 2
flex: tuple = ("XAT--12A-S", "XAT--12B-S")

# Global function
exists = lambda n : True if n not in ('', None) else False

# Global data class
@dataclass
class Error:
  Title: str
  Description: str

  def __init__(self, title: str, description: str):
    self.Title = title
    self.Description = description
