import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/predict';

export const predictFraud = async (text, type) => {
    try {
        const response = await axios.post(API_URL, {
            text: text,
            type: type
        });
        
        return response.data;
    } catch (error) {
        console.error("Error making prediction request:", error);
        throw error;
    }
};
