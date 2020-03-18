from bs4 import BeautifulSoup
import sys
import urllib.request


WEBSITE = "https://www.x-rates.com/table/?from=GBP&amount=1"


class ExchangeRateMonitor:
    def __init__(self, url):
        self.url = url

    def get_single_rate(self, table):
        tbody = table.find("tbody")
        for tr in tbody.find_all("tr"):
            row = [i.text for i in tr.find_all("td")]
            try:
                if row[0] == "Euro":
                    return float(row[1])
            except IndexError:
                continue
        return None

    def get_rates(self):
        page = urllib.request.urlopen(self.url)
        tree = BeautifulSoup(page, "html.parser")
        table = tree.find_all("table")[0]
        gbp_eur = self.get_single_rate(table)

        return gbp_eur

    def process_rates(self):
        gbp_eur = self.get_rates()

        return gbp_eur


if __name__ == "__main__":
    try:
        monitor = ExchangeRateMonitor(WEBSITE)
        print(monitor.process_rates())
    except Exception as e:
        print("Aborted")
        sys.exit(e)
