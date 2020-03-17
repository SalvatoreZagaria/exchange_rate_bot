import os
from selenium import webdriver
import sys
import datetime
import time


WEBSITE = "https://www.x-rates.com/table/?from=GBP&amount=1"


class ExchangeRateMonitor:
    def __init__(self, url):
        self.url = url
        self.chrome_driver_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "chromedriver.exe"
        )
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("window-size=1600x900")
        self.options.add_argument("headless")
        self.driver = webdriver.Chrome(options=self.options)
        self.table_xpath = "//table[@class='ratesTable']"

    def close(self):
        self.driver.quit()

    def get_single_rate(self, table_rows):
        for tr in table_rows.find_elements_by_xpath(".//tr"):
            row = [i.text for i in tr.find_elements_by_xpath(".//td")]
            try:
                if row[0] == "Euro":
                    return float(row[1])
            except IndexError:
                continue
        return None

    def get_rates(self):
        self.driver.get(self.url)
        table_rows = self.driver.find_elements_by_xpath(self.table_xpath)[0]
        gbp_eur = self.get_single_rate(table_rows)

        return gbp_eur

    def process_rates(self):
        gbp_eur = self.get_rates()

        if gbp_eur is None:
            print("[!] {} RATES NOT FOUND".format(datetime.datetime.now()))
            return

        print(gbp_eur)


if __name__ == "__main__":
    try:
        monitor = ExchangeRateMonitor(WEBSITE)
        monitor.process_rates()
        monitor.close()
    except Exception as e:
        print("Aborted")
        monitor.close()
        sys.exit(e)
