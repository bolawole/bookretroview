import requests,os,json
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



def get_info(isbn):
    r=requests.get(f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json").text
    y=json.loads(f'{r}')
    return y

