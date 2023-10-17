#!/usr/bin/python
"""
Author :    Sulaiman Mukahhal - s.mukahhal@gichd.org
Date   :    2022-12-10
Purpose:    A simple script script to import ACLED events into the IMSMA
            Core for any
            country
Version:    Version 1.0
Org    :   MAC + SESU
"""

import argparse
import logging
import json
import sys
import os
from datetime import datetime, date, timedelta
import requests
import pandas as pd
from arcgis.gis import GIS

from dotenv import load_dotenv

MAX_INCIDENT_PER_QUERY = 500
LOG_DIR = os.path.dirname(os.path.realpath(__file__))
LOGGING_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'


class Configure:
    """The configuration class to read the .env file"""

    def __init__(self, env):
        load_dotenv(env)

        self.acled_api = os.environ.get('ACLED_API')
        self.access_token = os.environ.get('ACLED_ACCESS_TOKEN')
        self.acled_email = os.environ.get('ACLED_EMAIL')
        self.arcgis_user = os.environ.get('ARCGIS_USER')
        self.arcgis_password = os.environ.get('ARCGIS_PASSWORD')
        self.arcgis_portal = os.environ.get('ARCGIS_PORTAL')
        # ARCGIS_FEATURE_LAYER = os.environ.get('ARCGIS_FEATURE_LAYER')
        self.arcgis_item_id = os.environ.get('ARCGIS_ITEM_ID')


# ---------------------------------------------------
def get_args():

    """ Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Loading data from ACLED - select the correct attributes",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-c',
                        '--country',
                        metavar='country',
                        type=str,
                        default='Ukraine',
                        help='Country Events to be imported')

    parser.add_argument('-d',
                        '--days',
                        metavar='days',
                        type=int,
                        help='Number of days to go back'
                        )
    
    parser.add_argument('-r',
                        '--records',
                        metavar='records',
                        type=int,
                        help='''Number of events to retrive, must be more than
                               500 records.'''
                        )

    parser.add_argument('--env',
                        metavar='env',
                        type=str,
                        default='.env',
                        help='''Update in case of changing defaul environment
                              file'''
                        )
    return parser.parse_args()


# ---------------------------------------------------
def get_admin_1(admin1):
    """ This is map the weird gazetteer used by ACLED """
    with open("gazetteer.json", encoding="utf-8") as gaz:
        gazetteer = json.load(gaz)

        if admin1 in gazetteer.keys():
            return gazetteer["admin1_name"][admin1]
    return admin1


# ---------------------------------------------------
def acled_api(config, country, year, start_date,
              end_date, records, page):
    """ Read ACLED data function """

    service_url = "{}?key={}&email={}".format(config.acled_api,
                                              config.access_token,
                                              config.acled_email)
    payload = {
        'terms': 'accept',
        'country': country,
        'year': year,
        'event_date': '{}|{}'.format(start_date, end_date),
        'event_date_where': 'BETWEEN',
        'page': page,
        'limit': MAX_INCIDENT_PER_QUERY
    }

    feature_response = requests.get(service_url, params=payload)

    json_string = feature_response.text
    pydict = json.loads(json_string)

    return pydict


# ---------------------------------------------------
def main():
    """ Main Method that read ACLED data and map it to the correct
     field in the feature serivce. """

    # Setting up the path for the log.
    logging.basicConfig(level=logging.INFO, filename=LOG_DIR+'//'+'logs.txt',
                        filemode='a', datefmt='%Y%m%d %H:%M:%S',
                        format=LOGGING_FORMAT)
    logging.getLogger('googleapiclient.discovery_cache'
                      ).setLevel(logging.ERROR)

    args = get_args()
    country = args.country.capitalize()
    year = args.year
    start_date = args.startDate
    end_date = args.endDate
    records = args.records
    env = args.env

    config = Configure(env)

    if args.days:
        start_date = date.today() - timedelta(days=args.days)
        end_date = date.today()

    # Connection to Portal
    logging.info('\t Program Started')
    logging.info('\t Eastablishing connection to Portal')

    counter_processed = 0
    counter_added = 0
    counter_existing = 0

    # arcgis_pass = base64.b64decode(config.arcgis_password).decode("utf-8")
    arcgis_pass = config.arcgis_password

    try:
        gis = GIS(config.arcgis_portal, config.arcgis_user, arcgis_pass)
    except RuntimeError as error:
        print('ERROR:\tCANNOT CONNECT TO PORTAL', error)
        # Add exc_info = 1 to log full error
        logging.error('ERROR:\t CANNOT CONNECT TO PORTAL: %(error)s')
        sys.exit()
    logging.info('\t Connection to Portal established!')

    # Search for the feature layer by ID
    security_report_item = gis.content.get(config.arcgis_item_id)

    # print(security_report_item)

    # Access the item's feature layers
    security_report_layers = security_report_item.layers
    security_rp_fl = security_report_layers[0]

    flayer_df = pd.DataFrame.spatial.from_layer(security_rp_fl)

    # flayer_df = security_rp_fl.query().df (Depricated)

    # Read inforamtion from ACLED API
    counter_processed = 0
    counter_added = 0
    counter_existing = 0
    # max_pages,
    page = 1

    # if records != None and records >= MAX_INCIDENT_PER_QUERY:
    #     max_pages = int(records/maMAX_INCIDENT_PER_QUERY)
    # else

    while True:
        acled = acled_api(config, country,
                          year, start_date, end_date, records, page)

        if len(acled['data']) > 1:
            logging.info('\t %s incidents in %s (page %s)',
                         len(acled['data']), country, page)
            print(f'''INFO:\t {len(acled['data'])} incidents in {country} ''' +
                  f'''(page {page})''')

            for item in acled['data']:
                counter_processed = counter_processed + 1
                # data_id = int(item['data_id'])
                iso = int(item['iso'])
                event_id_cnty = item['event_id_cnty']
                # event_id_no_cnty = item['event_id_no_cnty']
                event_date = item['event_date']
                year = int(item['year'])
                time_precision = int(item['time_precision'])
                event_type = item['event_type']
                sub_event_type = item['sub_event_type']
                actor1 = item['actor1']
                assoc_actor_1 = item['assoc_actor_1']
                inter1 = int(item['inter1'])
                actor2 = item['actor2']
                assoc_actor_2 = item['assoc_actor_2']
                inter2 = int(item['inter2'])
                interaction = int(item['interaction'])
                country = item['country']
                admin1 = get_admin_1(item['admin1'])
                admin2 = item['admin2']
                admin3 = item['admin3']
                location = item['location']
                latitude = item['latitude']
                longitude = item['longitude']
                geo_precision = int(item['geo_precision'])
                source = item['source']
                notes = item['notes']
                fatalities = item['fatalities']
                civilian_targeting = item['civilian_targeting']
                tags = item['tags']
                disorder_type = item['disorder_type']
                received_time = item['timestamp']
                source_scale = item['source_scale']
                fetchedfrom = '''
                                Armed Conflict Location & Event
                                Data Project (ACLED);
                                acleddata.com'''

                feature_dict = {
                    'attributes': {
                        # 'data_id': data_id,
                        'iso': iso,
                        'event_id_cnty': event_id_cnty,
                        # 'event_id_no_cnty': event_id_no_cnty,
                        'event_date': datetime.strptime(
                                          event_date, '%Y-%m-%d'),
                        'year': year,
                        'time_precision': time_precision,
                        'event_type': event_type,
                        'sub_event_type': sub_event_type,
                        'actor1': actor1,
                        'assoc_actor_1': assoc_actor_1,
                        'inter1': inter1,
                        'actor2': actor2,
                        'assoc_actor_2': assoc_actor_2,
                        'inter2': inter2,
                        'interaction': interaction,
                        'country': country,
                        'admin1': admin1,
                        'admin2': admin2,
                        'admin3': admin3,
                        'location': location,
                        'latitude': latitude,
                        'longitude': longitude,
                        'geo_precision': geo_precision,
                        'source': source,
                        'notes': notes,
                        'disorder_type': disorder_type,
                        'civilian_targeting': civilian_targeting,
                        'tags': tags,
                        'fatalities': int(fatalities),
                        'recevied_time': received_time,
                        'source_deteails': fetchedfrom,
                        'date_fetched': datetime.now(),
                        'source_scale': source_scale,
                        'status': 'external_acled',
                    },
                    'geometry': {
                        'x': float(longitude),
                        'y': float(latitude)
                    }
                }
                if len(flayer_df[flayer_df.event_id_cnty ==
                                 event_id_cnty]) == 1:
                    counter_existing = counter_existing + 1
                else:
                    result = security_rp_fl.edit_features(adds=[feature_dict])
                    if result['addResults'][0]['success']:
                        counter_added = counter_added + 1
                    else:
                        logging.error('Error adding %(event_id_cnty)s:%s',
                                      result)
                        logging.error(feature_dict)
                        print(f'ERROR:\tError {event_id_cnty}: {result}')
            page += 1
            if acled['count'] < MAX_INCIDENT_PER_QUERY:
                break
        else:
            break
    logging.info('For %s in %s:', country, year)
    logging.info('%s processed,%s added and %s already existing',
                 counter_processed, counter_added, counter_existing)
    print(f'INFO:\tFor {country} in {year}:')
    print(f'''INFO:\t{counter_processed} processed, {counter_added} added ''' +
          f'''and {counter_existing} already existing''')

    logging.info('########### END PROCESS IMPORT ###########')


if __name__ == '__main__':
    main()
