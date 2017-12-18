FROM debian

RUN apt-get update && apt-get install git python3 python3-pip python3-scipy python3-matplotlib imagemagick -y

ENV hapycolor /hapycolor/

RUN mkdir hapycolor
ADD ./ ${hapycolor}

WORKDIR ${hapycolor}

RUN python3 setup.py develop
CMD python3 tests/run_suite.py -v 3
