from flask import Flask, render_template, request, redirect, session, flash, url_for
# import the Connector function
from mysqlconnection import MySQLConnector
import re
# was unable to create a single regex expression for name.  Need to work more on regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')

app = Flask(__name__)
app.secret_key = 'supersecret'
# connect and store the connection in "mysql" note that you pass the database name to the function
mysql = MySQLConnector(app, 'emaildb')
# an example of running a query

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/update', methods=['POST'])
def update():
    query = "SELECT email FROM emails"                           # define your query
    emails = mysql.query_db(query)
    errors = False
    if len(request.form['email']) < 1:
        errors = True
        flash("e-mail address is empty. Enter e-mail.")
    elif not EMAIL_REGEX.match(request.form['email']):
        errors = True
        flash("Invalid e-mail address. Enter e-mail.")
    elif {'email' : request.form['email']} in emails:
        errors = True
        flash("The e-mail address entered already exists in the database.")
    if errors:
        return redirect('/')
    else:
        session['insert'] = 1
        query = "INSERT INTO emails (email, created_at, updated_at) VALUES (:email, NOW(), NOW())"
        data = {'email': request.form['email']}
        mysql.query_db(query, data)
        return redirect('/success')


@app.route('/success')
def email_list():
    query = "SELECT * FROM emails"                           # define your query
    emails = mysql.query_db(query)                           # run query with query_db()
    return render_template('email_list.html', list_emails=emails, insert = session['insert']) # pass data to our template

@app.route('/remove', methods=['POST'])
def remove():
    session['insert'] = 0
    errors = False
    if len(request.form['email']) < 1:
        errors = True
        flash("e-mail address field is empty. Enter e-mail to remove and re-submit.")
    elif not EMAIL_REGEX.match(request.form['email']):
        errors = True
        flash("Invalid e-mail address. Enter e-mail.")
    else:
        query = "SELECT email FROM emails"                           # define your query
        emails = mysql.query_db(query)
        if not {'email' : request.form['email']} in emails:
            errors = True
            flash("The e-mail address entered was not found in the database.")
    if errors:
        return redirect('/success')
    else:
        query = "DELETE FROM emails WHERE email = :email"
        data = {'email': request.form['email']}
        mysql.query_db(query, data)
        return redirect('/success')

if __name__ == "__main__":
    app.run(debug=True)
