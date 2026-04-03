import pandas as pd
import numpy as np
import re
import nltk
import joblib

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.feature_selection import chi2

from scipy.sparse import hstack

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from xgboost import XGBClassifier

import warnings
warnings.filterwarnings("ignore")

nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)


##############################################
# AGENT 1 — TEXT CLEANING
##############################################

def text_agent(text_series):

    print("[Agent 1] Cleaning text...")

    lemmatizer = WordNetLemmatizer()

    stop_words = set(stopwords.words('english'))

    def clean(text):

        if not isinstance(text, str):

            return ""

        text = text.lower()

        text = re.sub(r'[^a-z\s]', ' ', text)

        text = re.sub(r'\s+', ' ', text).strip()

        words = text.split()

        words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]

        return " ".join(words)

    return text_series.apply(clean)


##############################################
# AGENT 2 — TFIDF FEATURES
##############################################

def tfidf_agent(clean_text):

    print("[Agent 2] TF-IDF features...")

    vectorizer = TfidfVectorizer(

        max_features=5000,

        ngram_range=(1,2),

        min_df=2

    )

    X = vectorizer.fit_transform(clean_text)

    return X, vectorizer


##############################################
# AGENT 3 - KEYWORD FRAUD AGENT
##############################################
def keyword_agent(clean_text_series, auto_fraud_keywords):
    print("[Agent 3] Extracting Keyword Fraud Features...")
    
    payment_phrases = [
        "registration fee", "processing fee", "payment required", "refundable fee",
        "no experience required", "earn money easily", "weekly income", "daily payment",
        "work from home no experience", "limited seats", "guaranteed income",
        "activation fee", "verification fee", "training fee payment", "deposit required"
    ]
    
    # Process keywords to match the clean text
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    def clean_kw(kw):
        words = [lemmatizer.lemmatize(w) for w in kw.lower().split() if w not in stop_words]
        return " ".join(words)
        
    cleaned_auto_kws = set([clean_kw(kw) for kw in auto_fraud_keywords if clean_kw(kw)])
    cleaned_payment_phrases = set([clean_kw(pw) for pw in payment_phrases if clean_kw(pw)])
    
    features = []
    for text in clean_text_series:
        # Auto keywords (chi2 optimized)
        count = sum(text.count(kw) for kw in cleaned_auto_kws)
        presence = 1 if count > 0 else 0
        
        # Payment phrases (new manual rules engine)
        contains_payment = 1 if any(pw in text for pw in cleaned_payment_phrases) else 0
        
        features.append([count, presence, contains_payment])
        
    keyword_matrix = np.array(features)
    keyword_cols = ["keyword_count", "keyword_present", "contains_payment_phrase"]
    return keyword_matrix, keyword_cols


##############################################
# AGENT 4 — SENTIMENT FEATURES
##############################################

def sentiment_agent(clean_text):

    print("[Agent 4] Sentiment features...")

    analyzer = SentimentIntensityAnalyzer()

    features = []

    for text in clean_text:

        s = analyzer.polarity_scores(text)

        features.append([

            s['pos'],

            s['neg'],

            s['neu'],

            s['compound']

        ])

    return np.array(features), [

        "sent_pos",

        "sent_neg",

        "sent_neu",

        "sent_compound"

    ]


##############################################
# COMBINE FEATURES
##############################################

def combine_features(tfidf, keyword, sentiment):

    print("[Pipeline] Combining features...")

    return hstack([tfidf, keyword, sentiment])


##############################################
# AGENT 5 — MODEL
##############################################

def xgboost_agent(X, y):

    print("[Agent 5] Training model...")

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.2,

        stratify=y,

        random_state=42

    )

    scale_pos_weight = sum(y_train==0) / sum(y_train==1)

    model = XGBClassifier(

        n_estimators=400,

        learning_rate=0.05,

        max_depth=7,

        subsample=0.8,

        colsample_bytree=0.8,

        eval_metric="logloss",

        scale_pos_weight=scale_pos_weight,

        random_state=42

    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    print("\n==============================")

    print("EVALUATION")

    print("==============================")

    print("Accuracy :", accuracy_score(y_test,preds))

    print("Precision:", precision_score(y_test,preds))

    print("Recall   :", recall_score(y_test,preds))

    print("F1-score :", f1_score(y_test,preds))

    print("\nConfusion Matrix")

    print(confusion_matrix(y_test,preds))

    print("\nClassification Report")

    print(classification_report(y_test,preds))

    return model


##############################################
# AGENT 6 — EXPLAINABILITY
##############################################

def explainability_agent(model, feature_names):

    print("\nTop important features:\n")

    importances = model.feature_importances_

    idx = np.argsort(importances)[::-1][:20]

    for i in idx:

        if i < len(feature_names):

            print(feature_names[i], ":", round(importances[i],5))


##############################################
# DATASET PREPARATION
##############################################

def prepare_dataset(path):

    print("\nLoading dataset:", path)

    df = pd.read_csv(path)


    ##########################################
    # CASE 1 — already text + label
    ##########################################

    if "text" in df.columns and "label" in df.columns:

        final_df = df[["text","label"]].copy()

        final_df = final_df.dropna()

        final_df = final_df.drop_duplicates(subset=["text"])


    ##########################################
    # CASE 2 — EMSCAD dataset
    ##########################################

    else:

        cols = [

            "title",

            "company_profile",

            "description",

            "requirements",

            "benefits"

        ]

        for c in cols:

            if c not in df.columns:

                df[c] = ""

            df[c] = df[c].fillna("")

        df["text"] = (

            "TITLE " + df["title"]

            + " COMPANY " + df["company_profile"]

            + " DESCRIPTION " + df["description"]

            + " REQUIREMENTS " + df["requirements"]

            + " BENEFITS " + df["benefits"]

        )

        df["label"] = df["fraudulent"]

        final_df = df[["text","label"]]


    print("\nDataset size:", final_df.shape)

    print("\nClass distribution:")

    print(final_df["label"].value_counts())

    return final_df


##############################################
# MAIN PIPELINE
##############################################

def main():

    DATASET = "final_combined_dataset.csv"

    df = prepare_dataset(DATASET)


    clean_text = text_agent(df["text"])


    tfidf_features, vectorizer = tfidf_agent(clean_text)


    chi2_scores, _ = chi2(tfidf_features, df["label"])

    top_idx = np.argsort(chi2_scores)[::-1][:100]

    auto_keywords = [

        vectorizer.get_feature_names_out()[i]

        for i in top_idx

    ]


    keyword_features, keyword_cols = keyword_agent(

        clean_text,

        auto_keywords

    )


    sentiment_features, sentiment_cols = sentiment_agent(

        clean_text

    )


    X = combine_features(

        tfidf_features,

        keyword_features,

        sentiment_features

    )


    feature_names = (

        list(vectorizer.get_feature_names_out())

        + keyword_cols

        + sentiment_cols

    )


    model = xgboost_agent(

        X,

        df["label"]

    )


    explainability_agent(

        model,

        feature_names

    )


    ##########################################
    # SAVE FILES
    ##########################################

    joblib.dump(model,"xgboost_model.pkl")

    joblib.dump(vectorizer,"tfidf_vectorizer.pkl")

    joblib.dump(auto_keywords,"auto_fraud_keywords.pkl")

    print("\nSaved files:")

    print("xgboost_model.pkl")

    print("tfidf_vectorizer.pkl")

    print("auto_fraud_keywords.pkl")


##############################################

if __name__ == "__main__":

    main()