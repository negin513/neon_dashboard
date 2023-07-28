# see https://docs.bokeh.org/en/latest/docs/user_guide/server/app.html#ug-server-apps

from threading import Thread

def on_server_loaded(server_context):
    print("app_hook.py on_server_loaded START...")

    from .preload import Preload

    # for debugging I can limit the sites
    if False:
        Preload.neon_sites = Preload.neon_sites[0:4]

    Preload.run()
    print("app_hook.py on_server_loaded FINISHED")

def on_server_unloaded(server_context):
    pass

def on_session_created(session_context):
    pass

def on_session_destroyed(session_context):
    pass
