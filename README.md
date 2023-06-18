# Bondy Tree Tracker App
Madagascar is the 5️⃣th poorest country globally and faces terrific consequences due to climate change.
With multiple parties promising to provide reforestation services comes the fact that planting trees is simple, but making sure they will grow is more complex. 

For the moment, Bôndy monitors trees physically, but this is not a scalable model. 
Together with the Omdena, a solution to combine satellite and drone imagery, meterological data, and Machine Learning a dashboard was developed to monitor plants.

## File Structure
```
.
├── .dockerignore                         - Files to ignore when building docker image
├── .elasticbeanstalk                     - Elastic Beanstalk configuration files
│   ├── config.yml
│   └── saved_configs
│       └── prod-sc.cfg.yml
├── .env-template                         - Template for .env file
├── .gitignore                            - Files to ignore when pushing to git
├── .platform                             - Elastic Beanstalk configuration files
│   ├── custom.config
│   └── nginx
│       └── conf.d
│           └── proxy.conf
├── Dockerfile                            - Dockerfile for building docker image
├── Makefile                              - Makefile for running commands
├── Pipfile                               - Pipfile for python dependencies
├── Pipfile.lock                          - Pipfile.lock for python dependencies
├── README.md                             - README file
├── data                                  - Data folder
│   ├── drone                             - Drone images
│   │   ├── DJI_0022.JPG
│   │   ├── ...
│   ├── meteor                            - Meteorological data
│   │   ├── ERA5_Land_file.grib
│   │   ├── ERA5_Land_file.grib.idx
│   │   ├── ...
│   ├── model                             - Model files
│   │   ├── Best_Loss.onnx
│   │   ├── ...
│   ├── parcel                            - Parcel data
│   │   └── PlantedParcels.geojson
│   └── planet                            - Planet images
│       ├── Andramasina
│       │   ├── planet_file.tif
│       │   ├── ...
│       ├── Antolojanahary
│       │   ├── planet_file.tif
│       │   ├── ...
│       └── Majunga
│           ├── planet_file.tif
│           ├── ...
├── docker-compose.yml                    - Docker compose file
├── Home.py                               - Home page
├── pages                                 - Pages folder
│   ├── 1_🔮Model_Prediction.py           - Model prediction page
│   ├── 2_🩺Vegetation_Indices.py         - Vegetation indices page
│   ├── 3_🌤️Meterological_Data.py         - Meterological data page
│   ├── 4_📁Upload Drone Image.py         - Upload drone image page
│   └── 5_📒Instructions.py               - Instructions page
├── static                                - Static files folder
│   ├── bondy-logo.png
│   └── madagascar-flag.png
└── util.py                               - Utility functions
```