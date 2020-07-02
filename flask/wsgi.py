from app import app as flask_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware


application = DispatcherMiddleware(flask_app, {
})