#!/usr/bin/env python
# pylint: disable=missing-docstring

import os
import sys

if __name__ == "__main__":

    # load the content of .env in the current environement
    env_filename = '.env2'

    if 'test' in sys.argv:
        env_filename = '.env.sample'
    if os.path.exists(env_filename):
        with open(env_filename) as f:
            env = dict([line.split('=', 1) for line in f.readlines()])
            for k in env:
                os.environ.setdefault(k, env[k].strip())
