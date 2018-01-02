FROM debian

RUN apt-get update && apt-get install git python3 python3-pip python3-scipy python3-matplotlib imagemagick -y

RUN apt-get install vim -y
RUN useradd -m bonisseur-de-la-batte
RUN su - bonisseur-de-la-batte

ENV hapycolor ~/hapycolor

RUN mkdir -p ${hapycolor}
ADD ./ ${hapycolor}

WORKDIR ${hapycolor}

RUN python3 setup.py install
CMD python3 tests/run_suite.py -v 3
