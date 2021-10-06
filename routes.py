from flask import Flask, render_template, request
from flask_mail import Mail, Message
# from config import theemail, thepassword
app = Flask(__name__)

# two decorators, same function
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/blog.html')
def blog():
    return render_template('blog/blog.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

# Tours

@app.route('/budapestforbeginners.html')
def budapestforbeginners():
    return render_template('tours/budapestforbeginners.html')


# Blog Posts
@app.route('/covid-19-budapest-may-2021.html')
def blogpost_covid_19_budapest_may_2021():
    return render_template('blog/blog_posts/covid-19-budapest-may-2021.html')

@app.route('/covid-19-certificates-may-2021.html')
def blogpost_covid_19_certificates_may_2021():
    return render_template('blog/blog_posts/covid-19-certificates-may-2021.html')

if __name__ == '__main__':
    app.run(debug=True,port=9989,use_reloader=False)