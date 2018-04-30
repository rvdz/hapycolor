FROM debian

RUN apt update && apt install git python3 python3-pip imagemagick vim -y
RUN pip3 install click==6.7 colormath==3.0.0 decorator==4.3.0 imgur-downloader==0.1.7 networkx==1.11 numpy==1.14.3 Pillow==5.1.0 scipy==1.0.1


# RUN useradd -m bonisseur-de-la-batte
# RUN su - bonisseur-de-la-batte

ENV hapycolor ~/hapycolor

RUN mkdir -p ${hapycolor}
ADD ./ ${hapycolor}

WORKDIR ${hapycolor}

CMD python3 tests/run_suite.py -v 3
