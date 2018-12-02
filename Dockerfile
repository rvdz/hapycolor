FROM debian:stretch

RUN apt update && apt install git python3 python3-pip imagemagick vim -y
RUN pip3 install pipenv

# RUN useradd -m bonisseur-de-la-batte
# RUN su - bonisseur-de-la-batte

ENV hapycolor ~/hapycolor

RUN mkdir -p ${hapycolor}
ADD ./ ${hapycolor}

WORKDIR ${hapycolor}

# Set the locale
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN pipenv install

CMD pipenv run python setup.py test
