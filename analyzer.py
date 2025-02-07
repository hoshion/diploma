import spacy
import pandas as pd
from transformers import pipeline

nlp = spacy.load('en_core_web_sm')
analyzer = pipeline('sentiment-analysis', model="cardiffnlp/twitter-roberta-base-sentiment-latest")


def get_sentiment(text: str):
    print(len(text))
    vs = analyzer(text[0:1500])
    print(vs)
    return vs[0]['label']
    # if vs > 0.05:
    #     sentiment_label = "positive"
    # elif vs < -0.05:
    #     sentiment_label = "negative"
    # else:
    #     sentiment_label = "neutral"
    # return sentiment_label


if __name__ == '__main__':
    df = pd.read_excel('translated_hromadske.xlsx')
    df['sentiment'] = df['translated'].apply(get_sentiment)

    # df = pd.read_excel('processed_hromadske.xlsx')
    # df['sentiment'] = df['preprocesses_text'].apply(get_sentiment)

    df.to_excel('cardiffnlp.xlsx', index=False)
