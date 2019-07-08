Precision Chemotherapy Recommender
==================================

Description
-----------
This repo contains code used for the Precision Chemotherapy Recommender (link_), which is available as a Dash_ app deployed on Heroku_. It is also known as MeCan (Me: precision, Can: no cancer)!

The code for training and building the models used for this app is available at: https://github.com/syao13/insight_project.

Usage
-----
Upload a patient's gene expression file and it will output the most sensitive chemo drugs for this patient and the most important genes associated with each drug.

You can also run the app locally,

.. code:: bash

   python3 app.py



.. _link: https://mecan.herokuapp.com/
.. _Dash: https://plot.ly/products/dash/
.. _Heroku: https://www.heroku.com/
