from flask import Flask
from flask import render_template, request, flash, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
import mysql.connector

mydb = mysql.connector.connect(host = "localhost", user = "root", password = "", database = "test_sqlconnector_webpage")
mycursor = mydb.cursor()

app = Flask(__name__)
app.secret_key = 'jasonxuanxuan'

def create_tables():
    mycursor.execute("create table if not exists User(Login_ID char(200), password char(200))")
    mycursor.execute("create table if not exists Customer_order (Customer_name char(200), Login_id char(200), num0 integer, num1 integer, num2 integer, num3 integer, num4 integer, total_cost integer)")

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        if request.form['Submit'] == 'Register':
            return redirect(url_for('new_user_register'))
        else:
            query = """select password from User where Login_ID = %s"""
            mycursor.execute(query, (username,))
            # tuple 用法
            for x in mycursor:
                # 必须要嵌套在里面写，因为如果没有这个账号，confirm password没有值，无法进行比较
                confirm_password = x
                password = (password, )
                if confirm_password == password:
                    flash("Successfully log in")
                    return redirect(url_for('main_page', this_id = username))
            flash("Login_ID and password do not match. Please try again")
    return render_template('login_page.html')

@app.route('/register/', methods = ['GET', 'POST'])
def new_user_register():
    if request.method == 'POST':
        new_username = request.form.get("new_username")
        new_password = request.form.get("new_password")
        new_password2 = request.form.get("new_password2")
        if not all([new_username, new_password, new_password2]):
            flash("You have empty fileds")
        elif new_password != new_password2:
            flash("Two passwords are not equal")
        else:
            mycursor.execute("select Login_ID from User where Login_ID = %s", (new_username,))
            for x in mycursor:
                flash("This account is already registered. Please try login")
                return render_template('register.html')
            mycursor.execute("INSERT INTO User (Login_ID, password) values(%s, %s)", (new_username, new_password))
            mydb.commit()
            flash("Successfully create a new account! Please log in")
            return redirect(url_for('index'))
    return render_template('register.html')

def check_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False

@app.route('/mainpage/?<string:this_id>', methods = ['GET', 'POST'])
def main_page(this_id):
    if request.method == 'POST':
        customer_name = request.form.get("name")
        if customer_name == '':
            flash("You should type in your name first")
            return render_template('main_page.html')
        pricelist = [15, 12, 20, 18, 13]
        sum = 0
        num = [None] * 10
        num[0] = request.form.get("num0")
        num[1] = request.form.get("num1")
        num[2] = request.form.get("num2")
        num[3] = request.form.get("num3")
        num[4] = request.form.get("num4")
        for i in range(5):
            if num[i] is '':
                num[i] = '0'
            elif check_int(num[i]) is False:
                flash("You type invalid numbers")
                return render_template('main_page.html')
            else:
                sum = sum + int(num[i]) * pricelist[i]
        if sum == 0:
            flash("You should order at least one food")
            return render_template('main_page.html')
        # 将订单信息写入数据库，并且前进到支付界面
        mycursor.execute("INSERT INTO Customer_order (Customer_name, Login_ID, num0, num1, num2, num3, num4, total_cost) values (%s, %s, %s, %s, %s, %s, %s, %s)", (customer_name, this_id, int(num[0]), int(num[1]), int(num[2]), int(num[3]), int(num[4]), sum))
        mydb.commit()
        return redirect(url_for('finish', total_cost = sum))

    return render_template('main_page.html')

@app.route('/finish/<total_cost>')
def finish(total_cost):
    return render_template('finish.html', total_cost = total_cost)

if __name__ == '__main__':
    create_tables()
    app.run()


