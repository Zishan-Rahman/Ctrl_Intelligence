from surprise import SVD
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import cross_validate

import pandas as pd

from sklearn.neighbors import NearestNeighbors
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix


from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):

        books = pd.read_csv('data/BX_Books.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
        books.columns = ['ISBN', 'bookTitle', 'bookAuthor', 'yearOfPublication', 'publisher', 'imageUrlS', 'imageUrlM', 'imageUrlL']
        users = pd.read_csv('data/BX-Users.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
        users.columns = ['userID', 'Location', 'Age']
        ratings = pd.read_csv('data/BX-Book-Ratings.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
        ratings.columns = ['userID', 'ISBN', 'bookRating']



