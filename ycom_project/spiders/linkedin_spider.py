import json
from typing import Any

import scrapy
from scrapy.http import Response


class LinkedinSpider(scrapy.Spider):

    name = "linkedin_spider"

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.retry.RetryMiddleware": 90,
        },
        "ITEM_PIPELINES": {
            "ycom_project.pipelines.MergeLinkedInPipeline": 100,
        },
        "USER_AGENT": (
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) "
            "Gecko/20100101 Firefox/117.0"
        ),
    }

    def start_requests(self):
        with open("output/yc_companies.json", encoding='utf-8') as f:
            raw_data = f.read().rstrip(",\n")
            if not raw_data.endswith(']'):
                raw_data += '\n]'
            data = json.loads(raw_data)

        for company in data:
            linkedin_url = company.get("linkedin_url")
            if linkedin_url:
                yield scrapy.Request(
                    url=linkedin_url,
                    callback=self.parse,
                    meta={"company": company}
                )

    def parse(self, response: Response, **kwargs: Any) -> Any:
        company = response.meta["company"]
        item = {**company}

        if response.status != 200:
            self.logger.warning(f"Blocked or failed to fetch: {response.url}")
            return

        title = response.xpath('//h1[contains(@class, "title")]/text()').get()

        if title and 'YC S25' in title:
            item['ln_title'] = title.strip()
            item['ln_industry'] = response.xpath(
                '//div[@data-test-id="about-us__industry"]/dd/text()'
            ).get().strip()
            item['ln_type'] = response.xpath(
                '//div[@data-test-id="about-us__organizationType"]/dd/text()'
            ).get().strip()

            json_raw = json.loads(response.xpath(
                '//script[@type="application/ld+json"]/text()'
            ).get())

            if json_raw:
                try:
                    json_data = json.loads(json_raw)
                    if isinstance(json_data, list):
                        for data in json_data:
                            if data.get("@type") == "Organization":
                                item.update(self.extract_from_json_ld(data))
                    elif (
                            isinstance(json_data, dict) and
                            json_data.get("@type") == "Organization"
                    ):
                        item.update(self.extract_from_json_ld(json_data))

                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse JSON-LD from {response.url}: {e}"
                    )

            yield item

    def extract_from_json_ld(self, data):
        return {
            "ln_description": data.get("description"),
            "ln_employees_count": data.get(
                "numberOfEmployees", {}
            ).get("value"),
            "ln_logo": data.get("logo", {}).get("contentUrl"),
            "ln_slogan": data.get("slogan"),
        }
