import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import base64
import google.generativeai as genai

# Load environment variable for API Key
load_dotenv(dotenv_path='config.env')
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY not found in .env file")

# Setting up the GenAI model
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-pro")

# Initialize session state variables if they don't exist
if 'friends' not in st.session_state:
    st.session_state.friends = []

if 'payer' not in st.session_state:
    st.session_state.payer = None

if 'image_processed' not in st.session_state:
    st.session_state.image_processed = False

if 'products_data' not in st.session_state:
    st.session_state.products_data = []

if 'price_allocation' not in st.session_state:
    st.session_state.price_allocation = {}

if 'done_adding_friends' not in st.session_state:
    st.session_state.done_adding_friends = False

# Function to read and process the invoice image
def read_img(img):
    try:
        # Read image and encode it in base64
        image_data = base64.b64encode(img.read()).decode("utf-8")

        # Define the prompt to extract invoice data
        prompt = """Analyze the provided image of an invoice and extract its details into a single-line string with two lists, formatted as follows:
        The first list should include the following fields for each product on the invoice: Full Product Name(Make sure to add full name so each entry is unique), Quantity, Price (or Discounted Price, if applicable). If any product has a discount applied, identify the product and calculate its final discounted price by deducting the discount amount from its original price.
        The second list should include the following summary fields: Total Amount Before Tax, Tax Amount, Total Amount After Tax. Ensure all amounts reflect any discounts applied.
        Both lists should be enclosed in square brackets [] and separated by a semicolon ;. Omit any unrelated information, formatting artifacts, or decorative elements. Ensure the extraction is accurate and consistent with the invoice data. Present the extracted data in plain text format.
        Example output format:
        [Product1, Quantity1, FinalPrice1; Product2, Quantity2, FinalPrice2; ...][TotalBeforeTax, TaxAmount, TotalAfterTax]"""

        input_data = [{'mime_type': 'image/jpeg', 'data': image_data}, prompt]

        # Get response from the model
        response = model.generate_content(input_data)

        return response.text

    except Exception as e:
        return f"Error during API processing: {str(e)}"

# Streamlit UI for the friends list
st.title("Wisely Split: Invoice and Friend's List App")

# Step 1: Add Friends
st.subheader("Add Friends to Split the Invoice")
col1, col2 = st.columns([4, 1])  # Adjust width ratio to make textbox wider
with col1:
    name = st.text_input("", placeholder="Enter a friend's name here...")
    submit_button = st.button("Add Friend")

# Handle logic when the submit button is clicked
if submit_button:
    if name:
        if name not in st.session_state.friends:
            st.session_state.friends.append(name)
            st.success(f"Added {name} to the list!")
        else:
            st.warning(f"{name} is already in the list!")
    else:
        st.warning("Please enter a name!")

# Display the friends list
if st.session_state.friends:
    df = pd.DataFrame(st.session_state.friends, columns=["Friend's Name"])
    st.subheader("Friend's List")
    st.dataframe(df)

# Step 2: Ask if the user is done adding friends
if not st.session_state.done_adding_friends:
    done_button = st.button("Are you done adding friends?")
    if done_button:
        st.session_state.done_adding_friends = True
        st.success("You are done adding friends. Now, let's proceed.")

# Step 3: Ask Who Paid the Bill (only after "done" is clicked)
if st.session_state.done_adding_friends and not st.session_state.payer:
    st.subheader("Who Paid the Bill?")
    payer = st.selectbox("Select who paid the bill", st.session_state.friends)
    
    if payer:
        st.session_state.payer = payer
        st.success(f"{payer} is marked as the payer.")

# Step 4: Upload the Invoice Image
if st.session_state.payer and not st.session_state.image_processed:
    st.subheader("Upload an Invoice")
    img = st.file_uploader("Choose an invoice image", type=["jpeg", "jpg"])

    if img:
        with st.spinner("Processing your invoice..."):
            response = read_img(img)

        if "Error" in response:
            st.error("Failed to process the image. Please try again.")
        else:
            # Process the image only once
            st.session_state.image_processed = True
            st.session_state.image_data = response  # Store the response for future use

            # Extract products and summary from the invoice response
            products_str, summary_str = response.strip('[]').split('][')
            products = products_str.split(";")

            parsed_products = []
            for product in products:
                parts = product.strip().split(",")
                name = parts[0].strip()
                quantity = int(parts[1].strip())
                price = round(float(parts[2].strip()), 2)  # Round to 2 decimals
                parsed_products.append([name, quantity, price])

            # Extract summary (total before tax, tax, total after tax)
            parsed_summary = summary_str.strip().split(",")
            
            # Strip unwanted characters such as brackets and extra spaces from the summary
            total_before_tax = round(float(parsed_summary[0].strip(" []")), 2)  # Clean up and round
            total_tax = round(float(parsed_summary[1].strip(" []")), 2)
            total_after_tax = round(float(parsed_summary[2].strip(" []")), 2)

            # Calculate tax per product based on the price
            total_product_price = sum([product[2] * product[1] for product in parsed_products])  # Total price of all products
            tax_per_unit = total_tax / total_product_price  # Tax rate per unit price

            # Adding Tax and Price (Including Tax) to the product table
            for product in parsed_products:
                product_name = product[0]
                quantity = product[1]
                price = product[2]
                product_tax = round(price * quantity * tax_per_unit, 2)  # Round tax to 2 decimals
                price_including_tax = round(price + product_tax, 2)  # Round price including tax to 2 decimals
                product.append(product_tax)  # Add tax
                product.append(price_including_tax)  # Add price including tax

            # Store parsed products data in session state
            st.session_state.products_data = parsed_products

            # Create a DataFrame to show the products table with added Tax and Price (Including Tax)
            df1 = pd.DataFrame(parsed_products, columns=['Product', 'Quantity', 'Price', 'Tax', 'Price (Including Tax)'])
            st.subheader("Products")
            st.table(df1)

# Step 5: Assign Friends to Products and Split the Cost
if st.session_state.image_processed:
    st.subheader("Assign Friends to Products")

    # Dictionary to store price allocation per product
    for i, product in enumerate(st.session_state.products_data):
        product_name = product[0]
        product_price = product[4]  # Price (Including Tax)
        
        # Multiselect to choose friends for this product
        assigned_friends = st.multiselect(f"Assign friends to {product_name} (Price: {product_price})", 
                                          st.session_state.friends, key=f"{i}_friends")

        if assigned_friends:
            # Split price equally among the assigned friends
            split_price = round(product_price / len(assigned_friends), 2)  # Round split price to 2 decimals
            st.session_state.price_allocation[product_name] = {
                'assigned_friends': assigned_friends,
                'split_price': split_price
            }

    # Step 6: Show the final split price for each product
    if st.session_state.price_allocation:
        st.subheader("Price Splitting Summary")
        allocation_data = []

        for product, allocation in st.session_state.price_allocation.items():
            allocation_data.append([product, ", ".join(allocation['assigned_friends']), f"${allocation['split_price']:.2f}"])

        df3 = pd.DataFrame(allocation_data, columns=["Product", "Assigned Friends", "Split Price"])
        st.table(df3)

        # Step 7: Add "Calculate" Button to perform calculations manually
        calculate_button = st.button("Calculate Split and Owed Amounts")

        if calculate_button:
            # Calculate Who Owes How Much to Whom
            st.subheader("Who Owes How Much to Whom?")

            total_paid = {st.session_state.payer: 0}  # Track how much the payer paid
            owed_amount = {friend: 0 for friend in st.session_state.friends}  # Track what everyone owes

            for product, allocation in st.session_state.price_allocation.items():
                split_price = allocation['split_price']
                for friend in allocation['assigned_friends']:
                    if friend != st.session_state.payer:
                        owed_amount[friend] += split_price

            # Display the amounts owed by each friend to the payer
            for friend, amount in owed_amount.items():
                if friend != st.session_state.payer and amount > 0:
                    st.write(f"{friend} owes {st.session_state.payer} ${round(amount, 2)}")

            # Display how much the payer spent on themselves
            total_spent = sum([allocation['split_price'] for product, allocation in st.session_state.price_allocation.items() if st.session_state.payer in allocation['assigned_friends']])
            st.write(f"{st.session_state.payer} spent ${round(total_spent, 2)} on themselves.")
