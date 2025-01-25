# FILE: /vsports/vsports/vsports/__init__.py
""" 
This file is used to mark the directory as a Python package. 
It can also be used to define the public API of the package by importing necessary classes or functions.
"""

from .vsports import VsportsAPI  # Importing the VsportsAPI class for public access

__all__ = ['VsportsAPI']  # Defining the public API of the package

