from gi.repository import Gio

__HOSTNAME = "gnome.org"


def is_online(callback):
    def __async_cb(src, a_res, data):
        res = False
        try:
            res = Gio.NetworkMonitor.get_default().can_reach_finish(a_res)
        except Exception:
            import traceback

            traceback.print_exc()
            pass
        callback(res)

    Gio.NetworkMonitor.get_default().can_reach_async(
        Gio.NetworkAddress(hostname=__HOSTNAME), None, __async_cb, None
    )


def is_online_sync() -> bool:
    try:
        return Gio.NetworkMonitor.get_default().can_reach(
            Gio.NetworkAddress(hostname=__HOSTNAME), None
        )
    except Exception:
        pass
    return False
