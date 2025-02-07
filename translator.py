import pandas as pd
from deep_translator import GoogleTranslator


def preprocess(text: str):
    en_text = GoogleTranslator(source='auto', target='en').translate(text[0:3000])
    return en_text


if __name__ == '__main__':
    df = pd.read_excel('hromadske.xlsx')
    df['translated'] = df['text'].apply(preprocess)

    df.to_excel('translated_hromadske.xlsx', index=False)
