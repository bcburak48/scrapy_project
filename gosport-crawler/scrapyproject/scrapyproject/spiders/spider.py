import hashlib
import os
from datetime import datetime
from urllib.parse import urljoin

import json
import mysql
import scrapy
from scrapy_selenium import SeleniumRequest

from ..items import ScrapyprojectItem


class Spider(scrapy.Spider):
    name = 'spider'
    available_list = []

    def start_requests(self):
        category_urls = [
            'https://uae.gosportme.com/collections/mens-apparel',
            'https://uae.gosportme.com/collections/mens-footwear',
            'https://uae.gosportme.com/collections/mens-sports',
            'https://uae.gosportme.com/collections/mens-accessories',
            'https://uae.gosportme.com/collections/womens-apparel',
            'https://uae.gosportme.com/collections/womens-footwear',
            'https://uae.gosportme.com/collections/womens-sports',
            'https://uae.gosportme.com/collections/womens-accessories',
            'https://uae.gosportme.com/collections/boys-apparel',
            'https://uae.gosportme.com/collections/boys-footwear',
            'https://uae.gosportme.com/collections/boys-accessories',
            'https://uae.gosportme.com/collections/girls-apparel',
            'https://uae.gosportme.com/collections/girls-footwear',
            'https://uae.gosportme.com/collections/girls-accessories',
            'https://uae.gosportme.com/collections/kids-sports',
            'https://uae.gosportme.com/collections/kids-accessories',
            'https://uae.gosportme.com/collections/cardio',
            'https://uae.gosportme.com/collections/strength',
            'https://uae.gosportme.com/collections/support-recovery',
            'https://uae.gosportme.com/collections/tech',
            'https://uae.gosportme.com/collections/nutrition']

        for url in category_urls:
            yield SeleniumRequest(
                url=url,
                wait_time=3,
                callback=self.parse,
                dont_filter=True
            )

    def parse(self, response):
        for href in response.css('div.product-wrap > a::attr("href")'):
            url = urljoin("https://uae.gosportme.com/", href.extract())
            yield scrapy.Request(url, callback=self.parse_dir_contents)

        next_page = response.css('#bc-sf-filter-bottom-pagination > span.next > a::attr(href)')

        if next_page:
            yield SeleniumRequest(
                url=next_page.get(),
                wait_time=3,
                callback=self.parse,
                dont_filter=True
            )

    def parse_dir_contents(self, response):
        items = ScrapyprojectItem()

        stock = response.css('.in_stock::text')[0].extract()
        if stock != 'IN STOCK':
            upcean_check = response.css('.sku span::text').extract()
            upcean_check = upcean_check[0][12:]

            db = mysql.connector.connect(host="localhost", user="root", password="Aszxqw1234.", database="aisland")
            curr = db.cursor()
            curr.execute("""SELECT photos FROM mpproducts WHERE upcean = '%s'""" % upcean_check)
            result = curr.fetchall()

            image_paths_remove = result[0][0].replace('[', '').replace(']', '').replace('"', '').split(', ')
            for img in image_paths_remove:
                if os.path.exists(img):
                    os.remove(img)
                else:
                    print("The file does not exist " + img)

            db = mysql.connector.connect(host="localhost", user="root", password="Aszxqw1234.", database="aisland")
            curr = db.cursor()
            curr.execute("""DELETE FROM mpproducts WHERE upcean = '%s'""" % upcean_check)
            db.commit()
            return

        productid = response.css('.sku span::text').extract()
        if not productid:
            return
	    
        productid = hashlib.sha256(productid[0][12:].encode()).hexdigest()
        productid = productid[:len(productid) // 2]
        db = mysql.connector.connect(host="localhost", user="root", password="Aszxqw1234.", database="aisland")
        curr = db.cursor()
        curr.execute("""SELECT productid FROM mpproducts WHERE productid LIKE '%s'""" % productid)
        result = curr.fetchall()
        if result:
            while result[0][0] == productid:
                productid = hashlib.sha256(productid[0][12:].encode()).hexdigest()
                productid = productid[:len(productid) // 2]

        categoryurl = response.request.url.split('/products', 1)[0]
        # Men
        if categoryurl == 'https://uae.gosportme.com/collections/mens-apparel' \
                or categoryurl == 'https://uae.gosportme.com/collections/mens-footwear' \
                or categoryurl == 'https://uae.gosportme.com/collections/mens-sports' \
                or categoryurl == 'https://uae.gosportme.com/collections/mens-accessories':
            categoryid = 1
        # Women
        elif categoryurl == 'https://uae.gosportme.com/collections/womens-apparel' \
                or categoryurl == 'https://uae.gosportme.com/collections/womens-footwear' \
                or categoryurl == 'https://uae.gosportme.com/collections/womens-sports' \
                or categoryurl == 'https://uae.gosportme.com/collections/womens-accessories':
            categoryid = 2
        # Kids
        elif categoryurl == 'https://uae.gosportme.com/collections/boys-apparel' \
                or categoryurl == 'https://uae.gosportme.com/collections/boys-footwear' \
                or categoryurl == 'https://uae.gosportme.com/collections/boys-accessories' \
                or categoryurl == 'https://uae.gosportme.com/collections/girls-apparel' \
                or categoryurl == 'https://uae.gosportme.com/collections/girls-footwear' \
                or categoryurl == 'https://uae.gosportme.com/collections/girls-accessories' \
                or categoryurl == 'https://uae.gosportme.com/collections/kids-sports' \
                or categoryurl == 'https://uae.gosportme.com/collections/kids-accessories':
            categoryid = 3
        # Equipment
        elif categoryurl == 'https://uae.gosportme.com/collections/cardio' \
                or categoryurl == 'https://uae.gosportme.com/collections/strength' \
                or categoryurl == 'https://uae.gosportme.com/collections/support-recovery' \
                or categoryurl == 'https://uae.gosportme.com/collections/tech' \
                or categoryurl == 'https://uae.gosportme.com/collections/nutrition':
            categoryid = 4

        shortdescription = response.css('.product_name::text , .vendor a::text').extract()

        description = response.css('#accordion1 div::text').extract()
        if not description:
            description = response.css('#accordion1 p::text').extract()

        photos = response.css('.product_images .gallery-cell .image__container img::attr(data-src)').extract()
        joined_urls = []
        for photo in photos:
            joined_urls.append(urljoin("https:", photo))
        items['image_urls'] = joined_urls

        price = response.css('.money::text').extract()
        upcean = response.css('.sku span::text').extract()
        if not upcean[0][12:] in Spider.available_list:
            Spider.available_list.append(upcean[0][12:])

        packageurl = response.request.url.split('/products', 1)[0]
        # Clothes
        if packageurl == 'https://uae.gosportme.com/collections/mens-apparel' \
                or packageurl == 'https://uae.gosportme.com/collections/womens-apparel' \
                or packageurl == 'https://uae.gosportme.com/collections/boys-apparel' \
                or packageurl == 'https://uae.gosportme.com/collections/girls-apparel':
            packagesizel = 30
            packagesizeh = 20
            packagesizew = 3
            packageweight = 500
        # Shoes
        elif packageurl == 'https://uae.gosportme.com/collections/mens-footwear' \
                or packageurl == 'https://uae.gosportme.com/collections/womens-footwear' \
                or packageurl == 'https://uae.gosportme.com/collections/boys-footwear' \
                or packageurl == 'https://uae.gosportme.com/collections/girls-footwear':
            packagesizel = 34
            packagesizeh = 20
            packagesizew = 13
            packageweight = 500
        # Other Stuffs
        elif packageurl == 'https://uae.gosportme.com/collections/mens-sports' \
                or packageurl == 'https://uae.gosportme.com/collections/mens-accessories' \
                or packageurl == 'https://uae.gosportme.com/collections/womens-sports' \
                or packageurl == 'https://uae.gosportme.com/collections/womens-accessories' \
                or packageurl == 'https://uae.gosportme.com/collections/boys-accessories' \
                or packageurl == 'https://uae.gosportme.com/collections/girls-accessories' \
                or packageurl == 'https://uae.gosportme.com/collections/kids-sports' \
                or packageurl == 'https://uae.gosportme.com/collections/kids-accessories' \
                or packageurl == 'https://uae.gosportme.com/collections/cardio' \
                or packageurl == 'https://uae.gosportme.com/collections/strength' \
                or packageurl == 'https://uae.gosportme.com/collections/support-recovery' \
                or packageurl == 'https://uae.gosportme.com/collections/tech' \
                or packageurl == 'https://uae.gosportme.com/collections/nutrition':
            packagesizel = 20
            packagesizeh = 20
            packagesizew = 20
            packageweight = 500

        info = response.xpath(
            '/html/body/div[3]/div[1]/div/div/div/div/div[3]/form/div[1]/select/option/text()').extract()

        items['blocknumber'] = '0'
        items['txhash'] = ['']
        items['dtblockchain'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        items['signer'] = ['']
        items['email'] = 'samragosport@aisland.io'
        items['productid'] = productid[:len(productid) // 2]
        items['departmentid'] = '4'
        items['categoryid'] = categoryid
        items['shortdescription'] = shortdescription[0] + ' ' + shortdescription[1]
        items['description'] = ' '.join(description)
        items['specifications'] = ['']
        items['photos'] = ['']
        items['videos'] = ['']
        items['price'] = "{:.2f}".format(float(price[0][5:].replace(',', '')) / 3.66 * 1.15)
        items['currency'] = 'USDC'
        items['upcean'] = upcean[0][12:]
        items['returnpolicy'] = '30'
        items['guarantee'] = '365'
        items['minimumquantity'] = '1'
        items['packagesizel'] = packagesizel
        items['packagesizeh'] = packagesizeh
        items['packagesizew'] = packagesizew
        items['packageweight'] = packageweight
        items['info'] = json.dumps({"sizes": info})

        yield items

    def closed(self, spider):
        db = mysql.connector.connect(host="localhost", user="root", password="Aszxqw1234.", database="aisland")
        curr = db.cursor()
        curr.execute("""SELECT upcean FROM mpproducts""")
        result = curr.fetchall()
        db_list = []
        for x in result:
            db_list.append(x[0])

        dif_list = list(set(db_list) - set(Spider.available_list))

        for item in dif_list:
            db = mysql.connector.connect(host="localhost", user="root", password="Aszxqw1234.", database="aisland")
            curr = db.cursor()
            curr.execute("""SELECT photos FROM mpproducts WHERE upcean = '%s'""" % item)
            result = curr.fetchall()
            image_paths_remove = result[0][0].replace('[', '').replace(']', '').replace('"', '').split(', ')
            for img in image_paths_remove:
                if os.path.exists(img):
                    os.remove(img)
                else:
                    print("The file does not exist")

            db = mysql.connector.connect(host="localhost", user="root", password="Aszxqw1234.", database="aisland")
            curr = db.cursor()
            curr.execute("""DELETE FROM mpproducts WHERE upcean = '%s'""" % item)
            db.commit()

        dif_list.clear()
