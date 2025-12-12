import os

def load_config(app, overrides):
    if os.path.exists(os.path.join('./App', 'custom_config.py')):
        app.config.from_object('App.custom_config')
    else:
        app.config.from_object('App.default_config')
    app.config.from_prefixed_env()

    # Production DB robustness (Render Postgres): avoid stale pooled connections.
    # Only apply to Postgres URLs.
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI') or ''
    if isinstance(db_uri, str) and db_uri.startswith(('postgres://', 'postgresql://')):
        engine_opts = app.config.get('SQLALCHEMY_ENGINE_OPTIONS') or {}
        # Keep connection counts low on free-tier services (multiple workers).
        engine_opts.setdefault('pool_pre_ping', True)
        engine_opts.setdefault('pool_recycle', 280)
        engine_opts.setdefault('pool_size', 2)
        engine_opts.setdefault('max_overflow', 1)
        engine_opts.setdefault('pool_timeout', 30)

        # Ensure SSL when the connection string doesn't specify it.
        if 'sslmode=' not in db_uri:
            connect_args = engine_opts.get('connect_args') or {}
            connect_args.setdefault('sslmode', 'require')
            engine_opts['connect_args'] = connect_args

        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_opts

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['UPLOADED_PHOTOS_DEST'] = "App/uploads"
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
    app.config["JWT_COOKIE_SECURE"] = True
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config['FLASK_ADMIN_SWATCH'] = 'darkly'
    for key in overrides:
        app.config[key] = overrides[key]