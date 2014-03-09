tornado-bootstrap
=================

A framework for bootstrapping RESTful API's using Tornado 3.2 with Python 3.3.2.


Installation
------------

```
sudo apt-get install python3.3
sudo apt-get install pip3
sudo apt-get install libyaml-dev

sudo pip3 install virtualenv
sudo pip3 install paver
```

Quick Start
-----------

```
cd tornado-bootstrap
paver create_virtualenv
source bin/activate
rest_api -d ops/config.yaml
```

Finally, visit http://localhost:3000/v1/docs/index.html to see the current documentation for your project.

#####Acknowledgements
*I would like to credit Anthony Tarola and Kaleb Pomeroy for*
*help with the initial code and design of this project.*
