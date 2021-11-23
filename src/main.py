import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import math

from requests.models import HTTPError
class Scraper():
    heading=("BrandName","ProductName","Attribute Color","MRP","SalesPrice","Images","ProductDescriptions")
    SAREE_URL="https://www.ajio.com/mahamantra-woven-handloom-cotton-silk-saree/p/462541499_blue"
    
    #make a request to the url and return content
    def load_data(self):
        try:
            path=requests.get(self.SAREE_URL)
            if path.status_code == 200:
                return path.content
        
        except requests.exceptions.ConnectionError as e:
            print(e)
        finally:
            print("Searching Finish")
            
    #Scrap the data content which is get from url       
    def scrap_data(self):
        try:
            response = self.load_data()
            if response !=None:
                soup=BeautifulSoup(response,"html.parser")
                response=soup.find_all("script")[12].text.strip().replace("window.__PRELOADED_STATE__ = ","")
                response=response.replace(";","")
                const_dict=(json.loads(response)["product"]["productDetails"])
                brand_name=const_dict["brandName"]
                product_description=const_dict["featureData"]
                sales_price=const_dict["baseOptions"][0]["selected"]["wasPriceData"]["value"]
                image_url=const_dict["baseOptions"][0]["options"][0]["modelImage"]["url"]
                product_name=const_dict["baseOptions"][0]["options"][0]["modelImage"]["altText"]
                color=const_dict["baseOptions"][0]["options"][0]["color"]
                
                json_={"Description":product_description,
                    "sales_price":sales_price,"imageUrl":image_url,"color":color,
                    "brandName":brand_name,"productName":product_name
                    }
                return json_
            
        except Exception as e:
            print(e)
        finally:
            print("Scraping Finish")
    #This function calculate price MRP have above 0.5 decimal part than take ceil value(12.5,13)
    #If less than 0.5 take floor value(12.4,12)
    #return MRP
    def calculate_price(self,sales_price,off_price): 
        MRP=sales_price-(sales_price*off_price)
        decimal1,decimal2=math.modf(MRP)
        if(decimal1>=0.5):
                MRP=math.ceil(MRP)
                return MRP
        else:
                print("else")
                MRP=math.floor(MRP)
                return MRP
                
    #Process data find the dict value return in a list format
    def process_data(self):
        dict_=self.scrap_data()
        list_of_prod_details=[]
        for i in range((len(dict_["Description"]))):
            list_of_prod_details.append(dict_["Description"][i]["name"]+":"+dict_["Description"][i]["featureValues"][0]["value"])
        sales_price=int(dict_["sales_price"])
        MRP=0
        off_price=0
        if(sales_price<500):
            off_price=0.28
            MRP=self.calculate_price(sales_price,off_price)
        elif(sales_price in range(500,1000)):
            off_price=0.42
            MRP=self.calculate_price(sales_price,off_price)
        elif(sales_price in range(2000,3000)):
            off_price=0.55
            MRP=self.calculate_price(sales_price,off_price)
        elif(sales_price in range(3000,5000)):
            off_price=0.60
            MRP=self.calculate_price(sales_price,off_price)
        elif(sales_price in range(5000,10000)):
            off_price=0.72
            MRP=self.calculate_price(sales_price,off_price)
        else:
            off_price=0.78
            MRP=self.calculate_price(sales_price,off_price)
        print(MRP)
        brand_name=dict_["brandName"]
        product_name=dict_["productName"]
        color=dict_["color"]
        image_url=dict_["imageUrl"]
        list_=[[brand_name,product_name,color,MRP,sales_price,image_url,str(list_of_prod_details)],]
        return list_

    #Save data which is return by process_data() function in CSV format
    def save_in_csv(self):
        try:
            data_=self.process_data()
            if(data_!= None and len(data_)!=0):
                dataframe=pd.DataFrame(data_,columns=self.heading)
                dataframe.to_csv("src\data.csv")
                print("Saved in CSV format")
            else:
                print("list is empty")
        except Exception as e:
            print(e)

if __name__ == "__main__":
    obj=Scraper()
    obj.save_in_csv()