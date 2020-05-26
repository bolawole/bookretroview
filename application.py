import os,requests

from flask import Flask, session, render_template,request,flash,redirect,url_for,g,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from forms import SignUpForm,LoginForm
from API_for_books import get_info
from bs4 import BeautifulSoup


app = Flask(__name__)
app.config['SECRET_KEY']='1c59de0f14fddb79'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
#database area

@app.route("/",methods=['GET','POST'])
@app.route("/home",methods=['GET','POST'])
def index():
    data=db.execute("SELECT * FROM users").fetchall()
   
    return render_template("home.html")


@app.before_request
def before_request():
    g.user=None
    if 'user_id' in session:
        data=db.execute("SELECT * FROM users").fetchall()
        for each_user in data:
            if each_user.id==session['user_id']:
                g.user=each_user
                break
        

@app.route("/login",methods=['GET','POST'])
def login():
    session.pop('user_id',None)
    form=LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        data=db.execute("SELECT * FROM users WHERE (username LIKE :username) AND (password LIKE :password)",{"username":username,"password":password,}).fetchone()
        if data==None:
            flash(f'Login invalid! Please check you input a correct username and password','danger')
            return render_template("log-in.html",form=form)
        else:
            session['user_id']=data.id
            flash(f'account login','success')
            return redirect(url_for('profile'))
            
        #takes the user to their account page
    return render_template("log-in.html",form=form)
    
   # data=db.execute("SELECT * FROM users").fetchall()
    #print(data)
    # if a post request was made instead of a GET request
    #if request.method=='POST':
       # username=request.form.get("username")
       # password=request.form.get("password")
       # data=db.execute("SELECT * FROM users WHERE (username LIKE :username) AND (password LIKE :password)",{"username":username,"password":password,}).fetchone()
       # print(data)
       # if data==None:
       #     flash(f'Login invalid! Please check you input a correct password','danger')
       #     return render_template("log-in.html")

       # flash(f'account login','success')
        # takes the user to their account page
        #return redirect(url_for('usersession',name=username))

    #else:
    #    return render_template("log-in.html")
   



@app.route("/Signup",methods=['GET','POST'])
def SignUp():
    form=SignUpForm()
    if form.validate_on_submit():
        password=form.password.data
        username=form.username.data
        email=form.email.data
        #insert the new credential into the database and saves it
        db.execute("INSERT INTO users(username,email,password) VALUES (:username,:email,:password)",{"username":username,"email":email,"password":password})
        db.commit()
        flash(f'Your account has been created You can now Log In','success')
        return redirect(url_for('login'))
    return render_template("sign-up.html",form=form)



    # if a post request was made instead of a GET request
   #if request.method=='POST':
      #  username=request.form.get("name")
       # email=request.form.get("email")
        #password=request.form.get("psw")
        #password_rpt=request.form.get("psw-repeat")
        #if password ==password_rpt:
         #   flash(f'Account Created Please Login','success') #flash used to display message temporarily on the screen
            # insert the new credential into the database and saves it
          #  db.execute("INSERT INTO users(username,email,password) VALUES (:username,:email,:password)",{"username":username,"email":email,"password":password})
           # db.commit()
            #return redirect(url_for('login'))
        #else:
         #   flash('SignUp Unsuccesful! Please check you input a correct password','danger')
          #  data=db.execute("SELECT * FROM users").fetchall()
           # print(data)
    #return render_template("sign-up.html")
    
@app.route("/profile",methods=['GET', 'POST'])
def profile():
    count=0
    logout=True
    
    if g.user==None:
        flash('Page Forbidden Login into your account to view','danger')
        return redirect(url_for('login'))
    if request.method=="POST":
        table=True
        result_search=request.form.get('search')
        data=db.execute(f"SELECT * FROM books WHERE isbn LIKE '%{result_search}%' OR title LIKE '%{result_search.title()}%' OR title LIKE '%{result_search}%' OR author LIKE '%{result_search.title()}%'  OR year LIKE '%{result_search}%'").fetchall()
        for each_data in data:
            count+=1
        if data==None or data==[]:
           
           return render_template("user.html",message="Your Result was not found!",logout=logout) 
        
        return render_template("user.html",datas=data,logout=logout,count=count,table=table)

    return render_template("user.html",logout=logout)#post=session["posts"])

@app.route("/logout")
def logout():
    session.pop('user_id',None)
    return redirect(url_for('index'))

@app.route("/books",methods=['GET', 'POST'])
def books():
    if request.method=='POST':
        isbn=request.form.get("isbn")
        title=request.form.get("title")
        author=request.form.get("author")
        year=request.form.get("year")

        data=db.execute("SELECT * FROM books where isbn LIKE :isbn AND title LIKE :title AND author LIKE :author AND year LIKE :year ",{"isbn":isbn,"title":title,"author":author,"year":year},).fetchone()
        return render_template("review.html",data=data)
   
    return render_template("my-books.html")

#this is the review page of the book site
@app.route("/<string:name>/<string:id>",methods=['GET','POST'])
def review(name,id):
    # to check logout
    logout=True
    data=db.execute(f"SELECT isbn,author,year FROM books WHERE title='{name}'").fetchone()
    isbn=str(data.isbn)
    year=str(data.year)
    author=str(data.author)
    res = requests.get(f"https://www.goodreads.com/book/review_counts.json", params={"key": "S2OhYAU65Hz1yu2sqgnvhQ", "isbns": isbn})
    book_info=get_info(isbn)
    #this section gets the pictures to be displayed for each books from Openlibrary and displays it
    try:
        picture=str(book_info[f"ISBN:{isbn}"]["info_url"])
        p_req=requests.get(f"{picture}").content
        soup=BeautifulSoup(p_req,'html.parser')
        picture="http:"+ (soup.findAll('div', {'class': 'editionCover'})[0].find_all('a')[0]['href'])
        
        
    except KeyError:
        picture="none"
    
    # creating http request to get the book description is available
    try:
        description=str(book_info[f"ISBN:{isbn}"]["info_url"])
        d_req=requests.get(f"{description}").content
        soup=BeautifulSoup(d_req,'html.parser')
        description=soup.find_all("div",{"class":"editionAbout"})[0].find_all('p')[0].text
        
    except KeyError:
        description="none"



    
    good_reads_reviews=res.json()
    reviews_count_goodreads=good_reads_reviews['books'][0]['work_ratings_count']
    reviews_avg_rating_goodreads=float(good_reads_reviews['books'][0]['average_rating'])
    
    
    if g.user==None:
        flash('Login to View this page','danger')
        return redirect(url_for('login'))
    # this code get to run when a user submits a post request on the page
    if request.method=="POST":
        
        
        data=db.execute(f"SELECT book_id,user_id FROM reviews WHERE user_id={g.user[0]} AND book_id={id} ").fetchall()
    
        if not data:
            book_id=int(id)
            user_id=int(g.user[0])
            review=str(request.form.get("review"))
            db.execute(f"INSERT INTO reviews(comments,book_id,user_id) VALUES (:reviews,{book_id},{user_id})",{"reviews":review})
            db.commit()
            data=db.execute(f"SELECT comments, book_id,user_id FROM reviews WHERE user_id={g.user[0]} AND book_id={id} ").fetchall()
            flash("Your review has been included!",'green')
            return redirect(url_for('review',name=name,id=id))
        else:
            data=db.execute(f"SELECT comments, book_id,user_id FROM reviews WHERE user_id={g.user[0]} AND book_id={id} ").fetchall()
        
            flash(f"Seems you have made a Review Before!",'red')
            return render_template("review.html",logout=logout,name=name,isbn=isbn,
            year=year,author=author,
            reviews_count_goodreads=reviews_count_goodreads,
            reviews_avg_rating_goodreads=reviews_avg_rating_goodreads,picture=picture,description=description)

    
    return render_template("review.html",logout=logout,name=name,isbn=isbn,
    year=year,author=author,
    reviews_count_goodreads=reviews_count_goodreads,
    reviews_avg_rating_goodreads=reviews_avg_rating_goodreads,picture=picture,description=description)


@app.route("/bookretroview/api/book/<string:isbn>")
def api_route(isbn):
    book=db.execute("SELECT * FROM books where isbn LIKE :isbn",{"isbn": isbn}).fetchone()
    if not book:
        return jsonify({"error":"No Such book in the system"})
    
    book1=db.execute(f"SELECT comments,title,author,year FROM books JOIN reviews ON reviews.book_id=books.id WHERE isbn='{isbn}'").fetchall()
    # counts the number of reviews
    no_reviews=db.execute(f"SELECT COUNT(comments) from reviews where book_id={book.id}").fetchone()[0]
    
    return jsonify(
        {
            "title":f"{book.title}",
            "author":f"{book.author}",
            "ISBN":f"{book.isbn}",
            "review_count":f"{no_reviews}"


        }
    )
