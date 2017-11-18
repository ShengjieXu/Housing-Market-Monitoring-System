# Housing-Market-Monitoring-System

## Overview

This system monitors the housing market in real time and provides visualizations on analytical statistics in a scalable and evolvable way 🤖

## [Design Document](./Documents/Design%20Document.md)

## Quick Start

### Web Servers

* Node.js [install Node 8 LTS from nodesource](https://github.com/nodesource/distributions)

    ```sh
    sudo apt-get update
    curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
    sudo apt-get install -y nodejs build-essential
    ```

* Nodemon

    ```sh
    sudo npm install -g nodemon
    ```

* Express Generator

    ```sh
    sudo npm install -g express-generator
    ```

* Angular/Cli

    ```sh
    sudo npm install -g @angular/cli
    ```

## Backend Servers

* Redis

    ```sh
    wget http://download.redis.io/releases/redis-4.0.2.tar.gz
    tar xzf redis-4.0.2.tar.gz
    cd redis-4.0.2
    make
    cd utils
    sudo ./install_server.sh
    ```

* Pip

    ```sh
    sudo apt install -y python-pip
    ```

## Deployment

* Docker (ask [explainshell](https://explainshell.com/) about the commands)

    ```sh
    curl -fsSL https://get.docker.com/ | sh
    sudo usermod -aG docker $(whoami)
    sudo systemctl enable docker
    ```

* Nginx (detailed instructions available in [Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-16-04))

    ```sh
    sudo apt-get update
    sudo apt-get install nginx
    ```

  * Enable the most restrictive firewall profile that will still allow the traffic you've configured, `e.g. HTTP`:

    ```sh
    sudo ufw app list
    sudo ufw allow 'Nginx HTTP'
    ```