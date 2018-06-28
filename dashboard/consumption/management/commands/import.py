'''Running this script will import all relevant data in the data directory to
   the sqlite db.'''

import os
import logging
import pandas as pd
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from consumption.models import User_data, Consumption


class Importer(object):

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - '
                            '%(filename)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def import_user_data(self, user_data):
        '''This method imports user data to the user_data table in the
           sqlite db.'''
        try:
            user_data = pd.read_csv(user_data,
                                    encoding='utf-8').to_dict('records')
            user_data_table = [User_data(id=row['id'], area=row['area'],
                                         tariff=row['tariff'])
                               for row in user_data]
            User_data.objects.bulk_create(user_data_table)
            self.logger.info('User data imported')
        except IntegrityError:
            self.logger.info('user_data data already imported,'
                             ' drop all rows in the table to import again.')
        except Exception:
            self.logger.info('Could not import user_data')
        # importing user data

    def import_consumption_data(self, consumption_dir):
        '''This method imports consumption data to the consumption table in the
           sqlite db.'''
        df_list = []
        for file_name in os.listdir(consumption_dir):
            if not file_name.startswith('.'):
                df = pd.read_csv(consumption_dir + file_name,
                                 encoding='utf-8')
                df['user_data_id'] = int(os.path.splitext(file_name)[0])
                # adding id to consumption file before importing
                df.datetime = pd.to_datetime(df.datetime)
                df_list.append(df[['user_data_id', 'datetime',
                                   'consumption']])

        try:
            consumption_data = pd.concat(df_list).to_dict('records')

            consumption_data_table = [
                Consumption(
                    user_data_id=row['user_data_id'],
                    datetime=row['datetime'],
                    consumption=row['consumption'])
                for row in consumption_data]
            Consumption.objects.bulk_create(consumption_data_table)
            self.logger.info('Consumption data imported')
        except IntegrityError:
            self.logger.info('consumption table data already imported,'
                             ' drop all rows in the table import again.')
        except Exception:
            self.logger.info('Could not import consumption_data')
        # importing consumption data


class Command(BaseCommand):

    def handle(self, *args, **options):
        i = Importer()
        i.logger.info("Initiate Import.")
        i.import_user_data(os.path.join(os.path.dirname(__file__),
                                        '../../../../', 'data',
                                        'user_data.csv'))
        i.import_consumption_data(os.path.join(os.path.dirname(__file__),
                                               '../../../../', 'data',
                                               'consumption/'))
        i.logger.info("Import complete.")
