import requests
import json
from subprocess import check_output
from operator import or_
from functools import reduce
from gettext import gettext as _
from test_connection import is_online_sync
from requests_headers import GET_HEADERS


def get_all_interfaces():
    ip = json.loads(check_output("ip -j addr", shell=True))
    iface_l = list(
        filter(
            lambda ni: ni.valid and ni.interface_type != NetworkInterface.LOOPBACK,
            [NetworkInterface(adict) for adict in ip],
        )
    )
    return iface_l


def get_internet_interface():
    internet_iface = NetworkInterface(None, True)
    return (internet_iface.valid and internet_iface) or None


class NetworkInterface:
    INTERNET = "Internet"
    WIRELESS = "Wireless"
    WIRED = "Wired"
    MOBILE = "Mobile"
    LOOPBACK = "Loopback"
    VIRTUAL_BRIDGE = "Virtual bridge"
    TUNNEL = "Tunnel"
    WIREGUARD = "WireGuard"
    UNKNOWN = "Unknown"

    CATEGORY_REAL = (WIRELESS, WIRED, MOBILE)

    def __init__(self, addr_dict, internet=False):
        self.address = None
        self.interface = None
        self.interface_type = None
        self.location = None
        self.subnet_mask = 24
        if internet:
            # TODO: proper async
            if is_online_sync():
                for retry in range(0, 10):
                    res = requests.get(
                        "https://geoip.fedoraproject.org/city" if retry < 5 else "https://ifconfig.co/json",
                        timeout=10,
                        headers=GET_HEADERS,
                    )
                    if 200 <= res.status_code <= 299:
                        try:
                            geo = json.loads(res.text)
                            self.address = geo.get("ip", None)
                            self.interface = _("Public Internet")
                            self.interface_type = NetworkInterface.INTERNET
                            self.location = {
                                "city": geo.get("city") or _("Unknown city"),
                                "region": geo.get("region_name") or geo.get("region") or None,  # _('Unknown region'),
                                "country": geo.get("country_name") or geo.get("country") or _("Unknown country"),
                            }
                            break
                        except Exception:
                            continue
                    else:
                        continue
        else:
            if len(addr_dict.get("addr_info", [])) > 0:
                inet_list = list(filter(lambda d: d["family"] == "inet", addr_dict["addr_info"]))
                inet = inet_list[0] if len(inet_list) > 0 else None
                inet6_list = list(filter(lambda d: d["family"] == "inet6", addr_dict["addr_info"]))
                inet6 = inet6_list[0] if len(inet6_list) > 0 else None
                if inet is not None:
                    self.address = inet["local"]
                    self.subnet_mask = inet["prefixlen"]
                if inet6 is not None:
                    self.inet6_address = inet6["local"]
                self.interface = addr_dict["ifname"]
                self.interface_type = self.guess_interface_type(self.interface)
        self.valid = self.address is not None and self.interface is not None

    def guess_interface_type(self, iname):
        return (
            (iname == "lo" and NetworkInterface.LOOPBACK)
            or (reduce(or_, [sample in iname for sample in ("eth", "en", "em")]) and NetworkInterface.WIRED)
            or ("wl" in iname and NetworkInterface.WIRELESS)
            or ("wwan" in iname and NetworkInterface.MOBILE)
            or ("virbr" in iname and NetworkInterface.VIRTUAL_BRIDGE)
            or ("tun" in iname and NetworkInterface.TUNNEL)
            or ("wg" in iname and NetworkInterface.WIREGUARD)
            or NetworkInterface.UNKNOWN
        )

    def __repr__(self):
        return f"NetworkInterface {self.interface}, address: {self.address}"
