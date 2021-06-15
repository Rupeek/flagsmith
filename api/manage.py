#!/usr/bin/env python
import os
import sys

from environs import Env
env = Env()
env.read_env()

if __name__ == "__main__":
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.local")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
