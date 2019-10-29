FROM node:7.10.0

# Install gettext to get envsubst
RUN sed -i '/jessie-updates/d' /etc/apt/sources.list  # Now archived
RUN apt-get update && apt-get install -y gettext

# Install dependencies first to use cache
RUN npm install -g http-server bower

RUN mkdir -p /etc/ssl/certs
COPY lab.cluster.gsi.dit.upm.es.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

WORKDIR /usr/src/app/

ADD bower.json ./
RUN bower link --allow-root
RUN bower install --allow-root && mv bower_components ..

CMD ["/usr/src/app/init.sh"]