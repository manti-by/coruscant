Apollo App
==========================================================

Paspberry Pi App


Installation:
----------------------------------------------------------

1. Install system libraries:

        $ sudo apt-get install -y python-dev mysql-server libmysqlclient-dev python-smbus libjpeg-dev
    
2. Install and create virtualenv on RPI:

        $ sudo apt-get install -y python-virtualenv
        $ mkdir /home/pi/venv && cd /home/pi/venv
        $ virtualenv --no-site-packages worker 
    
3. Install server application and worker requirements:

        $ source /home/pi/venv/worker/bin/activate
        $ pip install -r /home/pi/apollo/worker/requirements.txt
        
4. Install notifier GTK+ library:

        $ sudo add-apt-repository ppa:gnome3-team/gnome3
        $ sudo add-apt-repository ppa:gnome3-team/gnome3-staging
        $ sudo add-apt-repository ppa:ubuntuhandbook1/corebird
        
        $ sudo apt-get update
        $ sudo apt-get install corebird
        $ sudo add-apt-repository -r ppa:gnome3-team/gnome3-staging
    
5. Run server application:

        $ python /home/pi/apollo/worker/app.py
        
6. Add worker crontab for root!:

        $ sudo crontab -e
        > 1/60 * * * *    /home/pi/venv/worker/bin/python /home/pi/apollo/worker/worker.py
        
7. Run notifier:

        $ python /home/pi/apollo/application/app.py
    