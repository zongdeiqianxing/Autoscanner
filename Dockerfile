FROM ubuntu:20.04


ENV TZ=Asia/Shanghai
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list \
&& sed -i s/security.ubuntu.com/mirrors.aliyun.com/g /etc/apt/sources.list \
&& apt-get clean \
&& apt update \
&& apt install -y wget gnupg zip\
&& wget -q -O - https://dl.google.com/linux/linux_signing_key.pub  | apt-key add - \
&& echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
&& wget http://npm.taobao.org/mirrors/chromedriver/70.0.3538.16/chromedriver_linux64.zip -O /tmp/chrome.zip \
&& unzip -d /opt /tmp/chrome.zip \
&& ln -fs /opt/chromedriver /usr/local/bin/chromedriver \
&& apt update

ADD . /root
WORKDIR /root/
COPY config/SIMSUN.TTC /usr/share/fonts/ttf-dejavu/SIMSUN.TTC

RUN ln -sf /usr/share/zoneinfo/$TZ /etc/localtime \
&& echo $TZ > /etc/timezone \
&& apt install -y wget python3 python3-pip masscan whatweb nmap nikto tzdata dnsutils google-chrome-stable \
&& pip3 install -r requirements.txt

ENTRYPOINT ["python3","main.py"]
