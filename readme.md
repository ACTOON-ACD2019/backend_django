# django-backend [![Build Status](https://travis-ci.com/ACTOON-ACD2019/backend_django.svg?branch=master)](https://travis-ci.com/ACTOON-ACD2019/backend_django) [![Code Quality](https://api.codacy.com/project/badge/Grade/142bd1ee8c7a4ea08a83696bb1c8d692?isInternal=true)](https://app.codacy.com/manual/k3nuku/backend_django) [![codecov](https://codecov.io/gh/ACTOON-ACD2019/backend_django/branch/master/graph/badge.svg)](https://codecov.io/gh/ACTOON-ACD2019/backend_django)

ACTOON backend implementation using Django REST Framework

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Make sure that you have installed [Python](https://python.org/) >=3.7 and [pip](https://pip.pypa.io/en/stable/installing/) before installation.

-   If you are using [pyenv](https://github.com/pyenv/pyenv) virtualenv, run a commands below to make separated python environment.
``` bash
git clone https://github.com/ACTOON-ACD2019/django-backend
cd django-backend
pyenv install 3.7.4
pyenv virtualenv 3.7.4 actoon-backend
pyenv local actoon-backend
```

### Installing

A step by step series of examples that tell you how to get a development env running

Make a migrations and apply for database to work properly.

``` bash
python ./manage.py makemigrations actoon
python ./manage.py migrate
```

## Deployment

Run the django server on-the-air.

``` bash
python ./manage.py runserver
```

You can serve django with a reverse-proxy setup with nginx, apache, caddy and the others that supports reverse proxy function.

## Built With

-   [Django](https://www.djangoproject.com/) - The Web framework built with Python
-   [Django REST Framework](https://www.django-rest-framework.org/) - REST API Framework for Django (Django Apps)
-   [Travis CI](https://travisci.com/) - Code Integration
-   [Codacy](https://codacy.com) - Code Qualification
-   [Codecov](https://codecov.io) - Code Coverage Measurement 
## Versioning

We use GitHub's tag for versioning. For the versions available, see the [tags on this repository](https://github.com/ACTOON-ACD2019/backend_django/tags). 

## Authors

-   **Dongkyun Yoo** - *Backend, Platform/Infrastructure Engineering* - [sokdak](https://github.com/k3nuku)

See also the list of [contributors](https://github.com/ACTOON-ACD2019/backend_django/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
