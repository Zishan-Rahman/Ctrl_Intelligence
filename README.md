# Ctrl Intelligence

Ctrl Intelligence, the major group project for SEG.

## Bookwise

Link to deployed version: https://whispering-bastion-83257.herokuapp.com/

Link to deployed version (administrators): https://whispering-bastion-83257.herokuapp.com/admin/

Use the following details:
- Email: ctrl@intelligence.com
- Password: Password123

## Project Structure

The main project is called `system` and it consists of two key applications, `bookclub` being the social-network side of Bookwise and `recommender` dealing with the dataset preprocessing.

## Team Members

- Fathima (JD) Jamal-Deen (K1922032)
- Emma Conteh (K20045772)
- Surma Begum (K19025208)
- Zishan Rahman (K20071291)
- Raisa Ahmed (K20056465)
- Zakariya Ahmed Mohamed (K20008985)
- Lorenzo Bonara (K20068878)
- Yiğit Cengiz (K20077068)
- Suhayb Yones (K20044202)
- Brendon Zoto (K19011443)

## Installation Instructions

We recommend you use Python 3.8 to run Bookwise due to a dependency (psycopg2) that fails to install in later versions of Python.

First, set up a Python virtual environment from the root of this project:

```bash
$ virtualenv venv
$ source venv/bin/activate
```

Then install all the required libraries needed to run Bookwise in your virtual environment:

```bash
(venv) $ pip3 install -r requirements.txt
```

Set up the recommender system pickle files:

```bash
(venv) $ python3 manage.py recommender
```

Migrate your database, then seed it to get all the data:

```bash
(venv) $ python3 manage.py makemigrations
(venv) $ python3 manage.py migrate
(venv) $ python3 manage.py seed
```

Finally, run the local server:

```bash
(venv) $ python3 manage.py runserver
```

To run the automated test suite:

```bash
(venv) $ python3 manage.py test
```

To see the results of the machine-learning models evaluator:

```bash
(venv) $ python3 manage.py evaluator
```

## Sources used

- https://www.youtube.com/watch?v=Rbkc-0rqSw8 (For email verification)
- Chess club project (KCL 5CCSSEG Semester 1)
- https://www.kaggle.com (For the recommender system)
- https://legionscript.medium.com/building-a-social-media-app-with-django-and-python-part-14-direct-messages-pt-1-1a6b8bd9fc40 (For private messaging)
- https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js (For the inbuilt search bars)
- https://getbootstrap.com/ (For icons, pagination, forms)
- http://www.inkscape.org/ (For editing images)
- https://www.pixabay.com/ (For the background image)
- https://drafts.csswg.org/css-animations-1/ (For css animations)
