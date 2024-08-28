import pandas as pd
import numpy as np
import re
import unicodedata
import nltk
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
import contractions
import string 
import joblib

nltk.download('punkt')
nltk.download('stopwords')
stopwords = nltk.corpus.stopwords.words('english')
ps = PorterStemmer()
wnl = WordNetLemmatizer()

msg_model = joblib.load('./models/msgs_Extra_Trees_model.pkl')
tfidf = joblib.load('./models/tfidf_model.pkl')

def message_analysis(message):
    try:
        df_message = preprocess_message(message)
        prediction = msg_model.predict(df_message)
        return prediction

    except Exception as e:
        print(e)
        return {"error": "Error while analyzing the message"}
    

def preprocess_message(message):
    df = pd.DataFrame([message], columns=['text_combined'])

    df['text_combined'] = df['text_combined'].str.lower()
    df['text_combined'] = df['text_combined'].apply(remove_accents)
    df['text_combined'] = df['text_combined'].apply(remove_special_characters)
    df['text_combined'] = df['text_combined'].apply(correct_contractions)
    df['text_combined'] = df.apply(lambda row: nltk.word_tokenize(row['text_combined']), axis=1)
    df['text_combined'] = df['text_combined'].apply(remove_stopwords)
    df['text_combined'] = df['text_combined'].apply(stemming)
    df['text_combined'] = df['text_combined'].apply(lemmatization)
    df['text_combined'] = df['text_combined'].apply(remove_short_words)
    df['text_combined'] = df['text_combined'].apply(normalize_text)
    df['text_combined'] = df['text_combined'].apply(text_preprocessing)
    df['text_combined'] = df['text_combined'].apply(remove_specific_words)
    df['text_combined'] = df['text_combined'].replace(np.nan, '', regex=True)
    df = tfidf.transform(df['text_combined'])
    tv_matrix = df.toarray()
    vocab = tfidf.get_feature_names_out()
    df = pd.DataFrame(np.round(tv_matrix, 2), columns=vocab)

    return df

def remove_accents(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')

def remove_special_characters(text):
    text = re.sub(r'[^a-zA-z\s]', '', text)
    return text

def correct_contractions(text):
    return contractions.fix(text)

def remove_stopwords(text):
    return [word for word in text if word not in stopwords]

def stemming(text):
    return [ps.stem(word) for word in text]

def lemmatization(text):
    return [wnl.lemmatize(word) for word in text]

# Remove words with length less than 4 characters
def remove_short_words(text):
    return [word for word in text if len(word) > 3]

def normalize_text(text):
    return ' '.join(text)

def text_preprocessing(text):
    text = str(text)
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('@\w+\s*', '', text)
    text = re.sub("\\W"," ",text) 
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('http', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', '', text)
    return text

def remove_specific_words(text):
    specific_words = ['subject', 'submiss', 'note', 'viru', 'virutotal', 
                      'submissionid', 'email', 'messag', 'file', 'enron', 
                      'mail', 'sender', 'receiv', 'attach', 'receiv', 'total']
    
    return ' '.join([word for word in text.split() if word not in specific_words])
