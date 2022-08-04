from kampetorpmarin.items import ScrapedProduct, ScrapedCategory, ScrapedProductCategoryAssociation
from kampetorpmarin.countrysettings import countries
from kampetorpmarin.machineapiconnector import MachineAPIWrapper
from kampetorpmarin.listfinder import bisectleftwithattribute, finditemsinlistwithbisect

class KampetorpmarinPipeline(object):
    countryproperties: {str: {str: list}} = dict()
    productcount = 0
    duplicatecount = 0

    def process_item(self, item, spider):
        storeid = item['storeid']
        if storeid not in self.countryproperties:
            self.countryproperties[storeid] = {"products": [],
                                               "categories": []}

        if isinstance(item, ScrapedCategory):
            try:
                item.validate()
            except (AssertionError, ValueError) as err:
                print(f"Error validating {item}: {err.args[0]}")
            if [x['name'] for x in self.countryproperties[storeid]['categories']].count(item['name']) >= 5:
                return item
            if item in self.countryproperties[storeid]['categories']:
                return item
            self.countryproperties[storeid]['categories'].append(item)
        if isinstance(item, ScrapedProduct):
            try:
                item.validate()
            except (AssertionError, ValueError) as err:
                print(f"Error validating {item}: {err.args[0]}")
            if "corona" in item['name'].lower() or "covid" in item['name'].lower():
                return item
            self.productcount += 1
            existingproducts = finditemsinlistwithbisect(itemlist=self.countryproperties[storeid]['products'],
                                                         attrname="identifier",
                                                         object=item)
            if len(existingproducts) > 0:
                for existingproduct in existingproducts:
                    self.duplicatecount += 1
                    if item['platformcategoryid'] not in [*existingproduct['additionalcategoryids'],
                                                          existingproduct['platformcategoryid']]:
                        existingproduct['additionalcategoryids'].append(item['platformcategoryid'])
                return item
            index = bisectleftwithattribute(self.countryproperties[storeid]['products'], item, "identifier")
            self.countryproperties[storeid]['products'].insert(index, item)
        if isinstance(item, ScrapedProductCategoryAssociation):
            existingproducts = finditemsinlistwithbisect(itemlist=self.countryproperties[storeid]['products'],
                                                         attrname="platformproductid",
                                                         object=item['productid'])
            if len(existingproducts) > 0:
                for existingproduct in existingproducts:
                    if item['category']['platformcategoryid'] not in [*existingproduct['additionalcategoryids'],
                                                                      existingproduct['platformcategoryid']]:
                        existingproduct['additionalcategoryids'].append(item['category']['platformcategoryid'])
        return item

    def close_spider(self, spider):
        # https://shopifyappdev3.amandaai.com/pridacapi
        # https://sapp.amandaai.com/pridacapi

        wrapper = MachineAPIWrapper(host="https://pridacapi.amandaai.com",
                                    username=spider.settings.attributes.get('FTP_USER').value,
                                    password=spider.settings.attributes.get('FTP_PASSWORD').value)
        for key, value in self.countryproperties.items():
            countryinfo = next(iter([x for x in countries if x['storeid'] == key]), None)
            if countryinfo is None:
                print("Could not find countryinfo for store with id {}".format(key))
                continue
            for product in value['products']:
                product.validate()
            for category in value['categories']:
                category.validate()
            wrapper.postproductsandcategories(storename=countryinfo['storename'],
                                              storeid=key,
                                              productsandcategories={
                                                  "products": [dict(x) for x in list(set(value['products']))],
                                                  "categories": [dict(x) for x in list(set(value['categories']))]
                                              })
