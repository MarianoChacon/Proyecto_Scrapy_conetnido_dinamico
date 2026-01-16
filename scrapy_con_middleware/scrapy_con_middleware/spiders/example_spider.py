import scrapy
from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy_playwright.page import PageMethod
from scrapy.utils.project import get_project_settings

class ExampleSpider(scrapy.Spider):
    name = "example_spider"
    start_urls = ["https://boardgamegeek.com/boardgame/224517/brass-birmingham"]
    parent_folder = Path(__file__).parent
    source_folder = parent_folder.parent.parent.parent
    dataset_folder = (source_folder.parent/ 'dataset').resolve()
    custom_settings = {
    'FEEDS': {str(dataset_folder) + '/Salida.csv': {'format': 'csv', 'encoding':'latin', 'delimiter': ';', 'overwrite': True}}
    }
    async def start(self):
        yield scrapy.Request(
            self.start_urls[0],
            meta={
                "playwright": True,
                # "playwright_context": "mobile",
                "playwright_page_methods": [
                    # Esperamos a que un selector específico dinámico cargue 
                     PageMethod("wait_for_selector", "h1 a", state="attached", timeout=10000),
                    # Espera 10 segundos a que cargue
                    PageMethod("wait_for_timeout", 10000),
                    # ESto hace un screenshot de la página scrapeada
                    PageMethod("screenshot", path="evidencia.png", full_page=True),

                ],
            },
            callback=self.parse
        )

    async def parse(self, response):
        # lo siguiente guarda el html que escrapea:
        with open("debug_page.html", "wb") as f:
            f.write(response.body)
        #for value in response.xpath('//li[@class="gameplay-item"]/p["$0"]/meta["$0"]').getall():
        #for value in response.xpath('//*[@id="mainbody"]/div[2]/div/div[2]/div[2]/ng-include/div/ng-include/div/div[2]/div[2]/div[1]/div/div[2]/hgroup/h1/a/span').getall():
        #    yield {'valor':value}
        nombre = response.css('h1 a').get()
        yield {
            "nombre": nombre.strip() if nombre else 'No encontrado'
        }


def execute_spider():
    # Obtenemos los settings base
    settings = get_project_settings()
    
    # Forzamos la configuración de Playwright
    settings.update({
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
    })

    process = CrawlerProcess(settings)
    process.crawl(ExampleSpider)
    process.start()