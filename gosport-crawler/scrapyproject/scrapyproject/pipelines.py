# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import hashlib
import json
from io import BytesIO

import mysql.connector
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.misc import md5sum
from scrapy.utils.python import to_bytes


class PhotoPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f'/{image_guid}.png'

    def image_downloaded(self, response, request, info, *, item=None):
        checksum = None
        for path, image, buf in self.get_images(response, request, info, item=item):
            if checksum is None:
                buf.seek(0)
                checksum = md5sum(buf)
            width, height = image.size
            self.store.persist_file(
                path, buf, info,
                meta={'width': width, 'height': height},
                headers={'Content-Type': 'image/png'})
        return checksum

    def convert_image(self, image, size=None):
        if image.format == 'PNG' and image.mode == 'RGBA':
            background = self._Image.new('RGBA', image.size, (255, 255, 255))
            background.paste(image, image)
            image = background.convert('RGB')
        elif image.mode == 'P':
            image = image.convert("RGBA")
            background = self._Image.new('RGBA', image.size, (255, 255, 255))
            background.paste(image, image)
            image = background.convert('RGB')
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        # if size:
        #     image = image.copy()
        #     image.thumbnail(size, self._Image.ANTIALIAS)

        if size is None:
            image = image.copy()
            basewidth = 1000
            hsize = 800
            image = image.resize((basewidth, hsize), self._Image.ANTIALIAS)

        buf = BytesIO()
        image.save(buf, 'PNG')
        return image, buf


class ScrapyprojectPipeline(object):

    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='Aszxqw1234.',
            database='aisland'
        )
        self.curr = self.conn.cursor()

    def create_table(self):
        # self.curr.execute("""DROP TABLE IF EXISTS mpproducts """)
        self.curr.execute("""CREATE TABLE IF NOT EXISTS mpproducts (
                            id mediumint(9) NOT NULL AUTO_INCREMENT,
                            blocknumber int(11) NOT NULL,
                            txhash varchar(66) NOT NULL,
                            dtblockchain datetime NOT NULL,
                            signer varchar(48) NOT NULL,
                            email varchar(66) NOT NULL,
                            productid varchar(32) NOT NULL,
                            departmentid int(11) NOT NULL,
                            categoryid int(11) NOT NULL,
                            shortdescription varchar(128) NOT NULL,
                            description text NOT NULL,
                            specifications text NOT NULL,
                            photos text DEFAULT NULL,
                            videos text DEFAULT NULL,
                            price decimal(36,18) NOT NULL,
                            currency varchar(4) NOT NULL,
                            upcean varchar(32) DEFAULT NULL,
                            brand int(11) DEFAULT NULL,
                            model int(11) DEFAULT NULL,
                            returnpolicy int(11) NOT NULL,
                            guarantee int(11) NOT NULL,
                            minimumquantity int(11) NOT NULL,
                            packagesizel decimal(8,2) NOT NULL,
                            packagesizeh decimal(8,2) NOT NULL,
                            packagesizew decimal(8,2) NOT NULL,
                            packageweight decimal(8,2) NOT NULL,
                            documents text DEFAULT NULL,
                            info text NOT NULL,
                            PRIMARY KEY (id)
                            ) ENGINE=InnoDB AUTO_INCREMENT=438 DEFAULT CHARSET=utf8mb4""")

    def process_item(self, item, spider):
        self.store_db(item)
        return item

    def store_db(self, item):

        item['photos'].clear()
        for index in range(len(item['images'])):
            for key in item['images'][index]:
                if key == 'path':
                    item['photos'].insert(index, "uploads" + item['images'][index][key])
        item['photos'] = json.dumps(item['photos'])

        dba = mysql.connector.connect(host="localhost", user="root", password="Aszxqw1234.", database="aisland")
        cur = dba.cursor()
        cur.execute("""SELECT EXISTS(SELECT * FROM mpproducts WHERE upcean = '%s')""" % item['upcean'])
        result = cur.fetchall()
        if result[0][0] == 1:
            print("UPDATE")
            self.curr.execute("""UPDATE mpproducts SET blocknumber=%s, txhash=%s, dtblockchain=%s, signer=%s, email=%s, productid=%s, 
                    departmentid=%s, categoryid=%s, shortdescription=%s, description=%s, specifications=%s, photos=%s, videos=%s, price=%s, currency=%s, 
                    upcean=%s, returnpolicy=%s, guarantee=%s, minimumquantity=%s, packagesizel=%s, packagesizeh=%s, packagesizew=%s, 
                    info=%s WHERE upcean = %s""", (
                item['blocknumber'],
                item['txhash'][0],
                item['dtblockchain'],
                item['signer'][0],
                item['email'],
                item['productid'],
                item['departmentid'],
                item['categoryid'],
                item['shortdescription'],
                item['description'],
                item['specifications'][0],
                item['photos'],
                item['videos'][0],
                item['price'],
                item['currency'],
                item['upcean'],
                item['returnpolicy'],
                item['guarantee'],
                item['minimumquantity'],
                item['packagesizel'],
                item['packagesizeh'],
                item['packagesizew'],
                item['info'],
                item['upcean']
            ))
        else:
            print("NEW")
            self.curr.execute("""insert into mpproducts (blocknumber, txhash, dtblockchain, signer, email, productid, 
            departmentid, categoryid, shortdescription, description, specifications, photos, videos, price, currency, 
            upcean, returnpolicy, guarantee, minimumquantity, packagesizel, packagesizeh, packagesizew, 
            packageweight, info) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
                item['blocknumber'],
                item['txhash'][0],
                item['dtblockchain'],
                item['signer'][0],
                item['email'],
                item['productid'],
                item['departmentid'],
                item['categoryid'],
                item['shortdescription'],
                item['description'],
                item['specifications'][0],
                item['photos'],
                item['videos'][0],
                item['price'],
                item['currency'],
                item['upcean'],
                item['returnpolicy'],
                item['guarantee'],
                item['minimumquantity'],
                item['packagesizel'],
                item['packagesizeh'],
                item['packagesizew'],
                item['packageweight'],
                item['info']
            ))
        self.conn.commit()
