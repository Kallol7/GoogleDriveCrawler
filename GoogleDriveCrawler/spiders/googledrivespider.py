import os
import logging
from scrapy.http import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import parse_qs
from .. import config

domain = config.domain
start_url = config.start_url

class GoogleDriveCrawlerSpider(CrawlSpider):
    custom_settings = {
        "ROBOTSTXT_OBEY" : True,
        # "ITEM_PIPELINES": {
        #     "GoogleDriveCrawler.pipelines.CustomFilesPipeline": 1,
        # },
        # "FILES_STORE" : "downloads",
        # "FILES_EXPIRES" : 7200, # 2 hours
        "DOWNLOAD_WARNSIZE" : 100 * 1024 * 1024,
        "AUTOTHROTTLE_ENABLED" : True,
        "AUTOTHROTTLE_START_DELAY" : 5,
        "AUTOTHROTTLE_MAX_DELAY" : 60,
        "AUTOTHROTTLE_TARGET_CONCURRENCY" : 1.0,
        "AUTOTHROTTLE_DEBUG" : False,
        'RETRY_TIMES': 5,
        'DOWNLOAD_TIMEOUT': 180,  # 3 min, increase for large files
        'DOWNLOAD_FAIL_ON_DATALOSS': False,  # defult: False
    }

    # scrapy crawl googledrive -O data.json
    name = "googledrive"
    allowed_domains = [f"{domain}", "drive.google.com", "drive.usercontent.google.com"]
    start_urls = [f"{start_url}/page/{num}" for num in range(1,)]

    rules = (
        Rule(LinkExtractor(allow=f"https://{domain}"), callback="parse_item"),
    )

    def parse_item(self, response):
        download_link = response.css(".wp-block-button__link::attr(href)").get()

        if not download_link:
            download_link = response.css(".wp-element-button::attr(href)").get()
        
        if download_link:
            if "export=download" in download_link:
                file_id = parse_qs(download_link).get("id")
                if file_id:
                    file_id = file_id[0]
                    file_name =  f"{file_id}"+".pdf"
                elif "id=" in download_link:
                    splits= download_link.split("id=")
                    if len(splits)>1:
                        l1 = splits.split("/")[0]
                        l2 = splits.split("?")[0]
                        if len(l1)<len(l2):
                            file_id = l1
                        else:
                            file_id = l2
                        
                        if file_id:
                            file_name = f"{file_id}"+".pdf"
                        else:
                            return
                else: # no id inside url found
                    raise Exception("Link doesn't have id")
            else: # "export=download" NOT IN download_link:
                file_id = download_link.split("/")
                if len(file_id)<5:
                    return
                else:
                    file_id=file_id[5]
                

                file_name =  f"{file_id}"+".pdf"
                
                download_link = f"https://drive.usercontent.google.com/u/0/uc?id={file_id}&export=download"
                
            file_name =  response.css(".entry-title::text").get()
            if file_name is None:
                file_name = file_id
            file_name = file_name+".pdf"

            if "drive" not in download_link:
                return

            yield Request(
                    download_link, callback=self.save_file, 
                    cb_kwargs={"download_link": download_link,"file_name": file_name}
                )
    
    def save_file(self, response, download_link, file_name, __first_call=[True]):
        if response.status != 200:
            logging.error(f"Failed to download file: {response.url} with status {response.status}")
            return
        
        if __first_call[0]:
            if not os.path.exists("downloads"):
                os.mkdir("downloads")
            __first_call[0] = False

        file_path = f"downloads/{file_name}"

        with open(file_path, "wb") as f:
            f.write(response.body)

        logging.info(f"File saved: {file_path}")

        yield {
            "file_name": file_name,
            "file_path": file_path,
            "url": download_link
        }
