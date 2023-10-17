# Importing ACLED data to IMSMA Core

 This python script illustrates how to migrate data from a third-party source to the IMSMA Core using the [ArcGIS API for Python](https://developers.arcgis.com/python/). The IMSMA Core is built around the pEsri Enterprise](https://www.esri.com/en-us/arcgis/products/arcgis-enterprise/overview), which communicates among its components via the [ArcGIS Rest API](https://developers.arcgis.com/rest/). That will be used to demonstrate how to read data from an API, format the data, and then append the data. We're going to use the [Armed Conflict Location and Event Data Project (ACLED)](https://acleddata.com) data API for this example. In addition, if you want to replicate the system in your environment, I've included the Survey123 template that was used.

The steps below will assist you in preparing your system and installing the code. We'll use Ukraine as an example, but you can choose from other countries covered by ACLED based on your needs.

## Instlllation 
If you don't have Python installed, go to the [python.org](https://www.python.org) and install it from there. Once that completed copy the ACLED reporistory to your local or server machine. The script should work with python version 3.7+

### Download the repository.
Make sure you've already git installed. Then you can run the following commands to get the scripts on your computer:

OS X, Linux and Windows:

 ```
 git clone https://github.com/smukahhal/ACLED_to_IMSMA.git"
 cd ACLED_to_IMSMA
 ```
This will have the system installed. 

### Import all libraries
To run the script, you will need to install important python librieris. You can use the `requirements.txt` to install them using `pip`.

```pip install -r requirement.txt```

Check that you have the most recent library for `arcgis` is imported. Be aware that when you install arcgis from Esri ArcGIS, it comes with over 100 libraries, many of them we will not use in this script.


### Prepare your Enterprise Server.
Now, using [ArcGIS Survey123 Connect](https://survey123.arcgis.com/), create a feature layer. Import the XLSForm `ACLED Incidents Form.xlsx` from the recently cloned `ACLED` folder. This will generate a feature layer that corresponds to the data imported from ACLED. To create the ACLED features layer, publish the new form.

Once the feature layer published, copy the ID of the features layer as will use in our script. 

Make a new `.env` environment file that will contain information about ACLED and the features layer. The document must be formatted and contain all of the following information:

```
ACLED_API = "https://api.acleddata.com/acled/read/"
ACLED_ACCESS_TOKEN = "Get that form ACLED Portal Administrator"
ACLED_EMAIL = "The email used to register in ACLED"
ARCGIS_USER = "The publisher that was used in Survey123 Connect"
ARCGIS_PASSWORD = "The password for the IMSMA Core"
ARCGIS_PORTAL = :The portal domain name with the http and the portal"
ARCGIS_FEATURE_LAYER = 'The Feature layer name'
ARCGIS_ITEM_ID = 'The id of the feature layer for ACLED in portal'
```

Save the ``.env`` file and place it in the same directory as the environment variables file for the main script. This file is required before running the script.

## Usage
To run the code, for example we can use the following command to import the last 10 days of incidents that occurred in Ukraine from ACLED Data to IMSMA:

 ```python get_acled_data.py -c Ukraine -d 10```

You can also run to get the help 
```python get_acled_data.py -h```
This will result in this:
```console
usage: get_acled_data.py [-h] [-c country] [-d days] [--env env]

Loading data from ACLED - select the correct attributes

options:
  -h, --help            show this help message and exit
  -c country, --country country
                        Country Events to be imported (default: Ukraine)
  -d days, --days days  Number of days to go back (default: None)
  -r records, --records records
                        Number of events to retrive, must be more than 500 records. (default: None)
  --env env             Update in case of changing defaul environment file (default: .env)
  ```

## Definiations: 

`ACLED_EMAIL`
: Character string as the Type. Enter the email address you used to sign up for ACLED access. We can also set the email address as an environment variable with `Sys.setenv(EMAIL_ADDRESS="your_email_address")`, in which case you can skip this argument. The following usage examples demonstrate these two approaches.

`ACLED_ACCESS_TOKEN`
: Character string as the Type. Supply your ACLED access key. The access key can also be set as an environment variable using Sys.setenv(ACCESS_KEY="your_access_key"), in which case we can skip this argument.

`country`
: Character string as the Type. Provide country names to narrow down which events should be retrieved. See the details below for more information on how the arguments "country" and "region" interact.

`days`
: Integer as the Type. Provide an integer to retrieve all incidents that occurred in the last number of days. 

## Administrative Structure 

When working with data, one of the first challenges is mapping the data to the appropriate administrative structure. This is because of two factors: The first consideration is the spelling of the names, particularly if they were translated from another language. The second reason is that the administrative structure is constantly changing, making it difficult to keep up. To address this issue, we are utilising a JSON file named 'gazetteer.json' to assist us in mapping the ACLED admin structure to the national programme admin structure. For example, in Ukraine, the spelling differed from the official names, and ACLED does not use P-Codes, which are used as a reference in many humanitarian programmes for sharing data between different bodies.

 ```
 {
    "admin1_name":
         {
            "Kyiv City": "Kyiv",
            "Dnipropetrovsk": "Dnipropetrovska",
            ...
         }
     "admin1_code":
         {
            "Kyiv City": "UA80",
            "Dnipropetrovsk": "UA12",
            ...
         }
 }
 ```

# References

* [GICHD - Information Management](https://www.gichd.org/our-response/information-management/)
* [Armed Conflict Location & Event Data Project (ACLED)](https://acleddata.com/)
* [ArcGIS API For Pythong - Feature Layer properties](https://developers.arcgis.com/python/guide/updating-feature-layer-properties/)


# A word of advice
Using this code for a long duration period may result in a large number of incidents and may affect your access to ACLED data. In other words use wisely.
