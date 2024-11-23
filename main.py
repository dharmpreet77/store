import os
import json
import streamlit as st
from groq import Groq

# Streamlit page configuration
st.set_page_config(
    page_title="Convenience Store - ChatBot",
    page_icon="🛒",
    layout="wide"
)

# Embed Bootstrap CSS into Streamlit app and apply custom CSS for title styling
st.markdown(
    """
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" 
    integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
    <style>
        .custom-title {
            font-size: 25px;
            font-weight: 600;
            margin-bottom: 0px;
            padding:0;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Load API Key from config file
working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))
GROQ_API_KEY = config_data["GROQ_API_KEY"]

# Save the API key to environment variable
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Initialize Groq client
client = Groq()

# Load product data from JSON
products_file = os.path.join(working_dir, "products.json")
with open(products_file, "r") as f:
    products_data = json.load(f)

# Load store info data from JSON
store_info_file = os.path.join(working_dir, "store_info.json")
with open(store_info_file, "r") as f:
    store_info_data = json.load(f)

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to display products as cards using Bootstrap
def display_products(products):
    card_template = """
    <div class="card" style="width: 100%; margin: 10px;">
        <div class="card-body">
            <h5 style="font-weight:600;margin:0;font-size:18px">{ProductName}</h5>
            <p class="card-text">
                Weight: {Weight}<br>
                Price: ${Price}<br>
                Available Stock: {AvailableStock}
            </p>
        </div>
    </div>
    """
    # Use Bootstrap grid system for cards
    html_content = '<div class="container"><div class="row">'
    for idx, product in enumerate(products):
        html_content += f'<div class="col-md-4">{card_template.format(**product)}</div>'
        if (idx + 1) % 3 == 0:
            html_content += '</div><div class="row">'  # Close and start a new row
    html_content += '</div></div>'  # Close the last row and container
    
    st.markdown(html_content, unsafe_allow_html=True)

# Function to search for products
def search_products(query=None):
    if not query:
        return products_data
    else:
        # Filter products based on search query
        return [
            product
            for product in products_data
            if query.lower() in product["ProductName"].lower() or query.lower() in product["Category"].lower()
        ]

# Multi-Language Support
def detect_language(text):
    """Basic language detection for 10 languages."""
    languages = {
        "english": ["hello", "hi", "how", "thank you"],
        "french": ["bonjour", "merci", "français"],
        "spanish": ["hola", "gracias", "español"],
        "german": ["hallo", "danke", "deutsch"],
        "italian": ["ciao", "grazie", "italiano"],
        "portuguese": ["olá", "obrigado", "português"],
        "dutch": ["hallo", "dank", "nederlands"],
        "russian": ["здравствуйте", "спасибо", "русский"],
        "chinese": ["你好", "谢谢", "中文"],
        "arabic": ["مرحبا", "شكرا", "عربي"]
    }
    for lang, keywords in languages.items():
        if any(word in text.lower() for word in keywords):
            return lang.title()
    return "English"  # Default to English

# Handle Special Queries
def handle_special_queries(query):
    if "complaint" in query.lower():
        return "To register a complaint, please call +1 (236) 338-0491 or email info@junaidconveniencestore.com."
    elif "lost and found" in query.lower():
        return "For lost and found inquiries, visit the store or call +1 (236) 338-0491."
    elif "special order" in query.lower():
        return (
            "We offer special orders for events and bulk purchases. Contact us at info@junaidconveniencestore.com "
            "or call us at +1 (236) 338-0491 for details."
        )
    elif "membership" in query.lower():
        plans = store_info_data["membership_plans"]
        response = "Here are our membership plans:\n"
        for plan, details in plans.items():
            response += f"**{plan.replace('_', ' ').title()}** - {details['price']}\n"
            response += "Benefits:\n"
            for benefit in details["benefits"]:
                response += f"- {benefit}\n"
        return response
    elif "place order" in query.lower() or "order" in query.lower():
        return (
            "Currently, we do not have an online ordering system. You can place a phone order by calling "
            "+1 (236) 338-0491 or visiting the store during working hours. For more information, email "
            "info@junaidconveniencestore.com."
        )
    return None

# Sticky title
st.markdown("<h1 class='custom-title'>🛒 Convenience Store ChatBot</h1>", unsafe_allow_html=True)

# Search Products Section
product_search_query = st.text_input("", placeholder="Search for products by name or category")
if product_search_query:
    search_results = search_products(product_search_query)
    if search_results:
        st.subheader("Search Results")
        display_products(search_results)
    else:
        st.write("No products found. Please refine your search.")

# Tabs for quick actions
tabs = st.tabs([
    "Is anyone available to chat?",
    "Store Location",
    "Store Working Hours",
    "Payment Methods",
    "Special Offers",
    "Store Policies",
    "Membership Plans",
    "FAQs"
])

# Add content to each tab dynamically from JSON data
with tabs[0]:
    st.write("Yes! Our team is here to assist you. Welcome to Junaid's Convenience Store! How can I help you today?")

with tabs[1]:
    location = store_info_data["location"]
    st.write(f"Our store is located at {location['address']}, {location['city']}, {location['state']} - {location['zip_code']}, {location['country']}.")
    st.write("We look forward to your visit!")

with tabs[2]:
    hours = store_info_data["working_hours"]
    st.write("Our working hours are:")
    for day, time in hours.items():
        st.write(f"{day.replace('_', ' ').title()}: {time}")

with tabs[3]:
    payment_methods = store_info_data["payment_methods"]
    st.write("We accept the following payment methods:")
    for method in payment_methods:
        st.write(f"- {method}")

with tabs[4]:
    special_offers = store_info_data["additional_information"]["special_offers"]
    st.write("### Special Offers:")

    # Display Winter Offers
    for offer in special_offers.get("winter_offers", []):
        st.write(f"- {offer}")

with tabs[5]:
    policies = store_info_data["store_policies"]
    st.write("Store Policies:")
    st.write(f"**Returns & Exchanges**: {policies['returns_exchanges']}")
    st.write(f"**Refund Policy**: {policies['refund_policy']}")
    st.write(f"**Privacy Policy**: {policies['privacy_policy']}")
    st.write(f"**Customer Support**: {policies['customer_support']}")

with tabs[6]:
    membership_plans = store_info_data["membership_plans"]
    st.write("Membership Plans:")
    for plan, details in membership_plans.items():
        st.write(f"**{plan.replace('_', ' ').title()}** - {details['price']}")
        st.write("Benefits:")
        for benefit in details["benefits"]:
            st.write(f"- {benefit}")

with tabs[7]:
    faqs = store_info_data["faqs"]
    st.write("Frequently Asked Questions:")
    for faq in faqs:
        st.write(f"**Q: {faq['question']}**")
        st.write(f"A: {faq['answer']}")

def handle_special_queries(query):
    if "complaint" in query.lower():
        return "To register a complaint, please call +1 (236) 338-0491 or email info@junaidconveniencestore.com."
    elif "lost and found" in query.lower():
        return "For lost and found inquiries, visit the store or call +1 (236) 338-0491."
    elif "special order" in query.lower():
        return (
            "We offer special orders for events and bulk purchases. Contact us at info@junaidconveniencestore.com "
            "or call us at +1 (236) 338-0491 for details."
        )
    elif "membership" in query.lower():
        plans = store_info_data["membership_plans"]
        response = "Here are our membership plans:\n"
        for plan, details in plans.items():
            response += f"**{plan.replace('_', ' ').title()}** - {details['price']}\n"
            response += "Benefits:\n"
            for benefit in details["benefits"]:
                response += f"- {benefit}\n"
        return response
    elif "place order" in query.lower() or "order" in query.lower():
        return (
            "At Junaid Convenience Store, we currently do not have an online ordering system. "
            "However, you can place a phone order or visit us in-store.\n\n"
            "**Phone Order Details**:\n"
            "- Call: +1 (236) 338-0491\n"
            "- Email: info@junaidconveniencestore.com\n"
            "- Website: junaidconveniencestore.com\n\n"
            "**Store Visit**:\n"
            "Visit us during our working hours:\n"
            "- Monday to Friday: 8:00 AM - 10:00 PM\n"
            "- Saturday: 9:00 AM - 11:00 PM\n"
            "- Sunday: 10:00 AM - 9:00 PM\n\n"
            "Our friendly staff will be happy to assist you with your order."
        )
    return None

# General Chatbot Input Box at the Bottom
user_prompt = st.chat_input("Ask anything (e.g., About Product, store policies, general inquiries)...")
if user_prompt:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # Check for special queries
    special_response = handle_special_queries(user_prompt)
    if special_response:
        assistant_response = special_response
    else:
        # Dynamically construct context from JSON data
        store_context = (
            f"Store Name: {store_info_data['store_name']}\n"
            f"Description: {store_info_data['description']}\n"
            f"Location: {store_info_data['location']['address']}, {store_info_data['location']['city']}, "
            f"{store_info_data['location']['state']} - {store_info_data['location']['zip_code']}, {store_info_data['location']['country']}\n"
            f"Working Hours: {', '.join([f'{day.replace('_', ' ').title()}: {time}' for day, time in store_info_data['working_hours'].items()])}\n"
            f"Payment Methods: {', '.join(store_info_data['payment_methods'])}\n"
            f"Policies: Returns - {store_info_data['store_policies']['returns_exchanges']}, "
            f"Refund - {store_info_data['store_policies']['refund_policy']}, "
            f"Privacy - {store_info_data['store_policies']['privacy_policy']}\n"
            f"Special Offers: {', '.join(store_info_data['additional_information']['special_offers']['winter_offers'])}\n"
            f"Membership Plans: {', '.join([f'{plan.replace('_', ' ').title()} - {details['price']} ({', '.join(details['benefits'])})' for plan, details in store_info_data['membership_plans'].items()])}\n"
            f"FAQs: {', '.join([faq['question'] for faq in store_info_data['faqs']])}\n"
        )

        product_context = "Products:\n" + "\n".join(
            [f"{product['ProductName']} - {product['Weight']} - ${product['Price']} (Stock: {product['AvailableStock']})"
             for product in products_data]
        )

        # Combine context
        combined_context = f"Store Information:\n{store_context}\n\n{product_context}"

        # Construct the conversation messages for the model
        messages = [
            {"role": "system", "content": "You are an intelligent assistant for Junaid Convenience Store. Answer user queries based on the context provided."},
            {"role": "system", "content": combined_context},
        ]

        # Add the user's query to the messages
        messages.append({"role": "user", "content": user_prompt})

        try:
            # Call the language model API
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages
            )
            assistant_response = response.choices[0].message.content
        except Exception as e:
            assistant_response = "I'm sorry, something went wrong while processing your request. Please try again."
            st.error(f"Error: {e}")

    # Add assistant's response to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

# Display the entire chat history
if st.session_state.chat_history:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
