import logging
import os
import pandas as pd
from google.cloud import bigquery


class BigQueryHandler():
    def __init__(self):
        self.project_id = os.getenv('GCP_PROJECT')
        self.dataset_name = 'body_temperature_data'
        self.bq = bigquery.Client()
        self.dataset = self.bq.dataset(self.dataset_name)

    def find_missing_users(self, n_days):
        # get all user id from user table
        df_user = self._get_all_user()
        # get last `n_days` records from temperature table
        df_temp = self._get_last_n_days_temp(n_days)
        # join by user_id
        df = pd.merge(df_user, df_temp, left_on='id', right_on='user_id', how='left')[
            ['name', 'id', 'date', 'temperature']]
        # count data
        missing_users = []
        for id_ in df['id'].unique():
            count = df.query(f'id == "{id_}"')[
                'date'].dropna().unique().size
            name = df.query(f'id == "{id_}"')['name'].unique()[0]
            logging.info(
                f'{name} has {count} unique records in the last {n_days} days.')
            if count == 0:
                missing_users.append({"id": id_, "name": name})

        return missing_users

    def find_fever_users(self, n_days, max_temp):
        q = (
            f'WITH temp AS( '
            f'   SELECT DATETIME(TIMESTAMP(datetime), "Asia/Tokyo") as datetime,date(TIMESTAMP(datetime), "Asia/Tokyo") as date, user_id, temperature FROM `{self.project_id}.{self.dataset_name}.temperature` '
            f'    WHERE DATE(TIMESTAMP(datetime), "Asia/Tokyo") > DATE_SUB(CURRENT_DATE("Asia/Tokyo"), INTERVAL {n_days} DAY) '
            f'    ORDER BY user_id, datetime '
            f'),'
            f'latest AS('
            f'    SELECT MAX(datetime) as datetime, user_id FROM temp GROUP BY user_id, date ORDER BY user_id, date '
            f'),'
            f'joined AS('
            f'    SELECT latest.datetime, temp.user_id, temp.temperature FROM temp INNER JOIN latest ON temp.datetime=latest.datetime AND temp.user_id=latest.user_id '
            f'),'
            f'max_temp AS('
            f'    SELECT user_id, MAX(temperature) as max_temp  FROM joined GROUP BY user_id'
            f')'
            f'SELECT user_id, name, max_temp.max_temp '
            f'FROM max_temp LEFT JOIN `{self.project_id}.{self.dataset_name}.user` ON max_temp.user_id=`{self.project_id}.{self.dataset_name}.user`.id '
            f'WHERE max_temp.max_temp>={max_temp}'
        )
        df = self._query_and_convert_to_df(q)

        # convert to list of dictionary
        users = []
        for k, v in df.to_dict(orient='index').items():
            users.append(v)
        return users

    def _get_all_user(self):
        q = (
            f'SELECT id, name FROM {self.project_id}.{self.dataset_name}.user'
        )
        return self._query_and_convert_to_df(q)

    def _get_last_n_days_temp(self, n_days):
        q = (
            f'SELECT DATE(TIMESTAMP(datetime), "Asia/Tokyo") as date, user_id, temperature '
            f'FROM {self.project_id}.{self.dataset_name}.temperature '
            f'WHERE DATE(TIMESTAMP(datetime), "Asia/Tokyo") > DATE_SUB(CURRENT_DATE("Asia/Tokyo"), INTERVAL {n_days} DAY) '
            f'ORDER BY user_id, date'
        )
        return self._query_and_convert_to_df(q)

    def _query_and_convert_to_df(self, query):
        rows = self.bq.query(query).result()
        df = rows.to_dataframe(self.bq)
        return df
