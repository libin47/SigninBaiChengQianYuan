import os
from datetime import timedelta
from app import create_app
from app.main import login_manager
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.config["SECRET_KEY"] = "dfduirtibs1231431"
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=2)

login_manager.init_app(app)
# m = Manager(app)

import traceback
traceback.print_exc()

# def make_shell_context():
#     return dict(app=app)
#
#
# m.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    port=os.getenv("PORT",8080)
    if os.getenv("ENV") == "prod":
        app.run(host="0.0.0.0",port=port,debug=False)
    else:
        app.run(host="0.0.0.0", port=port, debug=False)

