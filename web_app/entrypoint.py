"""
Flask Application entrypoint.
"""

import os

from app import create_app as fia_create_app

settings_mod = os.getenv('APP_SETTINGS_MODULE') or 'config.development'
app = fia_create_app(settings_mod)

if __name__ == '__main__':
    debug_envs = [app.config['APP_ENV_TESTING'],
                  app.config['APP_ENV_DEVELOPMENT']]
    debug_mode = True if app.config['APP_ENV'] in debug_envs else False
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
