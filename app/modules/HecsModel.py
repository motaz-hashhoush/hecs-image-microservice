from  tensorflow import keras
from bs4 import BeautifulSoup 
from skimage import io
from uuid import uuid4
import numpy as np
import requests
import os
import cv2

LABELS_ARRAY= np.array(['B_B', 'Bakery', 'Bar', 'Buffet', 'Cafe', 'Camping', 'Casinos',
        'Casual_Dining', 'Catering', 'Cinema_Theater', 'Club',
        'Fine_Dining', 'Ghost_Kitchen', 'Hotel', 'Motel', 'Park', 'Pub',
        'Quick_Casual', 'Quick_Service', 'Resort'])


class HecsModel:
    
    def __init__(self, path_to_model:str, label_freq:int, threshold:float, stor_images_path:str='app/modules/images/') -> None:
        self.model = self.load_hecs_model(path_to_model)
        self.label_freq = label_freq
        self.threshold = threshold
        self.label_freq = label_freq
        self.stor_images_path = stor_images_path
        
    def load_hecs_model(self, path_to_model):
        try:
            return keras.models.load_model(path_to_model)
        except Exception as e:
            print(str(e))
            raise e
        
    def prdict(self, branch_name):
        
        try:
            images_path = self.get_images(branch_name, 12)
            loaded_images = self.read_images(images_path)
            self.reomve_images(images_path)
            return self.predict_model(loaded_images)
            
        except Exception as e:
            print(str(e))
            raise e
        
    def reomve_images(self, images_path):
        """delete images that scripaing

        Args:
            images_path (list): path of images 
        """
        for path in images_path:
            os.remove(path)
            
    def read_images(self, paths: list):
    
        images = []
        for path in paths:
            images.append(io.imread(path))
        return np.array(images, dtype=object)
    
    def check_pred(self, prediction, threshold):
        """return labels are given prediction and a certain threshold

        Args:
            prediction (np.ndarray): prediction from the model
            threshold (float): The float number that we want to set any value greater than to be TRUE
        Returns:
            np.ndarray: all labels above the threshold
        """
        prediction[prediction < threshold] = 0
        prediction[prediction >= threshold] = 1

        return LABELS_ARRAY[prediction.astype(bool)]
    
    def filter_labels(self, labels_freq: dict)->list:
        """raturn a labels that have at lest 3 frequancy

        Args:
            labels_freq (dict): the key is the labels and value

        Returns:
            _type_: _description_
        """
        final_labels = []

        for key, value in labels_freq.items():
            if value >= self.label_freq:
                final_labels.append(key)

        return final_labels
    
    def predict_model(self, images: list)-> str:
        """predict a list of images given a certain model

        Args:
            images (list): Iterable contanis images
            model (keras.Model): the model to predict images 
            filter (bool, optional): filter the labels and take the label that is repeated three or more times 
            if False then take all labels from predictions . Defaults to True.

        Returns:
            str: all labels in one string
        """

        labels_freq = {}

        for img in images:
            try:
                img = cv2.resize(img, (224, 224))
                if img.shape[2] != 3:
                    img = img[:,:,:3]

                pred = self.model.predict(np.array([img]))
            except Exception as e:
                print(str(e))
                continue

            pred = np.array(pred)
            labels_pred = self.check_pred(pred[:, 0, 0], self.threshold)

            for label in labels_pred:
                if label in labels_freq:
                    labels_freq[label] += 1
                else:
                     labels_freq[label] = 1
                     
        labels = self.filter_labels(labels_freq)
        
        if labels == []:
            return ['unknown']   
        
        return labels

    def get_images(self, keyword, num_images):
        """scraping imgae from google imgaes given keywords

        Args:
            keyword (str): search keyword
            num_images (str): the number of images you want
            Image_Folder (str): _description_
        """
        paths = []
        request_link = 'https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&'
        user_agnt = { 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        } 

        search_url = request_link + 'q=' + keyword 

        if not os.path.exists(self.stor_images_path):
            os.mkdir(self.stor_images_path)

        # request url, without u_agnt the permission gets denied
        response = requests.get(search_url, headers=user_agnt)
        html = response.text #To get actual result i.e. to read the html data in text mode

        # find all img where class='rg_i Q4LuWd'
        b_soup = BeautifulSoup(html, 'html.parser') #html.parser is used to parse/extract features from HTML files
        results = b_soup.findAll('img', {'class': 'rg_i Q4LuWd'})

        #extract the links of requested number of images with 'data-src' attribute and appended those links to a list 'imagelinks'
        #allow to continue the loop in case query fails for non-data-src attributes
        count = 0
        imagelinks= []
        for res in results:
            try:
                link = res['data-src']
                imagelinks.append(link)
                count = count + 1
                if count >= num_images:
                    break
            except:
                continue
            
        for  imagelink in imagelinks:
            # open each image link and save the file
            response = requests.get(imagelink)

            imagename = f"{self.stor_images_path}{uuid4()}.jpg"
            paths.append(imagename)
            with open(imagename, 'wb') as file:
                file.write(response.content)

        return paths
    