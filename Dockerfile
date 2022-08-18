FROM ubuntu:20.04


ENV TZ=Asia/Shanghai
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# curl -fsSL https://dl.google.com/linux/linux_signing_key.pub  | apt-key add - \
# 如果chrome安装后执行失败，更换chromedrive版本，操作就是将下面url的版本更换为最新版本
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
&& wget https://golang.google.cn/dl/go1.17.linux-amd64.tar.gz \
&& tar -xvf go1.17.linux-amd64.tar.gz -C /usr/local/ \
&& apt update


ENV GOROOT="/usr/local/go"
ENV PATH="${PATH}:${GOROOT}/bin"
ENV PATH="${PATH}:${GOPATH}/bin"
ENV GOPATH=$HOME/go
ENV PATH="${PATH}:${GOROOT}/bin:${GOPATH}/bin"


ADD . /root
WORKDIR /root/
COPY config/SIMSUN.TTC /usr/share/fonts/ttf-dejavu/SIMSUN.TTC


RUN go env -w GOPROXY=https://goproxy.cn,direct \
&& GO111MODULE=on go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest

RUN ln -sf /usr/share/zoneinfo/$TZ /etc/localtime \
&& echo $TZ > /etc/timezone \
&& apt install -y curl wget python3 python3-pip masscan whatweb nmap tzdata dnsutils google-chrome-stable \
&& pip3 install -r requirements.txt

ENTRYPOINT ["python3","main.py"]
