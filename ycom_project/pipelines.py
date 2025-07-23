import json


class YComJsonPipeline:
    def open_spider(self, spider):
        self.items = []

    def close_spider(self, spider):
        with open('output/yc_companies.json', 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)

    def process_item(self, item, spider):
        self.items.append(item)
        return item


class MergeLinkedInPipeline:
    def open_spider(self, spider):
        self.data_path = 'output/yc_companies.json'

        with open(self.data_path, encoding='utf-8') as f:
            raw_data = f.read().rstrip(",\n")
            if not raw_data.endswith(']'):
                raw_data += '\n]'
            self.data = json.loads(raw_data)

        self.data_by_name = {
            company['name']: company for company in self.data
        }

    def process_item(self, item, spider):
        name = item.get("name")
        if name and name in self.data_by_name:
            self.data_by_name[name].update({
                k: v for k, v in item.items() if k.startswith("ln_")
            })
        return item

    def close_spider(self, spider):
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(
                list(self.data_by_name.values()),
                f,
                ensure_ascii=False,
                indent=2
            )
