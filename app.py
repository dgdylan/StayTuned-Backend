from html import unescape
from flask import Flask, request, jsonify, escape
from flask_cors import cross_origin
from flaskext.mysql import MySQL
import json
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.message import EmailMessage
from flask_cors import CORS
import sys

#Open credential file for necessary values
with open('credentials.json') as data_file:
    data = json.load(data_file)

username = data['username']
pw = data['password']
db = data['db']
host = data['host']
sender_email = data['sender_email']
email_pw = data['email_pw']

app = Flask(__name__, static_folder="../build", static_url_path='/')
CORS(app)

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = username
app.config['MYSQL_DATABASE_PASSWORD'] = pw
app.config['MYSQL_DATABASE_DB'] = db
app.config['MYSQL_DATABASE_HOST'] = host

mysql.init_app(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')


#GET Method, returns the product table from the MySQL database
#Calculates the sale price and displays it as product_current_price
#product_current_price will display on the website as the price
@app.route('/api/products', methods=["GET"])
@cross_origin(allow_headers=['*'])
def get_products():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = '''
        SELECT  product_id,
                product_model_number,
                product_brand,
                product_name,
                product_desc,
                product_price,
                product_discount_pctg,
                CAST((product_price - (product_price * product_discount_pctg)) as DECIMAL(10,2)) as product_current_price,
                quantity,
                img_name
        FROM   project.product 
        '''
        cursor.execute(sql)
        r = [dict((cursor.description[i][0], value)
                for i, value in enumerate(row)) for row in cursor.fetchall()]
        return jsonify(r)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

#POST Method, takes in the product_id of the item that the user wants notifications for
#price_at_moment will be the price of what the item currently is
#Email, first name and last name are taken in for the email that will be sent
@app.route('/api/create', methods=['POST'])
def create_request():
    try:        
        _json = request.json
        _product_id = _json['product_id']
        _email_address = _json['email_address']
        _first_name = escape(_json['first_name'])
        _last_name = escape(_json['last_name']	)
        _price_at_moment = _json['price_at_moment']

        if _product_id and _email_address and _first_name and _last_name and request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor()		
            sql = '''
            INSERT INTO project.email_requests
                        (product_id,
                        email_address,
                        first_name,
                        last_name,
                        price_at_moment)
            VALUES      (%s,
                        %s,
                        '%s',
                        '%s',
                        %s) 
            '''
            bindData = (_product_id, _email_address, _first_name, _last_name, _price_at_moment)            
            cursor.execute(sql, bindData)
            conn.commit()
            response = jsonify('Request added successfully!')
            response.status_code = 200
            return response
        else:
            return showError()
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()

#Method to display an error if needed
def showError(error=None):
    message = {
        'status': 404,
        'message': 'Not found' + request.url,
    }
    response = jsonify(message)
    response.status_code = 404
    return response


#Method to update the email_sent boolean value to true after the email has been sent to the user
#This will take the request off the SELECT statement in run_check since it will no longer meet the criteria
#Will update based on the customer_id
def updateStatus(customer_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = '''UPDATE project.email_requests SET email_sent = 1 WHERE customer_id = %s'''
        bindData = customer_id
        cursor.execute(sql, bindData)
        conn.commit()
        print('Table updated')
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()    

#Method to send the email out once it has met the criteria, will take in values from the dictionary to compose the message
def sendEmail(row):
    rec_email = str(row['email_address'])
    first_name = unescape(str(row['first_name'])).replace("'", "")
    last_name = unescape(str(row['last_name'])).replace("'", "")
    product_name = str(row['product_brand']) + ' ' + str(row['product_name'])
    price_at_moment = str(row['price_at_moment'])
    current_sale_price = str(row['current_sale_price'])
    sale = str(row['sale'])
    subject = product_name + ' is on sale!'
    body = "Hello " + first_name + ' ' + last_name + ", \nThe item " + product_name + " is currently on sale for $" + current_sale_price + ", saving you $" + sale + "!"
    message = EmailMessage()
    message.set_content(body)
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = rec_email
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, email_pw)
    print("Login success")
    sys.stdout.flush() #To show print on journalctl --follow -u FlaskApp
    server.send_message(message)
    print('Email has been sent to ', rec_email)
    sys.stdout.flush() #To show print on journalctl --follow -u FlaskApp
    server.quit()

#Main method to check if there has been a sale of $1 or more on the requested item
#If there are no requests, it will print to the console No requests at the momemnt
#Otherwise it will loop through the array of rows and pass that in the email method
#After the email method we will update the status so that it will no longer meet the criteria
def run_check():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = '''
        SELECT  a.customer_id,
	            a.product_id,
                a.email_address,
	            a.first_name,
                a.last_name,
                a.price_at_moment,
                CAST((b.product_price - (b.product_price * b.product_discount_pctg)) as DECIMAL(10,2)) as current_sale_price,
                CAST((a.price_at_moment - (b.product_price - (b.product_price * b.product_discount_pctg))) as DECIMAL(10,2)) as sale,
                b.product_brand,
                b.product_name
        FROM    project.email_requests AS a
                INNER JOIN project.product AS b
                    ON a.product_id = b.product_id
        WHERE   (a.price_at_moment - (b.product_price - (b.product_price * b.product_discount_pctg))) >= 1 AND a.email_sent = 0; 
        '''
        cursor.execute(sql)
        r = [dict((cursor.description[i][0], value)
                for i, value in enumerate(row)) for row in cursor.fetchall()]
        if not r:
            print('No requests at the moment.')
            sys.stdout.flush() #To show print on journalctl --follow -u FlaskApp
        for row in r:
            sendEmail(row)
            updateStatus(row['customer_id'])
        return r
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

# run_check()

# Running with the schedule import will make sure that the run_check function
# is checking the database for the specified time intervals
scheduler = BackgroundScheduler()
scheduler.add_job(func=run_check, trigger="interval", seconds=300)
scheduler.start()

#Shutdown upon exit
atexit.register(lambda: scheduler.shutdown())