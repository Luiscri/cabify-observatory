FROM python:3.6

# Install gettext to get envsubst
RUN sed -i '/jessie-updates/d' /etc/apt/sources.list  # Now archived
RUN apt-get update && apt-get install -y gettext \
	nano \
	netcat

ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /usr/src/app/

COPY requirements.txt ./
RUN pip3 install --user -r requirements.txt

COPY cfg/ /etc/luigi/
COPY wait-for-it.sh ./
RUN chmod +x ./wait-for-it.sh
COPY my_sched.py ./
COPY tasks.py ./
COPY scrapper/ ./scrapper/

CMD ./wait-for-it.sh $ES_NETWORK_LOCATION -t 0 -- ./wait-for-it.sh $SENPY_NETWORK_LOCATION -t 0 -- python my_sched.py