import sys
import pandas as pd 
import numpy as np 
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    """
    Function: to load the messages and categories files into two data sets, then merge the messages and categories datasets using the common id.
    
    Input: 
    messages_filepath: message file path
    categories_filepath: category file path
    
    Output: df (pandas dataframe): merged data
    """
    # load dataset "message" 
    messages = pd.read_csv(messages_filepath)
    messages.head()
    
    # load dataset "categories"
    categories = pd.read_csv(categories_filepath)
    categories.head()

    # merge dataset on "ID"
    df = messages.merge(categories, how="outer", on='id')
    df.head()
    
    return df
    

def clean_data(df):
    """
    Function: clean the merged dataset
    
    Input: df (pandas dataframe): source dataset
    
    Output: df (pandas dataframe): cleaned dataset 
    """
    # create a dataframe of the 36 individual category columns
    categories = df['categories'].str.split(';', expand=True)
    categories.head()

    # select the first row of the categories dataframe
    row = categories.head(1)

    # use this row to extract a list of new column names for categories.
    # one way is to apply a lambda function that takes everything 
    # up to the second to last character of each string with slicing
    category_colnames = row.applymap(lambda x: x[:-2]).iloc[0,:]
    
    
    # rename the columns of `categories`
    categories.columns = category_colnames
   
    
    # convert category values to 0 / 1 numerics
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].astype(str).str[-1]
    
        # convert column from string to numeric
        categories[column] = categories[column].astype(int) 
      
    categories = categories[categories["related"] < 2]
    # drop the original categories column from `df`
    df = df.drop(['categories'],axis = 1)
    
    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df,categories], axis = 1 )
   
    # drop duplicates
    df_nodup = df.drop_duplicates()
  
    return df_nodup
    

def save_data(df, database_filename):
    """
    Function: save the clean dataset into a sqlite database
    Input: 
        df (pandas dataframe): dataframe to save
        database_filename (string): destination sqlite database location
    Output:
        NA
    """
    engine = create_engine("sqlite:///{}".format(database_filename))
    df.to_sql("DisaterResponses", engine, index=False, if_exists="replace")


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
