import os
from gunicorn.app.base import BaseApplication
from main import app 

class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    options = {
        'bind': f'0.0.0.0:{port}',
        'workers': 1,
        'threads': 0,
    }

    StandaloneApplication(app, options).run()
