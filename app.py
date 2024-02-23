from flask import *

# start
app = Flask(__name__)
app.secret_key = "fmgk,hiyoh.ohkjjljl;k;'j;j;j'jlh;hhkn"

@app.route('/')
def home():
    import pymysql
    connection = pymysql.connect(host='localhost', user='root', password='', database='mbuni_flask_db')

    # create the cursor: Excecute SQL Queries
    cursor = connection.cursor()

    # Electronics
    sql = "select * from products where product_category = 'Electronics'"
    cursor.execute(sql)
    data = cursor.fetchall()

    # Fashion
    sql_fashion = "select * from products where product_category = 'Fashion'"
    cursor.execute(sql_fashion)
    data_fashion = cursor.fetchall()
    
    # end home
    return render_template('home.html', electronics = data, fashion = data_fashion)


@app.route('/upload', methods = ['POST', 'GET'])
def upload():
    if request.method == 'POST':
        product_name = request.form["product_name"]
        product_desc = request.form["product_desc"]
        product_cost = request.form["product_cost"]
        product_category = request.form["product_category"]
        product_image_name = request.files["product_image_name"]

        # step1: save image file to static/images/
        product_image_name.save('static/images/' + product_image_name.filename)

        # connect to the databse -> mbuni_flask_db
        import pymysql
        connection = pymysql.connect(host='localhost', user='root', password='', database='mbuni_flask_db')

        # create cursor(): execute sql
        cursor = connection.cursor()
        data = (product_name, product_desc, product_cost, product_category, product_image_name.filename)

        # sql to insert data to products
        sql = "insert into products (product_name, product_desc, product_cost, product_category, product_image_name) values (%s, %s, %s, %s, %s)"

        # use cursor to execute sql, then pass data
        cursor.execute(sql, data)
        connection.commit()
        return render_template('upload.html', message = 'Uploaded Successfully')
    
    else:
        return render_template('upload.html', message = 'Please Add Product Here' )


@app.route('/single/<product_id>')
def single(product_id):
    # Step1: Database connection
    import pymysql
    connection = pymysql.connect(host='localhost', user='root', password='', database='mbuni_flask_db')

    # Step2: Create cursor()
    cursor = connection.cursor()

    # Step3: SQL Query -> product_id from the URL
    sql = "select * from products where product_id = %s"
    cursor.execute(sql, product_id)
    data = cursor.fetchone()
    return render_template('single.html', single= data)


@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        phone = request.form["phone"]
        email = request.form["email"]
        user_image_name = request.files["user_image_name"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        # Step: 1: Save image static/users/
        user_image_name.save('static/users/' + user_image_name.filename)

        # Step2: Database Connection
        import pymysql
        connection = pymysql.connect(host='localhost', user='root', password='', database='mbuni_flask_db')

        # Step3: cursor()
        cursor = connection.cursor()
        data = (username, phone, email, user_image_name.filename, password)
        sql = "insert into users (username, phone, email,user_image_name, password ) values (%s, %s, %s, %s, %s)"

        # Step4: Excecute SQL
        # Condition: password and confirm
        if password != confirm:
            return render_template('register.html', warning = 'Password Dont Match')
        
        elif len(password) < 8:
            return render_template('register.html', warning = 'Password is Less than 8 characters')
        
        else:
            cursor.execute(sql, data)
            connection.commit()

            from sms import send_sms
            send_sms(phone, f"Thank you {username}, Karibu Sana!")

            return render_template('register.html', success = 'Registered Successfully')
        
    else:
        return render_template('register.html', message = 'Please Add Your Information' )


@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        import pymysql
        connection = pymysql.connect(host='localhost', user='root', password='', database='mbuni_flask_db')

        data = (username,password)
        sql = "select * from users where username = %s and password = %s"
        cursor = connection.cursor()
        cursor.execute(sql, data)
        # cursor.rowcount = returns the number of records
        if cursor.rowcount == 0:
            return render_template('login.html', warning = 'Invalid Credentials')
        else:
            user = cursor.fetchone()
            print(user)
            session["key"] = user[1]
            session["phone"] = user[2]
            session["image"] = user[4]
            return redirect('/')
        
    else:
        return render_template('login.html', message = 'Login Here')


@app.route('/logout')
def logout():
    if "key" in session:
        session.clear()
        return redirect('/login')

@app.route('/mpesa', methods = ['POST'])
def mpesa():
    phone = request.form["phone"]
    amount = request.form["amount"]

    from mpesa import stk_push
    stk_push(phone, amount)
    return "Please Check Your Phone to Complete Payment...."

app.run(debug=True)
# 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
# end