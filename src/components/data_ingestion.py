from src.logging.logger import logging
from src.entity.config_entity import  DataIngestionConfig
from src.constant.traning_pipline import DATA_FILE_PATH
from src.entity.artifacts_entity import DataIngestionArtifacts
import sqlite3
import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split

class DataIngestion:
    def __init__(self,data_ingestion_config: DataIngestionConfig):
        self.config= data_ingestion_config
        logging.info(f"Data Ingestion Config: {self.config}")

    def fetch_data_as_dataframe(db_path: str, query: str) -> pd.DataFrame:
      try:
         # Connect to the SQLite database
         connection = sqlite3.connect(db_path)
         
         # Execute the query and read data into a DataFrame
         df = pd.read_sql_query(query, connection)
         
         # Close the connection
         connection.close()
         
         return df
      
      except Exception as e:
         print(e)

    def export_data_to_feature_store(self,df:pd.DataFrame) -> pd.DataFrame:
      try:
         logging.info('Storing raw data to feature store path')

         feature_store_dir_path:str=self.config.data_ingestion_feature_store_dir

         dir_path=os.path.dirname(feature_store_dir_path)
         os.makedirs(dir_path,exist_ok=True)

         df.to_csv(feature_store_dir_path,index=False,header=True)
         logging.info('Storing Raw data completed')
         return df
      
      except Exception as e:
        logging.info(f'Error in export data {str(e)}')
        print(e)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path)
    def split_data_into_train_test(self,df):
      try:
         logging.info('spliting data to train set and test set and validation set')

         test_data,train_data=train_test_split(
            df,test_size=self.config.data_ingestion_train_test_split_ratio,random_state=42
			)
         logging.info('Data split into training and testing sets successfully.')

         # saving train and test data
         train_dir_path=os.path.dirname(self.config.data_ingestion_train_data_store_dir)
         os.makedirs(train_dir_path,exist_ok=True)
         train_data.to_csv(self.config.data_ingestion_train_data_store_dir)

         test_dir_path=os.path.dirname(self.config.data_ingestion_test_data_store_dir)
         os.makedirs(test_dir_path,exist_ok=True)
         test_data.to_csv(self.config.data_ingestion_test_data_store_dir)

         # validation split
         train_data,validation_data=train_test_split(
                train_data,test_size=self.config.data_ingestion_train_validation_split_ratio,random_state=42)

         val_dir_path=os.path.dirname(self.config.data_ingestion_valid_data_store_dir)
         os.makedirs(val_dir_path,exist_ok=True)
         validation_data.to_csv(self.config.data_ingestion_valid_data_store_dir)

         logging.info(f'Training and test data saved to {self.config.data_ingestion_train_data_store_dir} and {self.config.data_ingestion_test_data_store_dir} and {self.config.data_ingestion_valid_data_store_dir} respectively.')
      except Exception as e:
         print(f'Error in spliting data {str(e)}')
    
    def initiate_data_ingestion(self):
      try:
         
         # read data from sqllite3
         # df=self.fetch_data_as_dataframe(DATA_FILE_PATH)
         df=self.read_data(DATA_FILE_PATH)

         self.export_data_to_feature_store(df=df)

         self.split_data_into_train_test(df=df)

         data_ingestion_artifacts=DataIngestionArtifacts(
            train_data_path=self.config.data_ingestion_train_data_store_dir,
            test_data_path=self.config.data_ingestion_test_data_store_dir,
            validation_data_path=self.config.data_ingestion_valid_data_store_dir
			)
         return data_ingestion_artifacts
      
      except Exception as e:
         logging.info(f'Error in Data Ingestion: {str(e)}')
         print(e)