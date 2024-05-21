from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import parse_qs
from .. import config

domain = config.domain

class BookNames(CrawlSpider):    
    name = "booknames"
    allowed_domains = [f"{domain}", "drive.google.com", "drive.usercontent.google.com"]
    start_urls = [f"https://{domain}/category/item/page/{num}" for num in range(1,85)]

    rules = (
        Rule(LinkExtractor(allow=f"https://{domain}"), callback="parse_item"),
    )

    def parse_item(self, response):
        download_link = response.css('.wp-block-button__link::attr(href)').get()

        if not download_link:
            download_link = response.css('.wp-element-button::attr(href)').get()
        
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
                
                download_link = f"https://drive.usercontent.google.com/u/0/uc?id={file_id}&export=download"
            
            file_name =  response.css(".entry-title::text").get()
            if file_name is None:
                file_name = file_id
            file_name = file_name+".pdf"
                
            yield {
                file_id: [file_name, download_link]
            }
