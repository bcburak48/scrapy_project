## Installation

```
cd /usr/src/gosport-crawler/
pip install -r /usr/src/gosport-crawler/requirements.txt
```

## Usage

```
cd /usr/src/gosport-crawler/scrapyproject/scrapyproject/
scrapy crawl spider
```

At each run, it cycles through all the products one by one and updates the database and images.
Deletes products that no longer exist and out-of-stock items. If the product is available in the database,
it updates all the information except the manually entered weight information.