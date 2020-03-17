# ZDNS-Flask
### A simple implementation for using Zdns on Web browsers

Install Dependencies:
```bash
sudo apt-get update
sudo apt install zmap wget git build-essential python3.7 python3-setuptools python3-pip
sudo pip3 install Flask jinja2 demjson
```

Install Go (if you haven't got one):
```bash
wget https://storage.googleapis.com/golang/go1.10.4.linux-amd64.tar.gz
tar -C /usr/local -xzf go1.10.4.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
export GOPATH=/usr/local/go/bin/
```
Install ZDNS (if you haven't got one):
```bash
go get github.com/zmap/zdns/zdns
cd /usr/local/go/bin/src/github.com/zmap/zdns/zdns
go build
```
Run:
```bash
python3 zdnsflask.py
```
