import requests
from app.utils import CustomThread
import app.settings as settings
import pandas as pd
import numpy as np
from datetime import datetime
import os
from app.ecommerceBase import ecommerceBase
import time
from app.utils import ingestDATA

class crawlTiki(ecommerceBase):
    def __init__(self,**kwargs):
        self.reParam = {}
        for key, value in kwargs.items():
            self.reParam[key] = value
        self.categoryAPI = 'https://api.tiki.vn/raiden/v2/menu-config'
        self.pageAPI = 'https://tiki.vn/api/personalish/v1/blocks/listings'
        self.productAPI = 'https://tiki.vn/api/v2/products/'
        #------------#
        self.ID_FOLDER      = os.path.join(settings.BASE_DIR,'data\Tiki\id')
        self.PRODUCT_FOLDER = os.path.join(settings.BASE_DIR,'data\Tiki\product')
        self.Engine = settings.ecommerce_engine
    def __repr__(self):
        return "Tiki"
    def __getCategory(self):
        # ------------------------------
        while True:
            try:
                response = requests.get(
                    url=self.categoryAPI,
                    headers=self.reParam.get('headers')
                )
            except:
                response = requests.get(
                    url=self.categoryAPI,
                    headers=self.reParam.get('headers'),
                    proxies=self.reParam.get('proxies')
                )
            if response.status_code == 200:
                break
        jsonData = response.json()
        category = jsonData.get('menu_block').get('items')
        for cate in category:
            cate.pop('icon_url')
        for i in range(len(category)):
            if category[i]['text'] == 'NGON':
                category.pop(i)
                break
            else:
                continue
        # ------------------------------            
        return category
    def __getID_inPage(self,category:dict,numPage:int):
        ID = []
        link = category.get('link')
        elementLink = link.split('/')
        strParams = {
            'limit': '40',
            'include': 'advertisement',
            'aggregations': '2',
            'version': 'home-persionalized',
            'trackity_id': 'bf751c2a-3fd4-bd77-8eb0-3bc8d63c67aa',
            'category': elementLink[4][1:],
            'page': numPage,
            'urlKey': elementLink[3],
        }
        while True:
            try:
                response = requests.get(
                    url     = self.pageAPI,
                    headers = self.reParam.get('headers'),
                    params  = strParams  
                )
            except:
                response = requests.get(
                    url=self.categoryAPI,
                    headers=self.reParam.get('headers'),
                    params=strParams,
                    proxies=self.reParam.get('proxies')
                )
            if response.status_code == 200:
                break
        jsonData = response.json()
        data = jsonData.get('data')
        if data is None:
            return ID
        else:
            for ele in data:
                ID.append(ele.get('id'))
        return ID
    def __getID_inCategory(self,category:dict):
        ID = []
        batch = 5
        for i in range(1,51,batch):
            threads = []
            for j in range(i,i+batch):
                thread = CustomThread(target=self.__getID_inPage,args=(category,j))
                thread.start()
                threads.append(thread)
            for thread in threads:
                try:
                    id = thread.join()
                    ID.extend(id)
                except:
                    pass
            threads.clear() 

        ID = list(dict.fromkeys(ID))
        return ID    
    def __get_1_Product(self,id:int):
        pAPI = self.productAPI + str(id)
        strParams = {
            'platform': 'web',
            'spid': id,
            'version': '3',
        }
        while True:
            try:
                response = requests.get(url=pAPI,headers=self.reParam.get('headers'),params=strParams)
            except:
                response = requests.get(url=pAPI,headers=self.reParam.get('headers'),params=strParams,proxies=self.reParam.get('proxies'))
            if response.status_code == 200:
                break
        
        product = dict()

        product['id'] = id
        try:
            product['name'] = response.json().get('name')
        except:
            product['name'] = None

        try:
            product['description'] = response.json().get('short_description')
        except:
            product['description'] = None

        try:
            product['price'] = response.json().get('price')
        except:
            product['price'] = None

        try:
            product['url'] = response.json().get('short_url')
        except:
            product['url'] = None

        try:
            product['rate'] = response.json().get('rating_average')
        except:
            product['rate'] = None

        try:
            product['category'] = response.json().get('breadcrumbs')[0].get('name')
        except:
            product['category'] = None
            
        product['source'] = "TIKI"

        return product
    
    def getID(self):
        crawlIDs = []
        fileName = str(datetime.now().date()) + '.csv'
        listFile = os.listdir(self.ID_FOLDER)
        category = self.__getCategory()
        if fileName in listFile:
            newIDs = pd.read_csv(os.path.join(self.ID_FOLDER,fileName))['id'].to_list()
        else:
            for cate in category:
                cIDs = self.__getID_inCategory(category=cate)
                crawlIDs.extend(cIDs)
            dbIDs = pd.read_sql("SELECT id FROM product", con=self.Engine)['id'].to_list()
            newIDs = [id for id in crawlIDs if dbIDs.count(id) == 0]
            pd.DataFrame(newIDs,columns=['id']).to_csv(os.path.join(self.ID_FOLDER,fileName))
        return newIDs
    def getPRODUCT(self,ID:list):
        IDs = np.array_split(ID,len(ID)/1000)
        #-----------#
        fileName = str(datetime.now().date()) + '.csv'
        if fileName in os.listdir(self.PRODUCT_FOLDER):
            return  
        else:
            productContainer = []
            for ID in IDs:
                threads = []
                while len(ID) > 0:
                    ids = ID[:50]
                    for id in ids:
                        productid = id
                        thread = CustomThread(target=self.__get_1_Product,args=(productid,))
                        thread.start()
                        threads.append(thread)
                    for thread in threads:
                        product = thread.join()
                        if product != None:
                            productContainer.append(product)
                    ID = ID[50:]
            #-- Convert to DATAFRAME --#
            productDF = pd.DataFrame(productContainer)
            #-- Clean DF --#
            productDF.drop_duplicates(inplace=True)
            productDF.set_index('id', inplace=True)
            productDF.dropna(inplace=True)
            #-- Save DF --#
            productDF.to_csv(os.path.join(self.PRODUCT_FOLDER,fileName))

    def run(self):
        ID = self.getID()
        self.getPRODUCT(ID)
        #----#
        fileName = str(datetime.now().date()) + '.csv'
        data = pd.read_csv(os.path.join(self.PRODUCT_FOLDER,fileName))
        ingestDATA(data,settings.ecommerce_engine)
        return

        

        
        
        

        
