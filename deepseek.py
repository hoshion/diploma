import pandas as pd


def get_sentiment(text: str):
    if 'NEUTRAL' in text:
        return 'NEUTRAL'
    elif 'POSITIVE' in text:
        return 'POSITIVE'
    elif 'NEGATIVE' in text:
        return 'NEGATIVE'
    else:
        return 'NEUTRAL'


if __name__ == '__main__':
    df = pd.read_excel('llama3.1-2.xlsx')
    df['sentiment_word'] = df['sentiment'].apply(get_sentiment)

    df.to_excel('llama3.1-2.xlsx', index=False)
