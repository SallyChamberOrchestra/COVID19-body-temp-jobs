import os


class BigQueryHandler():
    def __init__(self):
        self.project_id = os.getenv('GCP_PROJECT')
        self.dataset_name = 'body_temperature_data'
        self.bq = bigquery.Client()
        self.dataset = self.bq.dataset(self.dataset_name)

    def find_missing_users(self, n_days):
        # get all user id from user table
        df_user = self._get_all_user_ids()
        # get last `n_days` records from temperature table
        df_temp = self._get_last_n_days_temp(n_days)

    def _get_all_user(self):
        q = (
            f'SELECT id, name FROM {self.project_id}.{self.dataset_name}.user'
        )
        return self._query_and_convert_to_df(q)

    def _get_last_n_days_temp(self):
        q = (
            f'SELECT datetime, user_id, temperature FROM {self.project_id}.{self.dataset_name}.temperature'
            f'WHERE DATE(TIMESTAMP(datetime), "Asia/Tokyo") > DATE_SUB(CURRENT_DATE("Asia/Tokyo"), INTERVAL 3 DAY)'
        )
        return self._query_and_convert_to_df(q)
        # WITH name_table AS(SELECT name, id FROM covid19-284209.body_temperature_data.user)
        # SELECT datetime, name_table.name, temperature.temperature, name_table.id FROM covid19-284209.body_temperature_data.temperature INNER JOIN name_table ON temperature.user_id=name_table.id

    def _query_and_convert_to_df(self, query):
        rows = self.bq.query(query).result()
        df = rows.to_dataframe(self.bq)
        return df
