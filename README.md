# **WiseSplit: Simplify Your Bill Splitting**

## **Project Motivation**

We’ve all been there: a night out with friends, a shared meal, and then the dreaded moment arrives — *Who paid for what?* Figuring out how to divide the bill fairly can become a stressful and tedious task. Whether it’s a dinner, a group vacation, or any shared expense, calculating who owes whom and by how much isn’t always straightforward. Enter **WiseSplit**, a smart platform designed to simplify the process of splitting bills and invoices between friends.

With **WiseSplit**, you can easily upload an invoice, let the AI extract all the necessary details, and automatically divide the expenses among your group. The platform uses **Generative AI** and **OCR** technology to parse your invoice, calculate totals, tax amounts, and even assign products to friends. Whether it's a dinner receipt or a hotel bill, **WiseSplit** makes it easy to figure out who owes what.

## **Why WiseSplit?**

- **Time-Saving**: No more manual calculations or back-and-forth on who owes whom.
- **AI-Powered**: Automatically processes invoice details and splits them fairly.
- **User-Friendly**: A simple and intuitive interface using **Streamlit**.
- **Fairness**: Ensures each person’s share is calculated correctly based on the invoice items.

---

## **Features**

- **Invoice Parsing**: Upload an image of your invoice, and the platform extracts product names, quantities, prices, and tax details using **OCR** and **Generative AI**.
- **Smart Price Allocation**: Split the bill fairly among friends, considering each person's share of the products.
- **User Profiles**: Add friends to the platform and easily assign them to products.
- **Total Calculation**: Get a breakdown of how much each friend owes, and see how much the payer spent.

---

## **How Does It Work?**

1. **Add Friends**: Add your friends who will be splitting the bill. 
2. **Upload Invoice**: Upload an image of your invoice (JPEG format), and the AI will process it to extract details such as product names, quantities, and prices.
3. **Assign Friends**: Assign the products to your friends and let the system split the costs.
4. **View Summary**: See who owes whom and how much, with an easy-to-read breakdown of the amounts.

---

## **Tech Stack**

- **GenAI**: Used for analyzing and extracting text from invoice images, utilizing advanced AI to recognize the details from the image.
- **OCR (Optical Character Recognition)**: Extracts text from images of invoices, allowing the platform to read and understand the contents.
- **Streamlit**: A lightweight and user-friendly framework for building interactive web apps with Python. Used to create the entire front-end interface.
- **Python**: The primary programming language used to implement the logic and the integration of AI/ML models.
