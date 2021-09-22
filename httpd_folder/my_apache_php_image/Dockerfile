FROM php:7.2-apache 
LABEL image-de-base="https://hub.docker.com/_/php"
MAINTAINER My909

RUN a2enmod headers 
RUN a2enmod rewrite 
RUN a2enmod proxy 
RUN a2enmod proxy_http 
RUN docker-php-ext-install pdo pdo_mysql

## Add the wait script to the image
# ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /wait
# RUN chmod +x /wait
# CMD ["/wait"]

RUN service apache2 restart



