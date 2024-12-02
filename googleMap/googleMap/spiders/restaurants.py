import scrapy
from scrapy_playwright.page import PageMethod

class RestaurantsSpider(scrapy.Spider):
    name = "restaurants"
    start_urls = ["https://www.google.com/maps"]

    def start_requests(self):
        search = "best restaurant in Nagpur"
        url = self.start_urls[0]
        yield scrapy.Request(url, 
                            meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_methods": [
                                PageMethod('wait_for_load_state', "networkidle"),
                                PageMethod('wait_for_load_state', "domcontentloaded"),
                                PageMethod('wait_for_timeout', 2000),
                                PageMethod("fill", 'input.fontBodyMedium', search),
                                PageMethod("click", 'button[aria-label="Search"]'),
                                PageMethod('wait_for_timeout', 5000),

                            ]                               
                    },
                  callback=self.parse
                )

    def parse(self, response):

       restaurant_elements = response.css('div.CpccDe')
       for restaurant in restaurant_elements[:3]:
            a_tag = restaurant.css('a.hfpxzc').getall()
    
            yield scrapy.Request(response.url,meta= {
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods":[
                    PageMethod('click', a_tag),
                    PageMethod("wait_for_selector", 'div.tAiQdd'),
                    PageMethod('wait_for_timeout', 5000),
          ]
       },
       callback=self.parse_restaurant_details
       )
            
            
    def parse_restaurant_details(self, response):
       
       restaurant_elements = response.css('div.tAiQdd')

       for element in restaurant_elements[:3]:

            name = element.css("h1.DUwDvf.lfPIob::text").get()
            rating = element.css("div.F7nice span[aria-hidden='true']::text").get()
            reviews = element.css("div.F7nice span[aria-label$='reviews']::attr(aria-label)").re_first(r"\d+")
            price_range = element.css("span.mgr77e span.fjHK4 + span span::text").get()
            restaurant_type = element.css("button.DkEaL::text").get()

            yield {
            "name": name ,
            "rating": rating,
            "reviews": reviews,
            "price_range": price_range,
            "restaurant_type": restaurant_type,
        }

