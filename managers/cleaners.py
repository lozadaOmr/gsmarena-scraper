from urlparse import urlparse
from .const import DEFAULT_FIELDNAMES
from .utils import dict_mapper


class CleanerManager(object):
    cleaner_providers = {}

    def add_cleaner_provider(self, domain):
        def wrapper(fn):
            self.cleaner_providers[domain] = fn
            return fn
        return wrapper

    def clean(self, url, data, fields=[]):
        if not url:
            return None

        parsed_uri = urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)

        if domain not in self.cleaner_providers:
            return None

        if not fields:
            fields = DEFAULT_FIELDNAMES

        returned_data = self.cleaner_providers[domain](data)

        for field in filter(lambda x: x not in fields, returned_data):
            returned_data.pop(field)

        return returned_data


cleaner_manager = CleanerManager()


@cleaner_manager.add_cleaner_provider("http://www.gsmarena.com")
def gsmarena(data):
    return data


@cleaner_manager.add_cleaner_provider("http://www.mobosdata.com")
def mobosdata(data):
    maps = [
        ("Model", ["also known as", "general name"]),
        ("GPRS", "gprs"),
        ("2G bands", ["2g gsm frequency", "2g cdma frequency", "2g cdma2000 frequency"]),
        ("Speed", "cpu speed"),
        ("3G bands", ["3g td-scdma frequency", "3g td-hspa frequency", "3g umts(w-cdma) frequency"]),
        ("EDGE", "edge"),
        ("Status", "availability"),
        ("SIM", "SIM type"),
        ("4G bands", ["4g lte(lte-a) frequency", "4g td-lte frequency"]),
        ("Announced", "availability"),
        ("Dimensions", "dimension"),
        ("Weight", "weight"),
        ("Resolution", ["display resolution-pixel", "display ppi"]),
        ("Type", "display touchscreen surface"),
        ("Size", "display diagonal"),
        ("OS", ["os", "os version"]),
        ("CPU", ["cpu speed"]),
        ("GPU", ["gpu speed"]),
        ("Internal", "internal"),
        ("Card slot", "card slot comment"),
        ("Secondary", "secondary camera"),
        ("Video", "video comment"),
        ("Primary", "pixels"),
        ("Loudspeaker", "loudspeaker"),
        ("3.5mm jack", "headphone jack"),
        ("Alert types", "alert types"),
        ("WLAN", "wlan comment"),
        ("USB", ["usb type", "usb version"]),
        ("Infrared port", "infrared port"),
        ("Bluetooth", "bluetooth version"),
        ("Radio", "fm radio"),
        ("GPS", "gps comment"),
        ("Messaging", "messaging sms"),
        ("Sensors", "sensors"),
        ("Java", "java comment"),
        ("Browser", "browser type"),
        ("Talk time", "talk time"),
        ("Stand-by", "stand by"),
        ("Music play", "music play"),
        ("Phonebook", "phonebook"),
        ("Call records", "call records"),
        ("Keyboard", "keyboard type"),
        ("NFC", "nfc"),
        ("Alarm", "alarm"),
    ]

    return dict_mapper(data, maps)


@cleaner_manager.add_cleaner_provider("http://www.phonearena.com")
def phonearena(data):
    maps = [
        ("2G bands", "GSM"),
        ("3G bands", "UMTS"),
        ("Status", "Officially announced"),
        ("4G bands", "Data"),
        ("Announced", "Officially announced"),
        ("Dimensions", "Dimensions"),
        ("Weight", "Weight"),
        ("Resolution", ["Resolution", "Pixel density"]),
        ("Type", "Technology"),
        ("Size", "Physical size"),
        ("OS", "OS"),
        ("CPU", "Processor"),
        ("Internal", "Built-in storage"),
        ("Card slot", "Storage expansion"),
        ("Secondary", "Front-facing camera"),
        ("Video", "Camcorder"),
        ("Primary", "Camera"),
        ("Loudspeaker", "Speakers"),
        ("3.5mm jack", "Speakers"),
        ("WLAN", "Wi-Fi"),
        ("USB", "USB"),
        ("Bluetooth", "Bluetooth"),
        ("GPS", "Positioning"),
        ("Sensors", "Sensors"),
        ("Talk time", "Talk time"),
        ("Stand-by", "Stand-by time"),
        ("Music play", "Music player"),
        ("Colors", "Colors"),
        ("Battery life", "Capacity"),
        ("NFC", "Other"),
        ("Manufacturer","manufacturer"),
    ]

    return dict_mapper(data, maps)


@cleaner_manager.add_cleaner_provider("http://imeidata.com")
def imeidata(data):
    maps = [
        ("Model", "model")
        ("Band", "band")
        ("Manufacturer","manufacturer"),
    ]

    return dict_mapper(data, maps)