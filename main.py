'''this module is required by GCP to automatically find the entrypoint.'''
# TODO(Nico) configure your own gunicorn server and set an entrypoint
from app import create_app

app = create_app()

if __name__ == "__main__":

    app = create_app()
    app.run(debug=True, host='0.0.0.0', port='8000') #, ssl_context=('server.crt', 'server.key'))
    # this is to run app on secure server via localhost
    # https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https