import streamlit as st
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import GoogleGenerativeAI
from langchain.schema import StrOutputParser
import json

# Configure page settings
st.set_page_config(
    page_title="Transfer Pricing Calculator",
    page_icon="💰",
    layout="wide"
)

# Initialize Gemini API
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

def get_llm_chain():
    """
    Creates and returns an LLMChain for transfer pricing calculations using Gemini.
    """
    llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)

    template = """
    Please analyze the following transfer pricing scenario and provide calculations:
    
    Company Details:
    - Parent Company: {parent_company}
    - Subsidiary: {subsidiary}
    - Transaction Type: {transaction_type}
    - Transaction Value: {transaction_value}
    - Market Conditions: {market_conditions}
    
    Please provide:
    1. Recommended transfer price range
    2. Markup percentage
    3. Key considerations
    4. Compliance notes
    
    Return the response strictly as a JSON with these exact keys:
    {{
        "price_range": "recommended price range as string",
        "markup_percentage": "markup percentage as string",
        "considerations": "key considerations as string",
        "compliance_notes": "compliance notes as string"
    }}
    """

    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    return chain

def calculate_transfer_price(data):
    """
    Calculate transfer pricing using Gemini model via LangChain
    """

    try:
        chain = get_llm_chain()
        response = chain.invoke(data)
        # Extract the JSON string from the response
        result = json.loads(response)
        return result
    except json.JSONDecodeError as e:
      st.error(f"Error decoding JSON: {e}. Please check the model's output format.")
      return None
    except Exception as e:
        st.error(f"Error in calculation: {str(e)}")
        return None

def main():
    st.title("Transfer Pricing Calculator")
    st.write("Calculate appropriate transfer prices for intercompany transactions")

    with st.form("transfer_pricing_form"):
        col1, col2 = st.columns(2)

        with col1:
            parent_company = st.text_input("Parent Company Name")
            subsidiary = st.text_input("Subsidiary Name")
            transaction_type = st.selectbox(
                "Transaction Type",
                ["Goods", "Services", "Intellectual Property", "Financial Services"]
            )

        with col2:
            transaction_value = st.number_input("Transaction Value (USD)", min_value=0.0)
            market_conditions = st.text_area("Market Conditions")

        submit_button = st.form_submit_button("Calculate Transfer Price")

        if submit_button:
            if not all([parent_company, subsidiary, transaction_value]):
                st.warning("Please fill in all required fields")
                return

            input_data = {
                "parent_company": parent_company,
                "subsidiary": subsidiary,
                "transaction_type": transaction_type,
                "transaction_value": transaction_value,
                "market_conditions": market_conditions
            }

            with st.spinner("Calculating transfer pricing..."):
                result = calculate_transfer_price(input_data)

            if result:
                st.subheader("Results")
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Recommended Price Range", result["price_range"])
                    st.metric("Markup Percentage", result["markup_percentage"])

                with col2:
                    st.subheader("Key Considerations")
                    st.write(result["considerations"])

                    st.subheader("Compliance Notes")
                    st.write(result["compliance_notes"])

                st.download_button(
                    "Download Report",
                    json.dumps(result, indent=2),
                    file_name="transfer_pricing_report.json",
                    mime="application/json"
                )

if __name__ == "__main__":
    main()
