import spacy
import pandas as pd
from textblob import TextBlob
from deep_translator import GoogleTranslator
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

nlp = spacy.load('uk_core_news_sm')
analyzer = pipeline('sentiment-analysis')

def preprocess(text: str):
    doc = nlp(text)
    filtered_tokens = [token.lemma_ for token in doc if not token.is_stop and token.text.isalpha()]
    uk_text = ' '.join(filtered_tokens)[0:3000]
    en_text = GoogleTranslator(source='auto', target='en').translate(uk_text)
    return en_text


def get_sentiment(text: str):
    print(len(text))
    vs = analyzer(text[0:2560])
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
    df = pd.read_excel('hromadske.xlsx')
    df['preprocesses_text'] = df['text'].apply(preprocess)
    df['sentiment'] = df['preprocesses_text'].apply(get_sentiment)

    # df = pd.read_excel('processed_hromadske.xlsx')
    # df['sentiment'] = df['preprocesses_text'].apply(get_sentiment)

    df.to_excel('processed_hromadske.xlsx', index=False)
