from flask import Flask, flash, redirect,render_template, request,jsonify
import os
from together import Together
import re
import json
from transformers import pipeline



app = Flask(__name__)  
  

client = Together(api_key="13f55eef90ddf7b27426ad189cacd6364e5dab8161ed5272f9279727444cd979")

url = "https://api.together.xyz/inference"

Model="meta-llama/Llama-3-70b-chat-hf"

 # Initialize the Hugging Face pipeline with your model
model_ckpt = "abhyast/minilm-finetuned-emotion-class-model"
pipe = pipeline("text-classification", model=model_ckpt)

# Use the Hugging Face pipeline for emotion detection
def detect_emotion(text):
    results = pipe(text)
    # Assuming we always get at least one result, extract the first one
    return results[0] if results else None


 


@app.route('/')  
def index():  
    return render_template('index.html')  

def create_ad_slogan(pd,emotion):
    prompt = '''You are an creative Advertisement generator given the user emotions and product details.
    You have to generate very creative and attractive advertisement slogan so that it can market well and also you have to generate interesting Advertisement content/description
    
    '''
   
    
    fewshots = ''' Only respond in below mention output format
             {"ad_slogan": "Generated Ad slogan", "ad_description": "Generated Ad description"}
    
    Product details and user review based emotion given below:
         '''
    inputs="Product details :" + pd + " User emotion: "+ emotion
    prompt = prompt +   fewshots + inputs
    response = client.chat.completions.create(
    model=Model,
    messages=[{"role": "user", "content": prompt}],
    )
    print("response :\n",response.choices[0].message.content)
    res = response.choices[0].message.content
    res_dict = extract_json(res)  
    
    
    # Extract individual response values  
    adSlogan = res_dict["ad_slogan"]  
    ad_description = res_dict["ad_description"]
   
    return  adSlogan,ad_description



def extract_json(response):  
    json_match = re.search(r'\{.*\}', response, re.DOTALL)  
    if json_match:  
        json_string = json_match.group(0)  
        json_data = json.loads(json_string)  
        return json_data  
    else:  
        return None 

@app.route('/generate', methods=['POST'])
def generate():
    if request.method =="POST":
 
        user_review = request.form['user_review']
        prod_details =request.form['product_details']
        emotion = detect_emotion(user_review)
        emotion = emotion['label']
        print("emotion",emotion)
        adSlogan,ad_description = create_ad_slogan(prod_details,emotion)
          
    return render_template("prod.html", adSlogan=adSlogan,ad_description=ad_description,emotion=emotion)


  
if __name__ == '__main__':  
    app.run(host='localhost', port='8888', debug=True)  