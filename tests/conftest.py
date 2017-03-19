import pytest


def pytest_addoption(parser):
    parser.addoption("--online", action="store_true",
                     help="run tests that hit online services")
