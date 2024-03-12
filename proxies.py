import requests


class Proxy:
    def __init__(self):
        self.api: any = None
        self.proxies = {}
        self.valid_proxies = []

    def __len__(self):
        return len(self.proxies)

    def __setitem__(self, key, value):
        self.proxies[key] = value

    def __getitem__(self, item):
        return self.proxies[item]

    def __delitem__(self, key):
        del self.proxies[key]

    def check_valid_proxies(self, proxies):
        if len(self.proxies) > 0:
            try:
                for proxie in proxies:
                    if requests.get(self.__getitem__(proxie)).status_code == 200:
                        self.valid_proxies.append(proxie)

                    else:
                        continue

            except Exception as e:
                return str(e)

        else:
            return "Proxie list must be greater than 0"

    def get_proxies_from_web(self, url):
        pass

    def get_proxies_from_api(self, api_url):
        pass
