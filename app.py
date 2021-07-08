from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import schedule

x=1
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

app = Flask(__name__)

@app.route('/')
def test():
    return render_template("input.html")

@app.route('/', methods = ['POST', 'GET'])

def input():
    #taking input from input html page
    url = request.form['1']
    desired_price = int(request.form['2'])
    email_address = request.form['3']
    
    
    def check_price():
        print("checking...")
        global x
        page = requests.get(url, headers = headers)
        soup = BeautifulSoup(page.content, 'lxml')

        if "amazon" in url.lower(): #if url is from amazon
            title = soup.find(id="productTitle").get_text().strip()
            try:
                price = soup.find(id="priceblock_ourprice").get_text().replace('₹','').replace(',','').strip()
            except:
                price = soup.find(id="priceblock_dealprice").get_text().replace('₹','').replace(',','').strip()
            

        elif "flipkart" in url.lower(): #if url is from flipkart
            title = soup.find("span", {"class": "B_NuCI"}).get_text().strip()
            price = soup.find("div", {"class": "_30jeq3 _16Jk6d"}).get_text()[1:].replace(',','').strip()

        
        my_price = int(float(price))
        print(f'Product name: {title}; Price: {price}')

        if(my_price < desired_price):
            send_mail(title)
            x=x+1
            
        else:
            print('No mail sent!')

    

    def send_mail(title):
        mail_content = f'Hey there, the price for the product: {title} has dropped according to your budget.\nCheck the amazon link: {url}'

        #The mail addresses and password
        sender_address = 'xyz@gmail.com' #sender gmail address
        sender_pass = '******' #sender gmail password
        
        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = email_address
        message['Subject'] = '!!!PRICE DROP ALERT!!!'   #The subject line
        #The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, email_address, text)
        print('Mail Sent!')  
    
    if(x==1): #checks price only if mail hasn't been sent yet
        schedule.every(10).seconds.do(check_price) #checks price every 10 hour
        
        while(x==1):
            schedule.run_pending()
            time.sleep(1)
    

    return render_template("output.html")
        

if __name__ == "__main__":
    app.run() #running the flask app
    
