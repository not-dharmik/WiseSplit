from dotenv import load_dotenv
import time
import os
import base64
import google.generativeai as genai
import streamlit as st
import pandas as pd

#Loading env variable
load_dotenv(dotenv_path='config.env')
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY not found in .env file")

#Setting GenAI 
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-pro")


def read_img(img):
    try:
        # Read image and encode it in base64
        image_data = base64.b64encode(img.read()).decode("utf-8")
        
        # Define the prompt
        prompt = """Analyze the provided image of an invoice and extract its details into a single-line string with two lists, formatted as follows:
        The first list should include the following fields for each product on the invoice: Full Product Name, Quantity, Price (or Discounted Price, if applicable). If any product has a discount applied, identify the product and calculate its final discounted price by deducting the discount amount from its original price.
        The second list should include the following summary fields: Total Amount Before Tax, Tax Amount, Total Amount After Tax. Ensure all amounts reflect any discounts applied.
        Both lists should be enclosed in square brackets [] and separated by a semicolon ;. Omit any unrelated information, formatting artifacts, or decorative elements. Ensure the extraction is accurate and consistent with the invoice data. Present the extracted data in plain text format.
        Example output format:
        [Product1, Quantity1, FinalPrice1; Product2, Quantity2, FinalPrice2; ...][TotalBeforeTax, TaxAmount, TotalAfterTax]"""

        input_data = [{'mime_type': 'image/jpeg', 'data': image_data}, prompt]
        # Get response from the model
        response = model.generate_content(input_data)
        print(response.text)
        return response.text

    except Exception as e:
        return f"Error: {e}"




st.markdown("<h1>This app helps you <i><u>split-WISELY</u></i></h1>", unsafe_allow_html=True)
img = st.file_uploader("Upload an invoice")

if img:
    with st.spinner("Processing your invoice..."): 
        response = read_img(img)
    
    if "Error" in response:
            st.error("Failed to process the image. Please try again.")
    else:
        #print(response)
        products1, summary = response.strip('[]').split('][')
        products = products1.split(";")

        parsed_products = []
        for product in products:
            parts = product.strip().split(",")
            name = parts[0].strip()
            quantity = int(parts[1].strip())
            price = float(parts[2].strip())
            parsed_products.append([name, quantity, price])
        df1 = pd.DataFrame(parsed_products, columns=['Product', 'Quantity', 'Price'])        
        st.subheader("Products")
        st.table(df1)

        print(summary)
        parsed_summary = summary.strip().split(",")
        for i in range(len(parsed_summary)):
            parsed_summary[i] = parsed_summary[i].strip("]")
            parsed_summary[i] = parsed_summary[i].strip()
            parsed_summary[i] = float(parsed_summary[i])
            print(parsed_summary[i])
        
        df2 = pd.DataFrame([parsed_summary], columns=['Price (Excluding Tax)', 'Tax', 'Price (Including Tax)'])        
        st.subheader("Total")
        st.table(df2)
        

        



        


 

    

