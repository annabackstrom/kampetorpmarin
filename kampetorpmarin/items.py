import scrapy


class ScrapedProduct(scrapy.Item):
    platformproductid = scrapy.Field()
    platformvariantid = scrapy.Field()
    imageLink = scrapy.Field()
    additionalImageLinks = scrapy.Field()
    price = scrapy.Field()
    saleprice = scrapy.Field()
    brand = scrapy.Field()
    name = scrapy.Field()
    gender = scrapy.Field()
    shipping = scrapy.Field()
    shippingWeight = scrapy.Field()
    sizes = scrapy.Field()
    mpn = scrapy.Field()
    gtin = scrapy.Field()
    color = scrapy.Field()
    material = scrapy.Field()
    instock = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    platformcategoryid = scrapy.Field()
    additionalcategoryids = scrapy.Field()
    agegroup = scrapy.Field()
    multipack = scrapy.Field()

    storeid = scrapy.Field()

    def __eq__(self, other):
        try:
            return self.identifier == other.identifier
        except (AttributeError, KeyError):
            return False

    def __lt__(self, other):
        try:
            return self.identifier < other.identifier
        except (AttributeError, KeyError):
            return False

    def __hash__(self):
        try:
            return hash(self.identifier)
        except AttributeError:
            return hash(1)

    def __repr__(self):
        return str(self['platformproductid']) + " " + self['name']

    @property
    def identifier(self):
        return self['platformproductid'] + self['platformvariantid']

    def validate(self):
        assert isinstance(self['platformproductid'], str), "Platformproductid is not a string"
        assert len(self['platformproductid']) > 0, "Platformproductid is empty"
        assert isinstance(self['platformvariantid'], str), "Platformvariantid is not a string"
        assert len(self['platformvariantid']) > 0, "Platformvariantid is empty"
        assert isinstance(self['imageLink'], str), "Imagelink is not a string"
        assert isinstance(self['additionalImageLinks'], list), "additionalImageLinks is not a list"
        assert None not in self['additionalImageLinks'], "None in additionalImageLinks"
        _ = float(self['price'])
        if self['saleprice']:
            _ = float(self['saleprice'])
        assert isinstance(self['brand'], str), "Brand is not a string"
        assert len(self['brand']) > 0, "Brand is empty string"
        assert isinstance(self['name'], str), "Name is not a string"
        assert len(self['name']) > 0, "Name is empty string"
        assert isinstance(self['gender'], str), "Gender is not a string"
        assert self['gender'] in ("male", "female", "unisex"), "Unsupported gender"
        assert isinstance(self['sizes'], list), "Sizes is not a list"
        assert len(self['sizes']) > 0, "Sizes is empty"
        assert isinstance(self['mpn'], str), "MPN is not a string"
        assert isinstance(self['gtin'], list), "Gtin is not a list"
        assert len(self['gtin']) > 0, "Gtin list is empty"
        assert len(self['gtin']) == len(self['sizes']), "Length of gtin and sizes does not match"
        if hasattr(self, 'color') and self['color']:
            assert isinstance(self['color'], str), "Color is not a string"
        if hasattr(self, 'material') and self['material']:
            assert isinstance(self['material'], str), "Material is not a string"
        assert isinstance(self['instock'], bool), "Instock is not a bool"
        assert isinstance(self['description'], str), "Descriptions is not a string"
        assert isinstance(self['url'], str), "URl is not a string"
        assert isinstance(self['platformcategoryid'], str), "Platformcategoryid is not a string"
        assert len(self['platformcategoryid']) > 0, "Platformcategoryid is empty"
        assert isinstance(self['additionalcategoryids'], list), "Additionalcateogryids is not a list"
        assert None not in self['additionalcategoryids'], "None in additionalcategoryids"
        assert self['agegroup'] in ("adult", "child"), "Unsupported age group"
        if hasattr(self, 'multipack') and self['multipack']:
            _ = int(self['multipack'])


class ScrapedCategory(scrapy.Item):
    platformcategoryid = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    targetgender = scrapy.Field()
    agegroup = scrapy.Field()
    coloroptions = scrapy.Field()
    level = scrapy.Field()
    generatedkeywords = scrapy.Field()

    storeid = scrapy.Field()

    def __eq__(self, other):
        try:
            return self['platformcategoryid'] == other['platformcategoryid']
        except (AttributeError, KeyError):
            return False
        except TypeError:
            print("jshdgf")

    def __lt__(self, other):
        try:
            return self['platformcategoryid'] < other['platformcategoryid']
        except AttributeError:
            return False

    def __hash__(self):
        try:
            return hash(self['platformcategoryid'])
        except AttributeError:
            return hash(1)

    def __repr__(self):
        return self['platformcategoryid'] + " " + self['name']

    def validate(self):
        assert isinstance(self['platformcategoryid'], str), "Platformcateogryid is not a string"
        assert len(self['platformcategoryid']) > 0, "Platformcategoryid is empty"
        assert isinstance(self['name'], str), "Name is not a string"
        assert len(self['name']) > 0, "Name is empty"
        assert isinstance(self['url'], str), "URL is not a str"
        assert isinstance(self['targetgender'], str), "Target gender is not a str"
        assert self['targetgender'] in ("male", "female", "unisex"), "Unsupported target gender"
        assert self['agegroup'] in ("adult", "child"), "Unsupported age group"
        if hasattr(self, "coloroptions") and self['coloroptions']:
            assert isinstance(self['coloroptions'], list), "Color options is not a list"
        if hasattr(self, "generatedkeywords") and self['generatedkeywords']:
            assert isinstance(self['generatedkeywords'], list), "Generatedkeywords is not a list"
        assert isinstance(self['storeid'], str), "Storeid is not a str"


class ScrapedProductCategoryAssociation(scrapy.Item):
    category = scrapy.Field()
    productid = scrapy.Field()
    storeid = scrapy.Field()
