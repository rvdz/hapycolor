FROM debian

RUN apt update && apt install git python3 python3-pip imagemagick vim -y


# RUN useradd -m bonisseur-de-la-batte
# RUN su - bonisseur-de-la-batte

ENV hapycolor ~/hapycolor

RUN mkdir -p ${hapycolor}
ADD ./ ${hapycolor}

WORKDIR ${hapycolor}

RUN pip3 install -r requirements.txt
CMD python3 tests/run_suite.py -v 3
