from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import sys
import os
from contextlib import contextmanager
import numpy as np

import nltk
from nltk.corpus import stopwords
try:
    STOPWORDS = set(stopwords.words('english'))
except Exception:
    nltk.download('stopwords', quiet=True)
    STOPWORDS = set(stopwords.words('english'))

# Adjust path to import from parent directory where ml_pipeline is
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml_pipeline import (
    text_agent as job_text_agent,
    keyword_agent as job_keyword_agent,
    sentiment_agent as job_sentiment_agent,
    combine_features as job_combine_features
)

from ml_pipeline_review import (
    text_agent as review_text_agent,
    keyword_agent as review_keyword_agent,
    sentiment_agent as review_sentiment_agent,
    combine_features as review_combine_features
)

app = FastAPI(title="Fraud Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Load job models
job_model = joblib.load(os.path.join(base_dir, "xgboost_model.pkl"))
job_vectorizer = joblib.load(os.path.join(base_dir, "tfidf_vectorizer.pkl"))
job_keywords = joblib.load(os.path.join(base_dir, "auto_fraud_keywords.pkl"))

# Load review models
review_model = joblib.load(os.path.join(base_dir, "review_xgboost_model.pkl"))
review_vectorizer = joblib.load(os.path.join(base_dir, "review_tfidf_vectorizer.pkl"))
review_keywords_list = joblib.load(os.path.join(base_dir, "review_keywords.pkl"))

class InferenceRequest(BaseModel):
    text: str
    type: str

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

@app.post("/predict")
def predict(req: InferenceRequest):
    if req.type not in ["job", "review"]:
        raise HTTPException(status_code=400, detail="Type must be 'job' or 'review'")
        
    user_input = req.text
    
    if req.type == "job":
        # Formatting input text explicitly to match train structure
        word_count = len(user_input.split())
        modified_text = user_input
        if word_count < 20: # Keyword duplication padding
            modified_text = f"{user_input} {user_input} {user_input}"
            
        simulated_structure = (f"TITLE: {modified_text} "
                               f"COMPANY: "
                               f"DESCRIPTION: {modified_text} "
                               f"REQUIREMENTS: {modified_text} "
                               f"BENEFITS:")
                               
        text_series = pd.Series([simulated_structure])
        
        with suppress_stdout():
            clean_text = job_text_agent(text_series)
            tfidf_matrix = job_vectorizer.transform(clean_text)
            keyword_features, kw_cols = job_keyword_agent(clean_text, job_keywords)
            sentiment_features, sent_cols = job_sentiment_agent(clean_text)
            final_features = job_combine_features(tfidf_matrix, keyword_features, sentiment_features)
            
            predictions = job_model.predict(final_features)
            probabilities = job_model.predict_proba(final_features)
            
        vectorizer = job_vectorizer
        model = job_model
        
    else:  # review
        text_series = pd.Series([user_input])
        
        with suppress_stdout():
            clean_text = review_text_agent(text_series)
            tfidf_matrix = review_vectorizer.transform(clean_text)
            keyword_features, kw_cols = review_keyword_agent(clean_text, review_keywords_list)
            sentiment_features, sent_cols = review_sentiment_agent(clean_text)
            final_features = review_combine_features(tfidf_matrix, keyword_features, sentiment_features)
            
            predictions = review_model.predict(final_features)
            probabilities = review_model.predict_proba(final_features)
            
        vectorizer = review_vectorizer
        model = review_model

    label = "Fake" if predictions[0] == 1 else "Real"
    risk_prob = float(probabilities[0][1])
    class_prob = float(probabilities[0][predictions[0]])
    risk_score = int(risk_prob * 100)
    
    # Sentiment
    compound_score = float(sentiment_features[0][3])
    if compound_score >= 0.05:
        sentiment_label = "Positive"
    elif compound_score <= -0.05:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"

    # Keywords
    kw_count = int(keyword_features[0][0])
    kw_present = int(keyword_features[0][1])
    payment_phrase = 0
    if len(keyword_features[0]) > 2:
        payment_phrase = int(keyword_features[0][2])
    
    if req.type == "job":
        if payment_phrase > 0 or kw_count > 5:
            keyword_risk_level = "High"
        elif kw_count > 0:
            keyword_risk_level = "Medium"
        else:
            keyword_risk_level = "Low"
    else:
        if kw_count > 3:
            keyword_risk_level = "High"
        elif kw_count > 0:
            keyword_risk_level = "Medium"
        else:
            keyword_risk_level = "Low"

    text_length = len(user_input.split())
    
    # Features
    try:
        tfidf_names = list(vectorizer.get_feature_names_out())
        feature_names = tfidf_names + kw_cols + sent_cols
        
        if hasattr(final_features, 'toarray'):
            instance_features = final_features.toarray()[0]
        elif hasattr(final_features, 'A'):
            instance_features = final_features.A[0]
        else:
            instance_features = np.array(final_features)[0]
            
        global_importances = model.feature_importances_
        local_importances = instance_features * global_importances
        
        top_indices = np.argsort(local_importances)[::-1][:5]
        top_features = {feature_names[i]: float(local_importances[i]) for i in top_indices if local_importances[i] > 0}
    except Exception as e:
        top_features = {}
        
    explanation = "The text appears genuine."
    if label == "Fake":
        explanation = f"Flagged as Fake with {risk_score}% risk score. "
        if kw_count > 0:
            explanation += f"Found {kw_count} suspicious keywords. "
        if payment_phrase > 0:
            explanation += "Mentions payment/fees which is highly suspicious. "
            
    # --- NEW EXPLAINABILITY FIELDS ---
    
    # 1. risk_category
    if risk_score <= 30:
        risk_category = "Low Risk"
    elif risk_score <= 60:
        risk_category = "Medium Risk"
    else:
        risk_category = "High Risk"
        
    # 2. matched_keywords
    raw_matched_keywords = []
    # Extract keywords from the cleaned text processing
    cleaned_input = str(clean_text.iloc[0]) if hasattr(clean_text, "iloc") else str(clean_text[0])
    keywords_to_check = job_keywords if req.type == "job" else review_keywords_list
    
    # Use simple substring matches for keywords in the cleaned text
    for kw in keywords_to_check:
        if kw in cleaned_input:
            raw_matched_keywords.append(kw)
            
    # Add payment phrases if matched in original text
    payment_phrases = [
        "registration fee", "processing fee", "payment required", "refundable fee",
        "no experience required", "earn money easily", "weekly income", "daily payment",
        "work from home no experience", "limited seats", "guaranteed income",
        "activation fee", "verification fee", "training fee payment", "deposit required"
    ]
    user_input_lower = user_input.lower()
    for pw in payment_phrases:
        if pw in user_input_lower:
            raw_matched_keywords.append(pw)
            
    raw_matched_keywords = list(set(raw_matched_keywords))
    
    # Filter keywords
    matched_keywords = []
    for kw in raw_matched_keywords:
        kw = kw.strip()
        # remove words shorter than 4 characters
        if len(kw) < 4:
            continue
        # remove common english stopwords
        if kw in STOPWORDS:
            continue
        # remove tokens containing only domain fragments like "com", "org", "net"
        if kw in ["com", "org", "net", "www", "http", "https"]:
            continue
        # only include keywords that contain alphabetic characters
        if not any(c.isalpha() for c in kw):
            continue
            
        matched_keywords.append(kw)
        
    # limit output to top 10 keywords
    matched_keywords = matched_keywords[:10]
    
    # 3. fraud_probability_explanation
    if label == "Fake" and kw_count > 0:
        fraud_probability_explanation = "Flagged as fraudulent. Suspicious promotional phrases and keywords were detected."
    elif label == "Fake":
        fraud_probability_explanation = "Flagged as fraudulent. Text structure and sentiment indicate potentially artificial or deceptive content."
    else:
        if kw_count > 0:
            fraud_probability_explanation = "Text shows natural language patterns. Some tracked keywords exist, but overall context is benign."
        else:
            fraud_probability_explanation = "Text shows natural language patterns with no suspicious markers."

    return {
        "prediction": label,
        "confidence": class_prob,
        "risk_score": risk_score,
        "sentiment_label": sentiment_label,
        "sentiment_score": compound_score,
        "text_length": text_length,
        "keyword_count": kw_count,
        "keyword_risk_level": keyword_risk_level,
        "top_features": top_features,
        "explanation": explanation.strip(),
        "risk_category": risk_category,
        "matched_keywords": matched_keywords,
        "fraud_probability_explanation": fraud_probability_explanation
    }
