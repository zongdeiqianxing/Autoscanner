FROM ubuntu:20.04

# RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list \
# && sed -i s/security.ubuntu.com/mirrors.aliyun.com/g /etc/apt/sources.list \
# && apt-get clean \
# && apt update

#ADD sources.list /etc/apt/sources.list
RUN apt update

ENV TZ=Asia/Shanghai
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

RUN apt install -y wget gnupg \
&& wget -q -O - https://dl.google.com/linux/linux_signing_key.pub  | apt-key add - \
&& echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list

RUN apt update

ADD . /root
WORKDIR /root/

RUN ln -sf /usr/share/zoneinfo/$TZ /etc/localtime \
&& echo $TZ > /etc/timezone \
&& apt install -y python3 python3-pip masscan wget whatweb nmap nikto zip tzdata google-chrome-stable \
&& pip3 install IPy simplejson requests bs4 prettytable func_timeout xlrd\
&& pip3 install -r requirements.txt

ENTRYPOINT ["python3","main.py"]
