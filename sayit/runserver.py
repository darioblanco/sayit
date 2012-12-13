#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import argparse

from sayit import app
from sayit.settings import DEBUG, HOST


if __name__ == '__main__':
    """Runs the sayit application"""
    parser = argparse.ArgumentParser(description='Run the sayit webserver')
    parser.add_argument("--host", type=str, default=HOST,
                        help="Webserver host")
    parser.add_argument("--debug", action="store_true", default=DEBUG,
                        help="Set debug mode")
    args_dict = vars(parser.parse_args())
    app.run(host=args_dict['host'], debug=args_dict['debug'])
