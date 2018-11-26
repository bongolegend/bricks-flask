'''this module is required by GCP to automatically find the entrypoint.'''
# TODO(Nico) configure your own gunicorn server and set an entrypoint
from app import create_app

app = create_app()