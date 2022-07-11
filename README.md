# StayTuned Engineering Exercise - Back-End

### Back-end Objective
Build a back-end demo that demonstrates what data you think should be stored to
accomplish this feature. You must persist data in a database. Give some thought to your
underlying data model design, queries, and indexes. You must also expose API endpoints
and provide some easy way to demonstrate them as working such as simple pages, scripts,
a postman workspace, or even putting it up on free cloud hosting. Feel free to use any
combination of language and database as long as they easily run on MacOS or linux.

### Back-end Solution Summary
For the database, product information is stored in the product table, and email notification requests are stored in the email_requests table. The Flask application has two endpoints, a GET method to get the product information to display/reference on the front-end; And a POST method to send to the email_requests table. For the POST request, I encrypted the first and last name values using the flask escape function, and then html unescape function when the email is ready to be sent out. In Python, I used a Background Scheduler to call a function every 5 minutes that queries the database for email_requests that meet the criteria (On sale for more than $1, and email_sent boolean value is false). If there are no results, it will print "No requests at this time" to the console/ubuntu journalctl log. If there are results, it will generate and send an email, then update the email_sent boolean value to true, so that it no longer is in the email queue.

## Technologies Used
### MySQL
MySQL database is used to store the product information and email requests that are coming in from the API.
To build the database, use the Scripts.sql file that contains the necessary queries.

### Flask (Python)
Flask is used to:
- Create API endpoints
- Serve front-end
- Query MySQL database for emails that are ready to be sent out, and then email and update the table

## Installation
### Folder Structure
```
FlaskApp
└───build
└───FlaskApp(repo)
```

Requirements to run:
- Python
- Pip
- credentials.json file that has username/password/host for the MySQL connection
- build folder from React App

This application was created on a Windows 10 desktop using:
- Python 3.10.4
- pip 22.0.4

Create Python Virtual Environment, install the dependencies, and run the application:

```sh
cd FlaskApp
pip install virtualenv
virtualenv env
env\Scripts\Activate
pip install -r requirements.txt
flask run
```

## API Endpoints
### Products
- URL: /api/products
- Method: GET

### Create
- URL: /api/create
- Method: POST

