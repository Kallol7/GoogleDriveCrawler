from scrapy.pipelines.files import FilesPipeline

class CustomFilesPipeline(FilesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None, __i = [0]):

        try:
          file_name = item["file_name"]
        except Exception:
          file_name = __i[0]+".pdf"
          __i[0]+=1

        return f"full/{file_name}"

"""
The typical workflow, when using the FilesPipeline goes like this:
  1. In a Spider, you scrape an item and put the URLs of the desired into a file_urls field.
    
  2. The item is returned from the spider and goes to the item pipeline.
    
  3. When the item reaches the FilesPipeline, the URLs in the file_urls field are 
  scheduled for download using the standard Scrapy scheduler and downloader 
  (which means the scheduler and downloader middlewares are reused), 
  but with a higher priority, processing them before other pages are scraped. 
  The item remains “locked” at that particular pipeline stage 
  until the files have finish downloading (or fail for some reason).

  4. When the files are downloaded, another field (files) will be populated with the results. 
  This field will contain a list of dicts with information about the downloaded files, 
  such as the downloaded path, the original scraped url (taken from the file_urls field), 
  the file checksum and the file status. 
  The files in the list of the files field will retain the same order of the original file_urls field. 
  If some file failed downloading, an error will be logged and the file won’t be present in the files field.
"""
