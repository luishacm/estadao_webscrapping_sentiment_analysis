from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
import re
import time

#On this project is not possible to use Requests. The requests module do not allow us to use the search bar, since it only loads when
#you interact with the webpage activating its javascript. There are work arounds with other libraries that allows us to wait for the javascript to load, however, some are deprecated
#and/or the libraries are not easily available. This website do not allow webcrawling, that said, the slow pace help us to not get blocked by the server.
#The way to deal with this particular website is to use Selenium and only use Requests to download the images we already acquired the links. 
#Which already generates a few problems that this code tries to solve.
#Requests is faster, with another websites should be the best way.

#Options for the user
login = ("example@example.com") #It may be necessary to login into the website to get the image in its full quality.
                                #If that's the case, you have to call the function 'estadaoLogin()' after you ran the class 'getlinks'
password = ("examplepassword")
keywords = ["ministro", "ministerio", "ministra", "mec", "itamaraty"] #Choose which keywords are within your research
caderno = "Editorial" #Choose which section of the newspaper you are looking into. If you leave it blank it will search the whole newspaper
                      #The possibilities are the following: Economia, Politica, Internacional, Cidades, Caderno 2, Geral, Editorial, Primeira, Opinião, Esportes,
                      #Guia, Agrícola, Imóveis, Viagem, Empregos, Especial, Projetos, Seu Bairro Sul, Oportunidades, Seu Bairro Oeste, Telejornal, Informática, Automóveis,
                      #Casa, Estadinho, Painel de Negócios, Seu Bairro Leste

startyear = 2003 #The year that you want your search to start
endyear = 2014  #The year that you want your search to end
txtPath = "arquivos/links_down.txt" #Txt path to where the links will be stored. You should create the folder called 'arquivos' or change the path to a more desirable name

def initDriver(loadStrategy = "eager", headless=True):  #There are 3 options: normal, eager or none. eager is the recommended for this project.
    #Driver General Options
    #Options are to determine the user-agent so the website knows who is using their website.
    caps = DesiredCapabilities().FIREFOX
    options = FirefoxOptions() #Creating the header for your browser
    options.set_preference("general.useragent.override", "Mozilla/5.0 (X11;     Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0   Safari/537.36")    
    print(loadStrategy)
    caps["pageLoadStrategy"] = loadStrategy #The load strategy is determined when calling the function
    if headless:
        #The standard is to be headless, however, if you pass the function 'headless=False', this section won't run.
        #It will reduce memory usage, be faster, but you won't see the program working
        options.add_argument("--headless")
    driver = webdriver.Firefox(options=options, desired_capabilities=caps)  #Calling the webdriver will open a web page and create a new Object that can be worked with.
    return driver

def resetDriver(driver):
    # do memory-intensive work
    # closing and quitting is not what ultimately frees the memory, but it
    # is good to close the WebDriver session gracefully anyway.
    driver.close()
    driver.quit()
    print("Your browser has been reset")
    time.sleep(2)

def getrandomwebsite(driver):
    #This function was created to stop a bug from the website that when you put a link on the browser it won't update the page
    #to the link you've just put. Going to another website and back will solve this isue.
    #This will go to another website that doesn't exist.
    try:
        driver.get("https://www.foo.bar")
    except Exception: 
        #When you go to an inexisting website it will raise an error, this will handle the error and just continue, since it is expected.
        pass

class getlinks:
    #Calling this Class will create a .txt file in your code folder with all the links of images from the Estadão website 
    #according to the paramethers that were given in the begining of the code.
    def __init__(self, startyear, endyear, keywords, cardeno, stop=False, links_txt="links_down.txt"):
        #This is the constructor of the Class. Here stays all the information that will be shared between all the functions inside.
        #When the Class is called, all of these objects will be created.
        self.anos = [i if startyear != endyear else startyear for i in range(startyear, endyear+1)]
        self.keywords = keywords
        self.caderno = caderno
        self.links_txt = links_txt
        self.stop = stop
        self.driver = initDriver() #This will initiate the Selenium Webdriver and allows us to work with it as a function
        self.savelinks() #This will run the function inside this class called savelinks. This function call all of the other members
                         #of this class and when you call the Class it will run automatically. You can disable this and call it yourself from outside the class.
    
    def pagnum(self):
        #Find out the amount of pages there is in a Search Link and return that number as an Integer.
        #It will wait a few seconds until the element is shown after the page is fully loaded.
        try:
            page_number = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, '//span[@class="page-ultima-qtd"]'))).text
        except TimeoutException:
            print("Could not identify the number of pages")
            return 1
        return int(page_number)
    
    def findlinks(self):
        #This function was created to get all the links from the pages we are trying to download.
        #It will return a list of website links where you can find high quality downloadable images.
        self.driver.get(self.determinesearch()[0]) 
        referencesList = []
        z = 0
        if self.stop: #This will read the txt file and see where it stopped last.
            with open('arquivos/getlinkstopped.txt', 'r') as f:
                whereStopped = str([line for line in f][0]) #Will save the link and save as a string 
        for i in self.determinesearch():  
            if self.stop:
                if whereStopped != i:  #Trying to determine where we've stopped, it will stop only when the links match and continue from there.
                    continue           #It will only use this function if "stop" is set to True. By standard is False.
                else:
                    self.stop = False
                    with open(self.links_txt, 'r') as f:
                        referencesList = [line.rstrip('\n') for line in f] #Will get the Links List that we already got and restart from there.
                    print(referencesList)
            try:
                print('Working on the link ' + i)
                getrandomwebsite(self.driver)
                self.driver.get(i) #Go to the first link so we can determine the number of pages to download.
                x = 0
                for j in range(self.pagnum()): #It will loop over the number of pages
                    z += 1  #This number is counting the total amount of loops
                    
                    #This will get the link we have and replace the page number with the for loop
                    #This will get all the pages for a determined search result 
                    #Ex:Editorial com a palavra ministro em 2014 tem 20 páginas, vai realizar um loop por todas as páginas
                    pag_pos = i.find("/1/")
                    link = i[:pag_pos] + "/{}/".format(j+1) + i[pag_pos + 3:] 
                    
                    if z > 200: #When the amount of loops reaches this number, it will reset the driver so we can free memory.
                        resetDriver(self.driver)   #Calling the function that closes the webdriver.
                        self.driver = initDriver() #Creating a new instance of the Driver.
                        if x != 0: #Checking if we are already at the page we were supposed to, if not, it will get there
                            getrandomwebsite(self.driver)
                        else:
                            self.driver.get(link)
                        z = 0
                        
                    if x != 0: #Checking if we are already at the page we were supposed to, if not, it will get there                                         
                        getrandomwebsite(self.driver)
                        self.driver.get(link)
                    x += 1 
                    
                    try:
                        #Finding all the links that the search engine provided for us and saving the htmls as an object
                        links = WebDriverWait(self.driver, 2).until(EC.presence_of_all_elements_located((By.LINK_TEXT, "LEIA ESTA EDIÇÃO")))
                    except TimeoutException:
                        print("There are no links to be found ")
                        continue
                    try:
                        #Getting the html and find the "href" attribute, where the link to the piece is stored.
                        [referencesList.append(link.get_attribute("href")) for link in links]
                    except NoSuchElementException:
                        print("Error getting the href attributes from the page") 
                        pass
            except TimeoutException:
                print("The website has blocked our access, let's save what we got")    
                with open('arquivos/getlinkstopped.txt', 'w+') as f:
                    f.write(i)
                return list(set(referencesList))
        return list(set(referencesList))
    
    def determinesearch(self):
        #This function was created so we can have all the search links according to what the user has input above
        #This will fill all the blanks of the search and get us the exact page we are looking for
        #It will return a list of the base-links we are seeking.
        linksList = []
        for i in self.anos:
            #This will determine which decade lies the year we are trying to search.
            #It is the website that asks for this information.
            if i in list(range(2020, 2030)):
                decada = ("20")
            if i in list(range(2010,2020)):
                decada = ("10")
            if i in list(range(2000,2010)):
                decada = ("00")
            for j in self.keywords:  
                #For each keyword and each year it will create a different link that will be later appended in a list
                #The order of the links will be by year. First will come the oldest. 
                #Chose to use .format instead of f string so we can know easily which variables we are inputing                 
                searchlink = ("https://acervo.estadao.com.br/procura/#!/{}/Acervo//spo/1/20{}/{}//{}".format(j, decada, i, self.caderno)) 
                linksList.append(searchlink)   
        return linksList 
    
    def savelinks(self):
        #This function will call the function "findlinks", receive the list and later save it in a .txt file
        #If the .txt file does not exist, it will create one.
        links = self.findlinks()        
        with open(self.links_txt, "w+") as f:
            f.write("\n".join(links)) #Using .join will make it iterate through the list while saving each link and later an "enter"
                                      #so each link is in its own line.
        resetDriver(self.driver)
        
def estadaoLogin(driver):
    #At some versions of this website this function was necessary to download the images in its full quality
    #If needed, you have to call this function before calling to download the images. To get the links is not necessary.
    driver.get("https://acesso.estadao.com.br/login")
    driver.find_element(By.XPATH, '//input[@name="email_login"]').send_keys(login) #Send the login to the correct field
    driver.find_element(By.XPATH, '//input[@name="senha"]').send_keys(password)    #Send the password to the correct field
    driver.find_element(By.XPATH, '//input[@value="Entrar"]').click()              #Clicking on the "Enter" so you can login
    time.sleep(2)
    print("Fez login!")
    
def month_string_to_number(string):
    #Transforming the month in writing that we got from the website to a number so it will be better organized in the database
    m = {
        'jan': "01",
        'fev': "02",
        'mar': "03",
        'abr': "04",
         'mai': "05",
         'jun': "06",
         'jul': "07",
         'ago': "08",
         'set': "09",
         'out': "10",
         'nov': "11",
         'dez': "12"
        }
    s = string.lower()
    try:
        out = m[s]
        return out
    except Exception:
        return string

def downloadimages(txtPath, stop):
    #This is the second block of the code: after we got all the links, we will download them now.
    headers = { #This headers is for the requests library. Without it, it's possible that the website will block the download of the images.
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
    }
    driver = initDriver(loadStrategy='normal') #Creating an instance of the driver. Here you can determine its loadStrategy. The default mode is loadStrategy='eager'
                                               #You can also determine if you want it to be headless or not. default: headless=True
    z=0
    lines = [line.rstrip('\n') for line in open(txtPath)] #Opening the txt file with links we've saved and saving each one as an element in a list  
    if stop is True: #This will read the txt file and see where it stopped last.
        with open('arquivos/wherestopped.txt', 'r') as f:
            whereStopped = str([line for line in f][0]) #Transforming the link on the txt file from a list to a single string so we can match it in the future
    else:
        whereStopped = ""
    for i in lines:
        #Checking the place we last stopped and restarting from there.
        #This will try to match both strings, the one we saved and the one in the for loop
        #if it is a match, it will begin.
        if i != whereStopped and stop is True:  
            continue
        elif i == whereStopped and stop is True:
            print("Restarting where we stopped")
            stop = False
        else:
            pass
            
        if z > 200: #When the amount of loops reaches this number, it will reset the driver so we can save memory.
            resetDriver(driver)   #Calling the function that closes the webdriver.
            driver = initDriver(loadStrategy='normal') #Creating a new instance of the Driver.
            getrandomwebsite(driver) #Getting a random website so it won't bug the main website
            z=0
        z+=1   
        
        time.sleep(4) #This wait time is necessary, otherwise the website will block our access.
        try:          
            getrandomwebsite(driver) #Getting a random website so it won't bug the main website.
            driver.get(i) #Asking the driver to go to the website
            
            try:
                #Catching when the website blocks our access and raising an error
                error = driver.find_element_by_xpath("//h1[contains(text(),'Access Denied')]").text            
            except Exception:
                error = ''
                pass            
            if error == 'Access Denied':
                print(error)
                raise TimeoutException #Since it is and expected error down below, we are raising TimeoutException. But the best practice would be to raise an Exception.
                
            try:
                #This will find the source of the link to be downloaded
                img = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//img[@class='BRnoselect']")))
            except TimeoutException:
                print("Could not find the link to download the image: " + i)
                with open('arquivos/notdownloaded.txt', 'a+') as f:    #The links that give an error will be stored in a txt file that can be later accessed and downloaded
                    f.write(i)
                    f.write('\n')
                continue
            src = img.get_attribute('src') #Getting the attribute "source" from the XPath we determine above
            try:
                srcname = driver.find_element_by_xpath("//h1[@class='edicao-data']").text #This will find the day, month and year this piece was made
            except NoSuchElementException:
                print("Could not find the name of the image: " + i)
                with open('arquivos/notdownloaded.txt', 'a+') as f: #The links that give an error will be stored in a txt file that can be later accessed and downloaded
                    f.write(i)
                    f.write('\n')
                continue            
            #Rewriting the name of the piece we got from the website to a format that fits better in a database
            subname = re.sub('[^A-Za-z0-9]+', '', srcname) #Using regex to get only letters and numbers
            dia = subname[29:31] #Finding the location of the day through the string index
            mes = subname[33:36] #Finding the location of the month through the string index
            mes = month_string_to_number(mes) #Transforming the string in writing to a number
            ano = re.sub('[^0-9]+', '', srcname) #Using regex to only get numbers, so the location of the year in the string will be precise.
            ano = ano[2:6] #Finding the location of the year through the string index
            nome = ("{} {} {} {} Estadao".format(ano, mes, dia, caderno)) #Creating a name for the file that will be organised in one folder
            with open(("Banco de Dados/{}.jpg".format(nome)), "wb") as f: #Saving the image to a Database. You will need to create the folder "Banco de Dados"
                f.write(requests.get(src, headers=headers).content)  #This will request the image to be downloaded  
        except TimeoutException:
            print("Could not finish downloading all the links: " + i)
            with open('arquivos/wherestopped.txt', 'w+') as f:   #Saving the link that we last tried downloading so we latter can opt to restart from there.
                f.write(i)
            resetDriver(driver)
            return error       
    return 'done'         
                     
if __name__ == "__main__":
    #getlinks(startyear, endyear, keywords, caderno, stop=False, links_txt=txtPath)   #Calling the class getlinks so we can create or .txt file.
                                                                                     #You can also put at the end of the parentheses the name you want for the .txt file
                                                                                     #for example (links_txt = "links_down.txt")
                                                                                     #Turn stop to True if you want to return to where it has stoped
    
    while True:                                                                     
        response = downloadimages(txtPath, False)  #Calling the function that will download the images.
                                                   #You can comment this section, or the above, if you want one or the other.
                                                   #Determine this boolean as True if you want to keep downloading the images where you've last stopped.
                                                   #Put it as False if you want to download the links from the start.

        
        if response == 'Access Denied':            #The Requests library creates a few problems with the website, since it doesn't allow webcrawling
                                                   #It will block our access every few minutes. This will keep the code running and keep downloading.
            print("Let's wait 20 minutes and try again")
            time.sleep(1200)
        elif response == 'done':                          
            print("We are done, check your files")
            break
        else:
            print('not sure what went wrong: ' + response)


