import requests
import string
import csv

from flask import Flask, request, render_template, Response

from bs4 import BeautifulSoup
from bs4.element import Comment


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    A simple word counting app with a given URL
    """
    context = {}
    if request.method == 'POST':
        try:
            url = request.form["url"]
            source = requests.get(url).text
            results = word_counter(source)
            context['results'] = results

            # Create CSV
            csv_file = open('word_count.csv', 'w',  newline='')
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['word', 'count'])
            for rec in results:
                csv_writer.writerow([rec, results[rec]])
            csv_file.close
            context['filename'] = csv_file

        except:
            context['url_help'] = 'Please enter a valid URL'

    return render_template('index.html', **context)


@app.route("/<path:filename>", methods=['GET', 'POST'])
def download_csv(filename):
    """
    Download a CSV file of the last word_counter() run
    """
    return Response(
        filename,
        mimetype="text/csv",
        
        )


def tag_allowed(tag):
    """
    Checks the tag for unwanted elements such as script tag data
    """
    if tag.parent.name in ['html', 'style', 'script', 'head', 'title', 'meta', '[document]', '!DOCTYPE']:
        return False
    if isinstance(tag, Comment):
        return False
    return True


def word_counter(url):
    """
    Counts the words within a url parsed
    """
    soup = BeautifulSoup(url, 'html.parser')
    all_words = soup.findAll(text=True)

    word_list = ', '.join(list(filter(tag_allowed, all_words))).split()
    word_count_dict = {}
    for word in word_list:
        # Remove punctions from either end
        if not word.isalnum():
            continue          
        first = 1 if word[0] in string.punctuation else 0
        last = -1 if word[-1] in string.punctuation else None
        word_count_dict[word[first:last].lower()] = word_count_dict.get(word[first:last].lower(), 0) + 1

    # Order Dict
    word_count_dict = {k: v for k, v in sorted(word_count_dict.items(), key=lambda item: item[1], reverse=True)}

    return word_count_dict
