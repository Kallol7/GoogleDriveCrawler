from scrapy.http import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import parse_qs

domain = "#domain_url"

class GoogleDriveCrawlerSpider(CrawlSpider):
    name = "googledrive"
    allowed_domains = [f"{domain}", "drive.google.com", "drive.usercontent.google.com"]
    start_urls = [f"https://{domain}/category/genre/page/{num}" for num in range(1,)]

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
                

                file_name =  f"{file_id}"+".pdf"
                
                download_link = f"https://drive.usercontent.google.com/u/0/uc?id={file_id}&export=download"
                

            yield Request(
                download_link, callback=self.save_file, 
                cb_kwargs={"file_name":file_name}
            )

    def save_file(self, response, file_name):
        item = {'file_urls': [response.url], 'files': [file_name]}
        yield item
