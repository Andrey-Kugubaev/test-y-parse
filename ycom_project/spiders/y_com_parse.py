import json
from typing import Any

import scrapy
from scrapy.http import Response


class YComSpider(scrapy.Spider):

    name = "y_com_spider"

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.retry.RetryMiddleware": 90,
        },
        "ITEM_PIPELINES": {
            "ycom_project.pipelines.YComJsonPipeline": 100,
        },
        "USER_AGENT": (
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) "
            "Gecko/20100101 Firefox/117.0"
        ),
    }

    def start_requests(self):
        url = (
            "https://45bwzj1sgc-dsn.algolia.net/1/indexes/*/"
            "queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)"
            "%3B%20Browser%3B%20JS%20Helper%20(3.16.1)&"
            "x-algolia-application-id=45BWZJ1SGC&x-algolia-api-key="
            "MjBjYjRiMzY0NzdhZWY0NjExY2NhZjYxMGIxYjc2MTAwNWFkNTkwNTc4Njg"
            "xYjU0YzFhYTY2ZGQ5OGY5NDMxZnJlc3RyaWN0SW5kaWNlcz0lNUIlMjJZQ0N"
            "vbXBhbnlfcHJvZHVjdGlvbiUyMiUyQyUyMllDQ29tcGFueV9CeV9MYXVuY2h"
            "fRGF0ZV9wcm9kdWN0aW9uJTIyJTVEJnRhZ0ZpbHRlcnM9JTVCJTIyeWNkY19w"
            "dWJsaWMlMjIlNUQmYW5hbHl0aWNzVGFncz0lNUIlMjJ5Y2RjJTIyJTVE"
        )

        headers = {
            "Content-Type": "application/json"
        }

        body = json.dumps(
            {
                "requests": [
                    {
                        "indexName": "YCCompany_production",
                        "params": (
                            "facetFilters=%5B%5B%22batch%3A"
                            "Summer%202025%22%5D%5D&facets=%5B%22app_answers"
                            "%22%2C%22app_video_public%22%2C%22batch%22%2C"
                            "%22demo_day_video_public%22%2C%22industries"
                            "%22%2C%22isHiring%22%2C%22nonprofit%22%2C"
                            "%22question_answers%22%2C%22regions%22%2C"
                            "%22subindustry%22%2C%22top_company%22%5D&"
                            "hitsPerPage=1000&maxValuesPerFacet=1000&"
                            "page=0&query=&tagFilters="
                        )
                    },
                    {
                        "indexName": "YCCompany_production",
                        "params": (
                            "analytics=false&clickAnalytics=false&"
                            "facets=batch&hitsPerPage=0&"
                            "maxValuesPerFacet=1000&page=0&query="
                        )
                    }
                ]
            }
        )
        yield scrapy.Request(
            url=url,
            method='POST',
            dont_filter=True,
            headers=headers,
            body=body,
            callback=self.parse_page
        )

    def parse_page(self, response: Response, **kwargs: Any) -> Any:
        response_data = json.loads(response.body)

        companies_data = response_data.get('results')[0].get("hits")

        for company_data in companies_data:
            slug = company_data.get("slug")

            url = f"https://www.ycombinator.com/companies/{slug}"

            yield scrapy.Request(
                url=url,
                callback=self.parse,
            )

    def parse(self, response: Response, **kwargs: Any) -> Any:
        company_text_data = response.xpath(
            '//body[contains(@class, "companies")]/div/@data-page'
        ).get()
        company_json_data = json.loads(company_text_data)
        company_data = company_json_data.get("props").get("company")

        item = {}

        item['id'] = company_data.get('id')
        item['name'] = company_data.get('name')
        item['website'] = company_data.get('website')
        item['url'] = f'https://www.ycombinator.com/{company_json_data.get("url")}'
        item['ycdc_status'] = company_data.get('ycdc_status')
        item['logo_url'] = company_data.get('logo_url')
        item['tags'] = company_data.get('tags')
        item['short_text'] = company_data.get('one_liner')
        item['long_text'] = company_data.get('long_description')
        item['founders'] = self.get_founders(company_data)
        item['year_founded'] = company_data.get('year_founded')
        item['location'] = company_data.get('location')
        item['team_size'] = company_data.get('team_size')
        item['linkedin_url'] = company_data.get('linkedin_url')
        item['company_photos'] = company_data.get('company_photos')
        yield item

    def get_founders(self, company_data):
        founder_list = [
            founder.get('full_name')
            for founder in company_data.get('founders')
        ]
        return founder_list
