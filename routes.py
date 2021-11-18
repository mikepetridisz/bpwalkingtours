from flask import Flask, render_template, request
from flask_mail import Mail, Message
# from config import theemail, thepassword
app = Flask(__name__)

# two decorators, same function
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/news.html')
def news():
    return render_template('news/news.html')

@app.route('/blog.html')
def blog():
    return render_template('blog/blog.html')

@app.route('/about.html')
def about():
    return render_template('about/about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact/contact.html')

# Tours
@app.route('/discover_the_buda_castle.html')
def discover_the_buda_castle():
    return render_template('tours/discover_the_buda_castle.html')

@app.route('/full_day_tour.html')
def full_day_tour():
    return render_template('tours/full_day_tour.html')

@app.route('/budapestforbeginners.html')
def budapestforbeginners():
    return render_template('tours/budapestforbeginners.html')

@app.route('/toursmain.html')
def toursmain():
    return render_template('tours/toursmain.html')

@app.route('/bites_of_budapest.html')
def bites_of_budapest():
    return render_template('tours/bites_of_budapest.html')

@app.route('/budapest_street_food_tour.html')
def budapest_street_food_tour():
    return render_template('tours/budapest_street_food_tour.html')

@app.route('/hungarian_wine_experience.html')
def hungarian_wine_experience():
    return render_template('tours/hungarian_wine_experience.html')

@app.route('/night_tour.html')
def night_tour():
    return render_template('tours/night_tour.html')

@app.route('/street_art_ruin_bar_tour.html')
def street_art_ruin_bar_tour():
    return render_template('tours/street_art_ruin_bar_tour.html')


# Blog Posts
@app.route('/covid-19-budapest-may-2021.html')
def newspost_covid_19_budapest_may_2021():
    return render_template('news/news_posts/covid-19-budapest-may-2021.html')

@app.route('/covid-19-certificates-may-2021.html')
def newspost_covid_19_certificates_may_2021():
    return render_template('news/news_posts/covid-19-certificates-may-2021.html')

if __name__ == '__main__':
    app.run(debug=True,port=9989,use_reloader=False)