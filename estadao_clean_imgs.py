import cv2
import numpy as np
import math
import os
from PIL import Image
import time
import logging

class clean_imgs_2003_2004:
    def __init__(self, img_name, path_img_ed, path_div1, path_div2, path_img_rem1, path_img_rem2):
        self.final_img = None
        self.img_name = img_name
        self.path_img_ed = path_img_ed
        self.path_div1 = path_div1
        self.path_div2 = path_div2
        self.path_img_rem1 = path_img_rem1
        self.path_img_rem2 = path_img_rem2        

    def find_loc_div(self):
        #Reading the images
        ed_img = cv2.imread(self.path_img_ed, cv2.IMREAD_UNCHANGED) 
        linha_img = cv2.imread(self.path_div1, cv2.IMREAD_UNCHANGED)
        linha_img_2 = cv2.imread(self.path_div2, cv2.IMREAD_UNCHANGED)
        
        #Downscaling the images
        ed_img = cv2.resize(ed_img, (0,0), fx=0.3, fy=0.3) 
        linha_img = cv2.resize(linha_img, (0,0), fx=0.3, fy=0.3) 
        linha_img_2 = cv2.resize(linha_img_2, (0,0), fx=0.3, fy=0.3) 
        
        #Identifying the location of the divisions we are seeking by matching
        result = cv2.matchTemplate(ed_img, linha_img, cv2.TM_CCOEFF_NORMED) 
        result_2 = cv2.matchTemplate(ed_img, linha_img_2, cv2.TM_CCOEFF_NORMED)

        #Expressing those locations and threshold in variables
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)  
        min_val_2, max_val_2, min_loc_2, max_loc_2 = cv2.minMaxLoc(result_2)
        
        #Re-escaling the locations
        superior_w = math.ceil(max_loc_2[0]/0.3)  
        superior_h = math.ceil(max_loc_2[1]/0.3)
        inferior_w = math.ceil(max_loc[0]/0.3)
        inferior_h = math.ceil(max_loc[1]/0.3)
        
        if max_loc_2[1]/0.3 < 700:   #Catching errors for specific pages. 
                                     #If it identifies the wrong section, this will make sure the correct part is returned
                                     
            threshold = max_val_2 - 0.05 #There are similar images and the best match may be the wrong one we are seeking
                                         #This will choose the second best match and guarantee that it's the correct one.
            yloc, xloc = np.where(result_2 >= threshold)
            loc = [[math.ceil(x/0.3), math.ceil(y/0.3)] for x, y in zip(yloc, xloc) if x in range(int(800*0.3), int(1400*0.3)) and y > int(140*0.3)]
            superior_w = loc[0][1]
            superior_h = loc[0][0]

        return superior_w, superior_h, inferior_w, inferior_h

    def crop_loc_div(self):
        ed_path = self.path_img_ed
        fn, fext = os.path.splitext(self.img_name)
        s_w, s_h, i_w, i_h = self.find_loc_div()
        i = Image.open(ed_path)
        crop1 = i.crop((130, 255, 1850, s_h+20)) #Making the necessary crops to select each editorial separately
        crop2 = i.crop((i_w, (s_h + 25), 1850, i_h))
        crop3 = i.crop((s_w, (s_h + 25), i_w, 3200))
        crops = [crop1, crop2, crop3] #Making a list with each section in Pillow format
        return crops
        
    def find_img_loc(self):
        imgs_pil = self.crop_loc_div()
        cropped_imgs_pil = []
        for i in imgs_pil:
            img_to_crop = np.array(i) #Transforming the pillow format into an array so the CV2 can match
            
            #Reading the image we want to match as CV2 array
            linha_img = cv2.imread(self.path_img_rem1, cv2.IMREAD_UNCHANGED)  
            linha_img_2 = cv2.imread(self.path_img_rem2, cv2.IMREAD_UNCHANGED)
            
            #Downscaling the images
            ed_img = cv2.resize(img_to_crop, (0,0), fx=0.5, fy=0.5)  
            linha_img = cv2.resize(linha_img, (0,0), fx=0.5, fy=0.5) 
            linha_img_2 = cv2.resize(linha_img_2, (0,0), fx=0.5, fy=0.5) 
            
            #Identifying the location of the divisions we are seeking by matching
            result = cv2.matchTemplate(ed_img, linha_img, cv2.TM_CCOEFF_NORMED) 
            result_2 = cv2.matchTemplate(ed_img, linha_img_2, cv2.TM_CCOEFF_NORMED)
            
            #Expressing those locations and threshold in variables
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)   
            min_val_2, max_val_2, min_loc_2, max_loc_2 = cv2.minMaxLoc(result_2)
            
            #Re-escaling the locations
            w = math.ceil(linha_img_2.shape[1]/0.5) 
            h = math.ceil(linha_img_2.shape[0]/0.5)
            w_2 = math.ceil(linha_img.shape[1]/0.5)
            h_2 = math.ceil(linha_img.shape[0]/0.5)
            s_w = math.ceil(max_loc_2[0]/0.5)  
            s_h = math.ceil(max_loc_2[1]/0.5)
            i_w = math.ceil(max_loc[0]/0.5)
            i_h = math.ceil(max_loc[1]/0.5)

            #Cropping the images out and saving into a list of arrays            
            img_arr = np.array(i)
            img_arr[(s_h - w + h) : s_h + h, s_w : (s_w + w)] = (255, 255, 255)
            img = Image.fromarray(img_arr)
            if max_val > 0.4:
                img_arr[i_h : i_h + h_2, i_w : (i_w + w_2)] = (255, 255, 255)
                img = Image.fromarray(img_arr)
            cropped_imgs_pil.append(img)
            
        return cropped_imgs_pil #Return a list of images in Pillow format
    
    
def detect_rectangles(image, xkernel, ykernel, box=False):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7,7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Create rectangular structuring element and dilate
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (xkernel,ykernel))
    dilate = cv2.dilate(thresh, kernel, iterations=3)

    # Find contours, draw rectangle and save coordinates to list
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    rectangles = []
    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        rectangles.append([x, y, (x + w), (y + h)])
        if box:
            cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 2) 
        
    return rectangles, image, dilate
    
class columnize:
    def __init__(self, cropped_img, number_ed, path_img, final_path):
        self.final_img = None
        if isinstance(cropped_img, np.ndarray):
            self.cropped_img = Image.fromarray(cropped_img)
        else:
            self.cropped_img = cropped_img
        self.number_ed = number_ed
        self.path_img = path_img
        self.final_path = final_path

    def get_title_article(self):
        #Since I decided to create two methods to separate the images, the first method will need the body to the separated from its title
        #That being, I created this method to perform this separation. It will bind together the all the lines of text
        #And it will bind this rows together only if they are close to each other, close enough to be part of the same block of text.
        
        img = np.array(self.cropped_img) #Will laod the image into an array
        rgb = cv2.pyrDown(img) #Downsizing the image
        small = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY) 

        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        kernel = np.ones((5, 5), np.uint8) 
        grad = cv2.morphologyEx(small, cv2.MORPH_GRADIENT, kernel)
        
        _, bw = cv2.threshold(grad, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU) # Creating a pure black and white image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 2)) # Defining ther filter
        connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel) #Applying the filter

        # using RETR_EXTERNAL instead of RETR_CCOMP
        contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #Finding the contours of the rectangles we are looking for

        mask = np.zeros(bw.shape, dtype=np.uint8)
        rectangles = []
        for idx in range(len(contours)):
            #Applying masks, getting the exact location of the rectangles and and drawing a contour around the article, can be accessed if you want to.
            x, y, w, h = cv2.boundingRect(contours[idx])
            rectangles.append([(x*2), (y*2), ((w*2) + (x*2) + 2), ((h*2) + (y*2) + 2)])
            mask[y:y+h, x:x+w] = 0
            cv2.drawContours(mask, contours, idx, (255, 255, 255), -1)
            r = float(cv2.countNonZero(mask[y:y+h, x:x+w])) / (w * h)

            if r > 0.45 and w > 8 and h > 8:
                cv2.rectangle(rgb, (x, y), (x+w-1, y+h-1), (0, 255, 0), 2)
        
        #Find the articles counting the amount of pixels it has in the Y Axis
        for i in rectangles:
            if self.number_ed == 3:
                if (i[3] - i[1]) > 850:
                    self.final_img = self.cropped_img.crop(i)
            else:
                if (i[3]-i[1]) > 200:
                    self.final_img = self.cropped_img.crop(i)
    
    def find_article_sections(self):
        #This will separate each article into multiple columns. Each column will have its own rectangle.
        if self.number_ed == 2:  
            image = np.array(self.final_img)
            rectangles, dilate, image = detect_rectangles(image, 1, 5, False) #Applying the filter to detect the rectangles
        else:
            image = np.array(self.final_img)
            rectangles, dilate, image = detect_rectangles(image, 2, 5, False)
            # cv2.imshow('a', image)
            # cv2.waitKey(0)
            
        if self.number_ed == 3:
            sections = [i for i in rectangles if (i[3] - i[1]) > 850 and (i[2] - i[0] > 100)]   #Determining which rectangles we want, there may be some bugs
                                                                                                #With the rectangle binding and it may create small rectangles that we 
                                                                                                #would want to exclude.
        else:
            sections = [i for i in rectangles if (i[3] - i[1]) > 150 and (i[2] - i[0] > 100)]
        x_of_sections = sorted([i[0] for i in sections])
        sections_loc = [o for i in x_of_sections for o in sections if o[0] == i]    #Finding the exact section of the X axis after we sorted then in order
        
        rectangles_loc = [] 
        for i in sections_loc:
            #Grouping together all the rectangles that may have overlaped and are close enough to be considered one
            #That avoids doubling our cuts and repeating the same section of the article many times.
            rectangles_loc.append(i)
            rectangles_loc.append(i)       #We need to have two copies of this append because there may be only one rectangle and the groupRectangles method needs
                                           #at least 2 to work with.
        sections_loc, weights = cv2.groupRectangles(rectangles_loc, 1, 0.2) #grouping the rectangles that may overlap
    
        return sections_loc #Retuurning the location of the rectangles of each section

    def get_concat_v_blank(self, im1, im2, color=(255, 255, 255)):
        #This method will bind together two images vertically
        dst = Image.new('RGB', (max(im1.width, im2.width), im1.height + im2.height), color)
        dst.paste(im1, (0, 0))
        dst.paste(im2, (0, im1.height))
        return dst

    def get_concat_v_multi_blank(self, im_list):
        #This method will take each item of the list, bind together until the list is complete
        #It will bind two by two, sending the Image of the last bind + a new image to the "get_concat_v_blank" method. 
        #Its a loop between two methods that will return all images puut together on the same page vertically. 
        #Organizing one article in one column, instead of side by side. 
        #This will make it easier when trying to separate each paragraph
        _im = im_list.pop(0)
        for im in im_list:
            _im = self.get_concat_v_blank(_im, im)
        return _im

    def concat_and_save_imgs(self):
        #This is the main method.
        #It will organize all other methods, call them and later save the final image with the correct name.
        if self.number_ed < 4:
            self.get_title_article()
        else:
            self.final_img = self.cropped_img
        sections_loc = self.find_article_sections()
        im_list = [self.final_img.crop(i) for i in sections_loc]
        im = self.get_concat_v_multi_blank(im_list)
        fn, fext = os.path.splitext(self.path_img)
        if self.number_ed == 4:
            self.number_ed = 1
        elif self.number_ed == 5:
            self.number_ed = 2
        elif self.number_ed == 6:
            self.number_ed = 3
        im.save('{}/{}_{}{}'.format(self.final_path, fn, self.number_ed, fext))  
    
class clean_imgs_2004_2014():
    def __init__(self, path_img_editorial):
        self.path_img_editorial = path_img_editorial
    
    def detect_sections_of_editorial(self):
        #This method will create rectangles around chunks of the image that bind themselves together when we apply the filter inside the "detect_rectangles" function
        #This will allow us to separate the text from the noise around the image that we do not need.
        #It will select the bigger chuncks and cut them into separate objects. 
        #The bigger rectangles they will be our text, since the articles will ocupy most of the page. 

        image = cv2.imread(self.path_img_editorial, cv2.IMREAD_UNCHANGED) #Reading the image through cv2
        rectangles, image, dilate = detect_rectangles(image, 11, 7) #Calling the function "detect_rectangles" so we can apply the filters we want and return the position of the articles
        
        #We are filtering our articles by the amount of pixels it contains in each axis, or it's position on the image.
        #We do not want the bottom articles, because they are from another section, not the 'editorial' one, so we select only the rectangles that
        #start at least on the position 1900 of the Y axis or above, below that will be the section we do not want.
        article_sections_loc = [rec for rec in rectangles if rec[1] < 1900 and rec[2]-rec[0] > 600 and rec[3]-rec[1] > 400]
        
        #There may be an error while using the filters because some page may not be within the paramethers of most. We expect it to be really few articles, maybe one in a five hundred.
        if len(article_sections_loc) < 3:
            raise Exception('There is less than 3 articles being separate on this page. Check for value errors at xkernel or ykernel in \"detect_rectangles\"')
                
        for i in article_sections_loc: 
            #Reordering the articles so they are organized as they are presented in the newspaper
            #From left to right and from up to down. That means the first index will be the one that is the top article
            #the second index will be the bottom left, and the last index will be the bottom right.
            if i[1] < 1000:
                a = i
            elif i[1] > 1000 and i[0] < 500:
                b = i
            else:
                c = i
        article_sections_loc = [a, b, c]         
            
        pil_editorial = Image.open(self.path_img_editorial)
        editorials_cropped = [pil_editorial.crop(i) for i in article_sections_loc] #Cropping the image into smaller pieces that contains the separated articles
            
        return editorials_cropped
    
    def exclude_non_textual_elements(self):
        #This method was created so we can delete everything that is not part of the written text
        #In the future it will be easier for the OCR program to read it without too much noise and give a more precise text and structure of the article.
        
        editorials = self.detect_sections_of_editorial() #Calling the method detect_sections_of_editorial so we have the pillow object for each article.
        clean_editorials = []
        for index, editorial in enumerate(editorials):
            #Getting the index and the pillow images for each loop and passing it into variables
            image = np.array(editorial) #Transforming the Pillow object into an array so the CV can work with it.
            if index != 0:  
                #This will try to identify the newspaper's rectangle that they put text on capital letters to highlight certain parts of the text
                #Since we don't need those, we will be excluding them. They are already part of the text.
                rectangles, image, dilate = detect_rectangles(image, 7, 7)
                rectangle_to_be_excluded = [rectangle for rectangle in rectangles if rectangle[3]-rectangle[1] < 200]                
                if rectangle_to_be_excluded:                       
                    rectangle_to_be_excluded = rectangle_to_be_excluded[0] #Transforming a list of lists into just one list, since there is only one value inside
                    #This will substitude this particular part of the array into a blank space, therefore, deleting the image that occupies that space
                    #The array space was detected by the CV algorythm and it gave us the exact coordinates of the object
                    image[rectangle_to_be_excluded[1] : rectangle_to_be_excluded[3], rectangle_to_be_excluded[0] : rectangle_to_be_excluded[2]] = (255, 255, 255)
                    clean_editorials.append(image)  
                else:
                    clean_editorials.append(image)
                    #We won't raise errors on this particular block because there are different patterns throughout the years, and some do not have images to be excluded
            else:
                #This will try to identify the newspaper's mark on the first article and eliminate it. It is a small rectangle, the rest is big blocks of text
                rectangles, image, dilate = detect_rectangles(image, 4, 4) #Dilating the image 4,4 will be enough to separate the text from the image without binding both together
                rectangle_to_be_excluded = [rectangle for rectangle in rectangles if 100 < rectangle[2]-rectangle[0] < 200] #If it is between 100 and 200 pixels on the Y axis, it will be excluded
                if rectangle_to_be_excluded:
                    rectangle_to_be_excluded = rectangle_to_be_excluded[0] #Transforming a list of lists into just one list, since there is only one value inside
                    #This will substitude this particular part of the array into a blank space, therefore, deleting the image that occupies that space
                    #The array space was detected by the CV algorythm and it gave us the exact coordinates of the object
                    image[rectangle_to_be_excluded[1] : rectangle_to_be_excluded[3], rectangle_to_be_excluded[0] : rectangle_to_be_excluded[2]] = (255, 255, 255)  
                    clean_editorials.append(image)
                else:
                    raise Exception('Could not exclude the image of the article')

        return clean_editorials


if __name__ == "__main__":   
    #Elements for method 1
    linha_div1_met_1 = 'crops/linha_divisoria_met_1.jpg'  # image of the division line between each editorial
    linha_div2_met_1 = 'crops/segunda_linha_met_1.jpg'
    img_div1_met_1 = 'crops/img_remove.jpg'  # image of the image we want to be removed
    img_div2_met_1 = 'crops/terceira_linha_met_1.jpg'   #image of the line that encapsules a portion of text we want to exclude
    
    #Folders separation and storage
    where_to_save = 'Clean DB'
    files_2003_2004 = os.listdir('Banco de Dados/metodo 1')
    files_2004_2014 = os.listdir('Banco de Dados/metodo 2')
    
    #Logging the files we could not process through the program, they will be save in a .log file.
    logging.basicConfig(filename='images_failed.log', level = logging.DEBUG, filemode = 'a')
    logger = logging.getLogger()
    
    # Metodo 1 - entre 2003 e 2004
     for f in files_2003_2004:
         x=0
         ed_path = ('Banco de Dados/metodo 1/{}'.format(f))
         print(f)
         try:
             cropped_imgs = clean_imgs_2003_2004(f, ed_path, linha_div1_met_1, linha_div2_met_1, img_div1_met_1, img_div2_met_1).find_img_loc()
         except Exception as e: 
             error_msg = f'error at: {f} with the following message: {e}'
             print(error_msg)
             logger.info(error_msg)                 
             continue
    
         for i in cropped_imgs:
             x += 1            
             try:
                 final_img = columnize(i, x, f, where_to_save)
                 final_img.concat_and_save_imgs() #Save image
             except Exception as e: 
                 error_msg = f'error at: {f} with the following message: {e}'
                 print(error_msg)
                 logger.info(error_msg) 
                 continue
    
    #Metodo 2 = entre 2004 e 2014
    for f in files_2004_2014:
        x=0
        ed_path = (f'Banco de Dados/metodo 2/{f}')
        print(f)
        try:
            clean_editorials = editorial_crop_class = clean_imgs_2004_2014(ed_path).exclude_non_textual_elements()
        except Exception as e:
            error_msg = f'Could not crop the image \'{f}\', exception at editorial crop, error caught: {e}'
            print(error_msg)
            logger.info(error_msg) 
            continue        
        x = 3
        for i in clean_editorials:
            x+=1
            try:
                columnize(i, x, f, where_to_save).concat_and_save_imgs()
            except Exception as e:
                error_msg = f'Could not columnize the image \'{f}\', error caught: {e}'
                print(error_msg)
                logger.info(error_msg) 
                continue
    
    
    
