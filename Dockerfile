FROM python:3.9-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

RUN python -m spacy download xx_ent_wiki_sm

RUN python -m spacy download en_core_web_md

RUN python -m spacy download de_core_news_md

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]