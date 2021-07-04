# ///////////////////////////////////////////////////////////////
#
# CREATED: NIZAR IZZUDDIN Y.F
# V: 1.0.0
# GITHUB: https://github.com/nizariyf
#
# This project is free for everyone, if there is an error please contribute in this
#
# ///////////////////////////////////////////////////////////////

import time, csv, datetime, socket, getopt, sys, os, random, json
from . usage import Help
from . utils import Color
from transformers import pipeline

def show(description, version):
  logo = '''                                                
          +                +++++++++* ++++        
          +++++           +++++++++++++++++:       
          +++++++++      ++++++++++++++++++#       
          *++++++++++++++++++++++++++++++          
          ++++++++++++++++++++++++++++++           
          ++++++++++++++++++++++++++++++           
            +++++++++++++++++++++++++++            
            +++++++++++++++++++++++++             
              +++++++++++++++++++++++              
        +++++++++++++++++++++++++*                
        +++++++++++++++++++++++                   
            +++++++++++++++                        
                                                  '''
  print(Color('cbl'),logo,Color('cend'))
  print(Color('cg'))
  print('\t',description)
  print('\t Version',version)
  print(Color('cend'))

def write_log(e):
  f = open('twibot_log.txt', 'a+')
  f.write(f'----------- {str(datetime.datetime.now())} ----------\n')
  f.write(str(e) + '\r\n')
  f.close()

try:
  from selenium import webdriver
  from selenium import common
  from selenium.webdriver.common import keys
  from selenium.common.exceptions import NoSuchElementException
  from selenium.webdriver.firefox.options import Options
  from selenium.webdriver.common.action_chains import ActionChains
  from webdriver_manager.firefox import GeckoDriverManager
except Exception as ex:
  write_log(ex)
  Help(3)

# ------- SECTION DRIVER -------

options = Options()
options.headless = True
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1920,1080')
options.add_argument('--start-maximized')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')

with open('.config.json') as json_data:
  cfg = json.load(json_data)

# ------- SECTION GPT NEO -------
def generate_word(word):
  generator = pipeline('text-generation', model=cfg['AiTextGeneration']['model'])
  text = generator(word, max_length=50, do_sample=True, temperature=0.9)
  return text[0]['generated_text']

# ------- SECTION TWITTER BOT -------

class Twitter:

  def __init__(self, email, password):
    self.email = email
    self.password = password
    self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)
    self.bot = False
    self.skip = False
    self.is_logged_in = False

  def check_element(self,xpath):
    try:
      self.driver.find_element_by_xpath(xpath)
      return True
    except NoSuchElementException:
      return False

  def login(self):
    driver = self.driver
    driver.get('https://twitter.com/login')
    time.sleep(4)

    try:
      email = driver.find_element_by_name('session[username_or_email]')
      password = driver.find_element_by_name('session[password]')
    except NoSuchElementException:
      time.sleep(3)
      email = driver.find_element_by_name('session[username_or_email]')
      password = driver.find_element_by_name('session[password]')
    
    email.clear()
    password.clear()
    email.send_keys(self.email)
    password.send_keys(self.password)

    try:
      button_login = driver.find_element_by_xpath('//div[@data-testid="LoginForm_Login_Button"]')
      ActionChains(driver).move_to_element(button_login).click(button_login).perform()
    except:
      time.sleep(2)
      password.send_keys(keys.Keys.RETURN)

    time.sleep(10)

    if self.check_element('//form[@id="login-challenge-form"]') == True:
      print(f'{Color("cr")}    [x] Skip account due to code{Color("cend")}')
      write_log(f'Skip account {self.email} due to code')
      self.skip = True
    
    if self.check_element('//input[@type="tel"]') == True:
      print(f'{Color("cr")}    [x] Skip account due to code{Color("cend")}')
      write_log(f'Skip account {self.email} due to code')
      self.skip = True

    if driver.current_url == 'https://twitter.com/login/check':
      print(f'{Color("cr")}    [x] BOT account detected{Color("cend")}')
      write_log(f'BOT account {self.email} detected')
      self.bot = True

    if driver.current_url == 'https://twitter.com/account/access':
      print(f'{Color("cr")}    [x] Account lock{Color("cend")}')
      write_log(f'Account {self.email} lock')
      self.skip = True

    if driver.current_url == 'https://twitter.com/login?username_disabled=true&redirect_after_login=%2F':
      print(f'{Color("cr")}    [x] Account disabled{Color("cend")}')
      write_log(f'Account {self.email} disabled')
      self.skip = True

    phone = ''

    if '+' in self.email:
      phone = self.email.split('+')
      phone = phone[1]
    
    if driver.current_url in [f'https://twitter.com/login/error?username_or_email=%2B{phone}&redirect_after_login=%2Fhome',f'https://twitter.com/login/error?username_or_email=%2B{phone}&redirect_after_login=%2F',f'https://twitter.com/login/error?username_or_email=%2B{self.email}&redirect_after_login=%2Fhome',f'https://twitter.com/login/error?username_or_email=%2B{self.email}&redirect_after_login=%2F']:
      print(f'{Color("cr")}    [x] Skip account because there is an error{Color("cend")}')
      write_log(f'Skip account {self.email} because there is an error')
      self.skip = True

    if driver.current_url != 'https://twitter.com/home':
      time.sleep(10)

    self.is_logged_in = True

  def logout(self):
    if self.is_logged_in == False:
      print(f'{Color("cr")}    [x] You must log in first!{Color("cend")}')
    elif self.skip == True:
      print(f'{Color("cr")}    [x] Skip account because there is an error{Color("cend")}')
    elif self.bot == True:
      print(f'{Color("cr")}    [x] BOT account detected{Color("cend")}')
    else:
      driver = self.driver
      driver.get('https://twitter.com/home')
      time.sleep(4)

      try:
        driver.find_element_by_xpath('//div[@data-testid="SideNav_AccountSwitcher_Button"]').click()
      except NoSuchElementException:
        time.sleep(3)
        sideNav = driver.find_element_by_xpath('//div[@data-testid="SideNav_AccountSwitcher_Button"]')
        ActionChains(driver).move_to_element(sideNav).click(sideNav).perform()

      time.sleep(3)

      try:
        driver.find_element_by_xpath('//a[@data-testid="AccountSwitcher_Logout_Button"]').click()
      except NoSuchElementException:
        time.sleep(3)
        divPic = driver.find_element_by_xpath('//a[@data-testid="AccountSwitcher_Logout_Button"]')
        ActionChains(driver).move_to_element(divPic).click(divPic).perform()

      time.sleep(3)

      try:
        driver.find_element_by_xpath('//div[@data-testid="confirmationSheetConfirm"]').click()
      except NoSuchElementException:
        time.sleep(3)
        confirmButton = driver.find_element_by_xpath('//div[@data-testid="confirmationSheetConfirm"]')
        ActionChains(driver).move_to_element(confirmButton).click(confirmButton).perform()

      time.sleep(3) 
      self.is_logged_in = False
      driver.quit()

  def post_tweets(self,tweetBody):
    if self.is_logged_in == False:
      print(f'{Color("cr")}    [x] You must log in first!{Color("cend")}')
    elif self.skip == True:
      print(f'{Color("cr")}    [x] Skip account because there is an error{Color("cend")}')
    elif self.bot == True:
      print(f'{Color("cr")}    [x] BOT account detected{Color("cend")}')
    else:
      driver = self.driver  

      try:
        driver.find_element_by_xpath('//a[@data-testid="SideNav_NewTweet_Button"]').click()
      except NoSuchElementException:
        time.sleep(3)
        sideNav = driver.find_element_by_xpath('//a[@data-testid="SideNav_NewTweet_Button"]')
        ActionChains(driver).move_to_element(sideNav).click(sideNav).perform()

      time.sleep(4) 
      body = tweetBody
      print(f'    Tweet Word: {body}')

      try:
        driver.find_element_by_xpath('//div[@role="textbox"]').send_keys(body)
      except NoSuchElementException:
        time.sleep(3)
        driver.find_element_by_xpath('//div[@role="textbox"]').send_keys(body)

      time.sleep(4)
      driver.find_element_by_class_name('notranslate').send_keys(keys.Keys.ENTER)

      try:
        driver.find_element_by_xpath('//div[@data-testid="tweetButton"]').click()
      except NoSuchElementException:
        time.sleep(2)
        tweetButton = driver.find_element_by_xpath('//div[@data-testid="tweetButton"]')
        ActionChains(driver).move_to_element(tweetButton).click(tweetButton).perform()

      print(f'{Color("cg")}    [+] Writing Successful Tweets{Color("cend")}')
      time.sleep(4)

  # ------- RETWEET TWEET -------
  
  def retweet_tweet(self, tweetLink):
    if self.is_logged_in == False:
      print(f'{Color("cr")}    [x] You must log in first!{Color("cend")}')
    elif self.skip == True:
      print(f'{Color("cr")}    [x] Skip account because there is an error{Color("cend")}')
    elif self.bot == True:
      print(f'{Color("cr")}    [x] BOT account detected{Color("cend")}')
    else:
      driver = self.driver
      
      time.sleep(4)
      driver.get(tweetLink)
      time.sleep(4)

      if self.check_element('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@class="css-1dbjc4n r-1awozwy r-xoduu5 r-16y2uox r-1777fci r-1jgb5lz r-1ye8kvj r-1qfz7tf r-18scu15 r-13qz1uu"]') == False:

        try:
          if self.check_element('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="unretweet"]') == False:
            try:
              driver.find_element_by_xpath('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="retweet"]').click()
            except NoSuchElementException:
              time.sleep(2)
              section_retweet = driver.find_element_by_xpath('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="retweet"]')
              ActionChains(driver).move_to_element(section_retweet).click(section_retweet).perform()

            time.sleep(2)

            try:
              driver.find_element_by_xpath('//div[@data-testid="retweetConfirm"]').click()
            except NoSuchElementException:
              time.sleep(2)
              button_retweet = driver.find_element_by_xpath('//div[@data-testid="retweetConfirm"]')
              ActionChains(driver).move_to_element(button_retweet).click(button_retweet).perform()
          
          time.sleep(2)

          if self.check_element('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="unlike"]') == False:
            try:
              driver.find_element_by_xpath('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="like"]').click()
            except NoSuchElementException:
              time.sleep(2)
              button_like = driver.find_element_by_xpath('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="like"]')
              ActionChains(driver).move_to_element(button_like).click(button_like).perform()

          print(f'{Color("cg")}    [+] Successfully retweet tweets{Color("cend")}')
        except:
          print(f'{Color("cr")}    [-] An error occurred{Color("cend")}')
      else:
        print(f'{Color("cr")}    [-] Tweet link doesn\'t exist{Color("cend")}')

  # ------- QUOTE RETWEET TWEET -------
  
  def quote_tweet(self, tweetLink, tweetWord):
    if self.is_logged_in == False:
      print(f'{Color("cr")}    [x] You must log in first!{Color("cend")}')
    elif self.skip == True:
      print(f'{Color("cr")}    [x] Skip account because there is an error{Color("cend")}')
    elif self.bot == True:
      print(f'{Color("cr")}    [x] BOT account detected{Color("cend")}')
    else:
      driver = self.driver

      time.sleep(4)
      driver.get(tweetLink)
      time.sleep(4)

      if self.check_element('//div[@class="css-1dbjc4n r-1awozwy r-xoduu5 r-16y2uox r-1777fci r-1jgb5lz r-1ye8kvj r-1qfz7tf r-18scu15 r-13qz1uu"]') == False:

        try:
          if self.check_element('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="unlike"]') == False:
            try:
              driver.find_element_by_xpath('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="like"]').click()
            except NoSuchElementException:
              time.sleep(2)
              button_like = driver.find_element_by_xpath('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="like"]')
              ActionChains(driver).move_to_element(button_like).click(button_like).perform()

          time.sleep(2)

          if self.check_element('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="unretweet"]') == False:
            try:
              driver.find_element_by_xpath('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="retweet"]').click()
            except NoSuchElementException:
              time.sleep(2)
              section_retweet = driver.find_element_by_xpath('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="retweet"]')
              ActionChains(driver).move_to_element(section_retweet).click(section_retweet).perform()
          elif self.check_element('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="retweet"]') == False:
            try:
              driver.find_element_by_xpath('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="unretweet"]').click()
            except NoSuchElementException:
              time.sleep(2)
              section_retweet = driver.find_element_by_xpath('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="unretweet"]')
              ActionChains(driver).move_to_element(section_retweet).click(section_retweet).perform()

          time.sleep(2)

          try:
            driver.find_element_by_xpath('//a[@role="menuitem"]').click()
          except NoSuchElementException:
            time.sleep(2)
            button_retweet = driver.find_element_by_xpath('//a[@role="menuitem"]')
            ActionChains(driver).move_to_element(button_retweet).click(button_retweet).perform()

          time.sleep(4)

          try:
            driver.find_element_by_xpath('//div[@role="textbox"]').send_keys(tweetWord)
          except NoSuchElementException:
            time.sleep(3)
            driver.find_element_by_xpath('//div[@role="textbox"]').send_keys(tweetWord)

          time.sleep(4)
          driver.find_element_by_class_name('notranslate').send_keys(keys.Keys.ENTER)

          try:
            driver.find_element_by_xpath('//div[@data-testid="tweetButton"]').click()
          except NoSuchElementException:
            time.sleep(2)
            tweetButton = driver.find_element_by_xpath('//div[@data-testid="tweetButton"]')
            ActionChains(driver).move_to_element(tweetButton).click(tweetButton).perform()

          time.sleep(2)

          print(f'{Color("cg")}    [+] Successfully quote retweet tweets{Color("cend")}')
        except Exception as e:
          print(f'{Color("cr")}    [-] An error occurred{Color("cend")}')
          print(e)
      else:
        print(f'{Color("cr")}    [-] Tweet link doesn\'t exist{Color("cend")}')

  # ------- REPLY TWEET -------
  
  def reply_tweet(self, tweetLink, tweetWord):
    if self.is_logged_in == False:
      print(f'{Color("cr")}    [x] You must log in first!{Color("cend")}')
    elif self.skip == True:
      print(f'{Color("cr")}    [x] Skip account because there is an error{Color("cend")}')
    elif self.bot == True:
      print(f'{Color("cr")}    [x] BOT account detected{Color("cend")}')
    else:
      driver = self.driver

      time.sleep(4)
      driver.get(tweetLink)
      time.sleep(4)

      if self.check_element('//div[@class="css-1dbjc4n r-1awozwy r-xoduu5 r-16y2uox r-1777fci r-1jgb5lz r-1ye8kvj r-1qfz7tf r-18scu15 r-13qz1uu"]') == False:

        try:
          if self.check_element('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="unlike"]') == False:
            try:
              driver.find_element_by_xpath('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="like"]').click()
            except NoSuchElementException:
              time.sleep(2)
              button_like = driver.find_element_by_xpath('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="like"]')
              ActionChains(driver).move_to_element(button_like).click(button_like).perform()

          time.sleep(2)

          try:
            driver.find_element_by_xpath('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="reply"]').click()
          except NoSuchElementException:
            time.sleep(2)
            section_reply = driver.find_element_by_xpath('//article[@class="css-1dbjc4n r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh"]//div[@data-testid="reply"]')
            ActionChains(driver).move_to_element(section_reply).click(section_reply).perform()

          time.sleep(4)

          try:
            driver.find_element_by_xpath('//div[@role="textbox"]').send_keys(tweetWord)
          except NoSuchElementException:
            time.sleep(3)
            driver.find_element_by_xpath('//div[@role="textbox"]').send_keys(tweetWord)

          time.sleep(4)
          driver.find_element_by_class_name('notranslate').send_keys(keys.Keys.ENTER)

          try:
            driver.find_element_by_xpath('//div[@data-testid="tweetButton"]').click()
          except NoSuchElementException:
            time.sleep(2)
            tweetButton = driver.find_element_by_xpath('//div[@data-testid="tweetButton"]')
            ActionChains(driver).move_to_element(tweetButton).click(tweetButton).perform()

          time.sleep(2)

          print(f'{Color("cg")}    [+] Successfully reply tweets{Color("cend")}')
        except Exception as e:
          print(f'{Color("cr")}    [-] An error occurred{Color("cend")}')
          print(e)
      else:
        print(f'{Color("cr")}    [-] Tweet link doesn\'t exist{Color("cend")}')

# ------- MENU -------
def tweet(a,link='',ai='',hashtag='',tag=''):
  # ------- READ INPUT FROM CLI -------
  show('Twibot by Nizar', 'v1.0.0')
  print()

  if hashtag == False:
    hashtag = ''
  if tag == False:
    tag = ''

  if a == 1:
    time_now = str(datetime.datetime.now())[:-7]
    print(f'TwitterBot started at {time_now} !')
    try:
      with open('./wordlist.csv','r') as word_obj:
        csv_word = csv.reader(word_obj)
        words_data = [d for d in csv_word]
        count_line = len(words_data)

      with open('./account.csv', 'r') as read_obj:
        csv_reader = csv.reader(read_obj)
        header = next(csv_reader)
        if header != None:
          for number, item in enumerate(csv_reader):
            number = number+1
            print(f'[*] Login account twitter {number}')
            print(f'    Username/Phone Number : {item[0]}')
            start = Twitter(item[0], item[1])
            start.login()

            #------- WORD RANDOM ------
            random_line = random.randint(0, count_line-1)
            count_words = len(words_data[random_line])
            random_word = random.randint(0, count_words-1)
            words = words_data[random_line][random_word]
            if ai == True:
              words = generate_word(words)
            word = f'{words}\n{tag}\n\n{hashtag}'

            start.post_tweets(word)
            start.logout()
            print(f'[*] Logout account twitter {number}')
    except Exception as e:
      print(e)
      start.logout()
      write_log(e)
  elif a == 2:
    time_now = str(datetime.datetime.now())[:-7]
    print(f'TwitterBot started at {time_now} !')
    link_tweet = link
    try:
      with open('./account.csv', 'r') as read_obj:
        csv_reader = csv.reader(read_obj)
        header = next(csv_reader)
        if header != None:
          for number, item in enumerate(csv_reader):
            number = number+1
            print(f'[*] Login account twitter {number}')
            print(f'    Username/Phone Number : {item[0]}')
            start = Twitter(item[0], item[1])
            start.login()
            start.retweet_tweet(link_tweet)
            start.logout()
            print(f'[*] Logout account twitter {number}')
    except Exception as e:
      start.logout()
      print(e)
      write_log(e)
  elif a == 3:
    time_now = str(datetime.datetime.now())[:-7]
    print(f'TwitterBot started at {time_now} !')
    link_tweet = link
    try:
      with open('./wordlist.csv','r') as word_obj:
        csv_word = csv.reader(word_obj)
        words_data = [d for d in csv_word]
        count_line = len(words_data)

      with open('./account.csv', 'r') as read_obj:
        csv_reader = csv.reader(read_obj)
        header = next(csv_reader)
        if header != None:
          for number, item in enumerate(csv_reader):
            number = number+1
            print(f'[*] Login account twitter {number}')
            print(f'    Username/Phone Number : {item[0]}')
            start = Twitter(item[0], item[1])
            start.login()

            #------- WORD RANDOM ------
            random_line = random.randint(0, count_line-1)
            count_words = len(words_data[random_line])
            random_word = random.randint(0, count_words-1)
            words = words_data[random_line][random_word]
            if ai == True:
              words = generate_word(words)
            word = f'{words}\n{tag}\n\n{hashtag}'

            start.quote_tweet(link_tweet, word)
            start.logout()
            print(f'[*] Logout account twitter {number}')
    except Exception as e:
      start.logout()
      print(e)
      write_log(e)
  elif a == 4:
    time_now = str(datetime.datetime.now())[:-7]
    print(f'TwitterBot started at {time_now} !')
    link_tweet = link
    try:
      with open('./wordlist.csv','r') as word_obj:
        csv_word = csv.reader(word_obj)
        words_data = [d for d in csv_word]
        count_line = len(words_data)

      with open('./account.csv', 'r') as read_obj:
        csv_reader = csv.reader(read_obj)
        header = next(csv_reader)
        if header != None:
          for number, item in enumerate(csv_reader):
            number = number+1
            print(f'[*] Login account twitter {number}')
            print(f'    Username/Phone Number : {item[0]}')
            start = Twitter(item[0], item[1])
            start.login()

            #------- WORD RANDOM ------
            random_line = random.randint(0, count_line-1)
            count_words = len(words_data[random_line])
            random_word = random.randint(0, count_words-1)
            words = words_data[random_line][random_word]
            if ai == True:
              words = generate_word(words)
            word = f'{words}\n{tag}\n\n{hashtag}'

            start.reply_tweet(link_tweet, word)
            start.logout()
            print(f'[*] Logout account twitter {number}')
    except Exception as e:
      start.logout()
      print(e)
      write_log(e)