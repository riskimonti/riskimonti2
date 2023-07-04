# skripsi-mukti

Skripsi Mukti is a web application that can be used to manage the data of theses and dissertations in the Faculty of Engineering, Universitas Nusantara PGRI Kediri. This application is built using the Django framework and MySQL database. This application is also equipped with a REST API that can be used to access the data in the application. This aplication for my final project in Universitas Nusantara PGRI Kediri.

## Installation

1. Clone this repository

    ```bash
    git clone https://github.com/ikimukti/skripsi-mukti.git
    ```

2. Install Python Latest Version in Windows, Linux, or Mac

    ```bash
    # Windows
    https://www.python.org/downloads/windows/
    Click Download Python Latest Version
    When the download is complete, run the installer and follow the steps to install Python on your computer.
    Add Python to Path: Check the box next to Add Python X.X to PATH. Then click Install Now.
    Limit the path length: Check the box next to Disable path length limit. Then click Install Now.
    ```

    ```bash
    # Linux
    sudo apt-get update
    sudo apt-get install python
    sudo apt-get install python3-pip
    sudo apt-get install python3-venv
    ```

    ```bash
    # Mac
    https://www.python.org/downloads/mac-osx/
    Click Download Python Latest Version
    When the download is complete, run the installer and follow the steps to install Python on your computer.
    Add Python to Path: Check the box next to Add Python X.X to PATH. Then click Install Now.
    Limit the path length: Check the box next to Disable path length limit. Then click Install Now.
    ```

3. Install Node.js

    ```bash
    # Windows
    https://nodejs.org/en/download/
    Click Download Node.js Latest Version
    When the download is complete, run the installer and follow the steps to install Node.js on your computer.
    ```

    ```bash
    # Linux
    sudo apt-get update
    sudo apt-get install nodejs
    sudo apt-get install npm
    ```

    ```bash
    # Mac
    https://nodejs.org/en/download/
    Click Download Node.js Latest Version
    When the download is complete, run the installer and follow the steps to install Node.js on your computer.
    ```

4. Install XAMPP and start the Apache and MySQL

    ```bash
    # Windows
    https://www.apachefriends.org/download.html
    Click Download XAMPP Latest Version
    When the download is complete, run the installer and follow the steps to install XAMPP on your computer.
    Start the Apache and MySQL
    ```

    ```bash
    # Linux
    sudo apt-get update
    sudo apt-get install xampp
    sudo /opt/lampp/lampp start
    ```

    ```bash
    # Mac
    https://www.apachefriends.org/download.html
    Click Download XAMPP Latest Version
    When the download is complete, run the installer and follow the steps to install XAMPP on your computer.
    Start the Apache and MySQL
    ```

5. Environment Setup

    ```bash
    cd skripsi-mukti
    python3 -m venv env
    source venv/bin/activate # Linux or Mac 
    env\Scripts\activate # Windows
    pip install -r requirements.txt
    ```

6. Install connector MySQL for Python

    ```bash
    # Windows
    pip install mysql-connector-python
    Download Connector MySQL for Python: https://dev.mysql.com/downloads/connector/python/
    When the download is complete, run the installer and follow the steps to install Connector MySQL for Python on your computer.
    ```

    ```bash
    # Linux
    pip install mysql-connector-python
    ```

    ```bash
    # Mac
    pip install mysql-connector-python
    ```

7. Create database in MySQL and migrate

    ```bash
    # Windows
    Open XAMPP Control Panel
    Start the Apache and MySQL
    Open the browser and go to http://localhost/phpmyadmin/
    Create database with name finalprojectdb
    python manage.py migrate
    ```

    ```bash
    # Linux
    sudo /opt/lampp/lampp start
    Open the browser and go to http://localhost/phpmyadmin/
    Create database with name finalprojectdb
    python manage.py migrate
    ```

    ```bash
    # Mac
    Open XAMPP Control Panel
    Start the Apache and MySQL
    Open the browser and go to http://localhost/phpmyadmin/
    Create database with name finalprojectdb
    python manage.py migrate
    ```

8. Configure Tailwind CSS Django

    ```bash
    # Create a Tailwind CSS compatible Django app
    python manage.py tailwind init
    # Install Tailwind CSS dependencies
    python manage.py tailwind install
    # Start the development server by running tailwind
    python manage.py tailwind start
    ```

9. Create superuser

    ```bash
    python manage.py createsuperuser
    # Enter your username, email, and password
    Username (leave blank to use 'smkn1kediri'): admin
    Email address: admin@ikimukti.com
    Password: 
    Password (again): 
    Superuser created successfully.
    ```

10. Run the development server

    ```bash
    python manage.py runserver
    ```
