import pandas as pd
import joblib
import sys
import os
from contextlib import contextmanager

from ml_pipeline_review import text_agent, keyword_agent, sentiment_agent, combine_features

@contextmanager
def suppress_stdout():
    """Context manager to suppress print statements from the pipeline agents"""
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

def interactive_inference():
    print("\n--- Review Fraud Detection CLI ---")
    print("Loading saved model and vectorizer...")
    
    with suppress_stdout():
        model = joblib.load("review_xgboost_model.pkl")
        vectorizer = joblib.load("review_tfidf_vectorizer.pkl")
        auto_fraud_keywords = joblib.load("review_keywords.pkl")
    
    print("Ready.\n")
    
    while True:
        try:
            user_input = input("Enter text (type 'exit' to stop):\n> ").strip()
            if not user_input:
                continue
            if user_input.lower() == 'exit':
                break
                
            text_series = pd.Series([user_input])
            
            with suppress_stdout():
                clean_text = text_agent(text_series)
                tfidf_matrix = vectorizer.transform(clean_text)
                keyword_features, _ = keyword_agent(clean_text, auto_fraud_keywords)
                sentiment_features, _ = sentiment_agent(clean_text)
                final_features = combine_features(tfidf_matrix, keyword_features, sentiment_features)
                
                predictions = model.predict(final_features)
                probabilities = model.predict_proba(final_features)
            
            label = "Fake" if predictions[0] == 1 else "Real"
            risk_prob = probabilities[0][1] # Probability the class is exactly 1 (Fake)
            class_prob = probabilities[0][predictions[0]] # Probability of chosen prediction
            
            print(f"\nPrediction: {label}")
            print(f"Confidence: {class_prob:.2f}")
            print(f"Risk Score: {int(risk_prob * 100)}%\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error processing prediction: {e}")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    interactive_inference()
