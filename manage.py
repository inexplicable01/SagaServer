#!/usr/bin/env python3.7
"""Django's command-line utility for administrative tasks."""
import os
import sys


# def main():
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
#     try:
#         from django.core.management import execute_from_command_line
#     except ImportError as exc:
#         raise ImportError(
#             "Couldn't import Django. Are you sure it's installed and "
#             "available on your PYTHONPATH environment variable? Did you "
#             "forget to activate a virtual environment?"
#         ) from exc
#     execute_from_command_line(sys.argv)
#
#
# if __name__ == '__main__':
#     main()

import hashlib

for file in os.listdir('Files'):
    print('filename\t',file)
    fileb = open(os.path.join('Files',file), 'rb')
    # fileb = open(filepath, 'rb')
    content=fileb.read()
    md5hash = hashlib.md5(content)
    md5 = md5hash.hexdigest()
    print('md5\t\t\t',md5)
    print('\n')
    open(os.path.join('Files',md5), 'wb').write(content)

