import pandas as pd
import numpy as np
import re
import nltk
import joblib
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import warnings
warnings.filterwarnings("ignore")

nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# AGENT 1 - TEXT PROCESSING AGENT
def text_agent(text_series):
    print("[Agent 1] Processing text (lower, punctuation, numbers, stopwords, lemmatization)...")
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

# AGENT 2 - TF-IDF FEATURE AGENT
def tfidf_agent(clean_text_series):
    print("[Agent 2] Extracting TF-IDF Features...")
    vectorizer = TfidfVectorizer(max_features=6000, ngram_range=(1, 2), min_df=2)
    tfidf_matrix = vectorizer.fit_transform(clean_text_series)
    return tfidf_matrix, vectorizer

# AGENT 3 - KEYWORD FRAUD AGENT
def keyword_agent(clean_text_series, auto_fraud_keywords):
    print("[Agent 3] Extracting Auto Keyword Fraud Features...")
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    def clean_kw(kw):
        words = [lemmatizer.lemmatize(w) for w in kw.lower().split() if w not in stop_words]
        return " ".join(words)

    cleaned_auto_kws = set([clean_kw(kw) for kw in auto_fraud_keywords if clean_kw(kw)])
    
    features = []
    for text in clean_text_series:
        count = sum(text.count(kw) for kw in cleaned_auto_kws)
        presence = 1 if count > 0 else 0
        features.append([count, presence])
        
    keyword_matrix = np.array(features)
    keyword_cols = ["keyword_count", "keyword_present"]
    return keyword_matrix, keyword_cols

# AGENT 4 - SENTIMENT ANALYSIS AGENT
def sentiment_agent(clean_text_series):
    print("[Agent 4] Extracting Sentiment Features via VADER...")
    analyzer = SentimentIntensityAnalyzer()
    features = []
    for text in clean_text_series:
        scores = analyzer.polarity_scores(text)
        features.append([scores['pos'], scores['neg'], scores['neu'], scores['compound']])
    sentiment_matrix = np.array(features)
    sentiment_cols = ["sentiment_pos", "sentiment_neg", "sentiment_neu", "sentiment_compound"]
    return sentiment_matrix, sentiment_cols

# COMBINE FEATURES FUNCTION
def combine_features(tfidf_matrix, keyword_matrix, sentiment_matrix):
    print("[Pipeline] Combining Features...")
    return hstack([tfidf_matrix, keyword_matrix, sentiment_matrix])

# AGENT 5 - XGBOOST MODEL AGENT
def xgboost_agent(feature_matrix, labels):
    print("[Agent 5] Training XGBoost Model...")
    X_train, X_test, y_train, y_test = train_test_split(
        feature_matrix, labels, test_size=0.20, stratify=labels, random_state=42
    )

    scale_pos_weight = sum(y_train == 0) / sum(y_train == 1) if sum(y_train == 1) > 0 else 1

    model = XGBClassifier(
        n_estimators=400,
        learning_rate=0.05,
        max_depth=7,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric='logloss',
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        use_label_encoder=False
    )
    
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    
    print("\n" + "="*40)
    print("EVALUATION METRICS")
    print("="*40)
    print(f"Accuracy:  {accuracy_score(y_test, preds):.4f}")
    print(f"Precision: {precision_score(y_test, preds):.4f}")
    print(f"Recall:    {recall_score(y_test, preds):.4f}")
    print(f"F1-Score:  {f1_score(y_test, preds):.4f}")
    print("-" * 40)
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, preds))
    
    return model

# AGENT 6 - EXPLAINABILITY AGENT
def explainability_agent(model, feature_names):
    print("\n" + "="*40)
    print("[Agent 6] Explainability - Top Influencing Features")
    print("="*40)
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    for i in range(20):
        if i < len(indices):
            idx = indices[i]
            col_name = feature_names[idx] if idx < len(feature_names) else f"Unknown_Idx_{idx}"
            prob_score = importances[idx]
            print(f"{i+1:2d}. {col_name:<30} : {prob_score:.5f}")


def prepare_dataset(filepath):
    print(f"Loading dataset from: {filepath}")
    df = pd.read_csv(filepath)
    df = df.dropna(subset=['text', 'label'])
    df['label'] = df['label'].astype(int)
    
    # Shuffle dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"Dataset Size: {df.shape[0]}")
    print("\nClass Distribution:")
    print(df['label'].value_counts())
    print("\n")
    return df

def main():
    filepath = 'final_fake_review_dataset.csv'
    df = prepare_dataset(filepath)
    
    clean_text = text_agent(df['text'])
    tfidf_features, vectorizer = tfidf_agent(clean_text)
    
    from sklearn.feature_selection import chi2
    chi2_scores, _ = chi2(tfidf_features, df['label'])
    top_indices = np.argsort(chi2_scores)[::-1][:100]
    all_feature_names = vectorizer.get_feature_names_out()
    auto_fraud_keywords = [all_feature_names[i] for i in top_indices]
    
    keyword_features, keyword_cols = keyword_agent(clean_text, auto_fraud_keywords)
    sentiment_features, sentiment_cols = sentiment_agent(clean_text)
    
    final_features = combine_features(tfidf_features, keyword_features, sentiment_features)
    feature_names = list(vectorizer.get_feature_names_out()) + keyword_cols + sentiment_cols
    
    model = xgboost_agent(final_features, df['label'])
    explainability_agent(model, feature_names)

    joblib.dump(model, "review_xgboost_model.pkl")
    joblib.dump(vectorizer, "review_tfidf_vectorizer.pkl")
    joblib.dump(auto_fraud_keywords, "review_keywords.pkl")
    print("\nSaved: review_xgboost_model.pkl")
    print("Saved: review_tfidf_vectorizer.pkl")
    print("Saved: review_keywords.pkl")

if __name__ == "__main__":
    main()
