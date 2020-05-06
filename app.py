import numpy as np
import pandas as pd
import requests
import re
import operator
import os

from flask import Flask, request, render_template, send_from_directory, abort

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
        # Try URL or return message error
        try:
            url = request.form["url"]
            source = requests.get(url).text
        except:
            context['url_help'] = 'Please enter a valid URL'
            return render_template('index.html', **context)

        context['results'] = word_counter(source)
        context['filename'] = 'word_count.csv'

    return render_template('index.html', **context)


@app.route('/<filename>')
def download_csv(filename):
    try:
        return send_from_directory(app.root_path, filename=filename, as_attachment=True)
    except OSError:
        abort(404)


def allowed_tag(tag):
    """
    Checks the tag for unwanted elements such as script tag data
    """
    if isinstance(tag, Comment) or tag.parent.name in [
        'html',
        'style',
        'script',
        'head',
        'title',
        'meta',
        'document',
        '!DOCTYPE'
    ]:
        return False
    else:
        return True


def word_counter(source):
    """
    Counts the words within a url parsed
    """
    soup = BeautifulSoup(source, 'html.parser')
    text = soup.findAll(text=True)
    # Remove unwanted tags and convert to str
    text = ', '.join(list(filter(allowed_tag, text))).lower()
    # Create key, val pairs
    k, v = np.unique(np.array(re.sub(r'[^A-Za-z0-9 \']', '', text).split()), return_counts=True)
    # Build df
    df = pd.DataFrame(data={'count':v}, index=k).sort_values('count', ascending=False)
    df.to_csv('word_count.csv')
    # Build dict
    words = dict(sorted(dict(zip(k, v)).items(), key=operator.itemgetter(1),reverse=True))
    return words
