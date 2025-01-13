# main.py
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import PromptTemplate, LLMChain
from typing import Dict, Any
import json

# Configure page settings
st.set_page_config(
    page_title="Transfer Pricing Calculator",
    page_icon="💰",
    layout="wide"
)

# Initialize Gemini model with Langchain
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=st.secrets["GOOGLE_API_KEY"],
        temperature=0.1
    )

# Create prompt template
transfer_pricing_template = """
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
{
    "price_range": "recommended price range as string",
    "markup_percentage": "markup percentage as string",
    "considerations": "key considerations as string",
    "compliance_notes": "compliance notes as string"
}
"""

prompt = PromptTemplate(
    input_variables=["parent_company", "subsidiary", "transaction_type", "transaction_value", "market_conditions"],
    template=transfer_pricing_template
)

def calculate_transfer_price(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate transfer pricing using Langchain and Gemini model
    """
    try:
        llm = get_llm()
        chain = LLMChain(llm=llm, prompt=prompt)
        
        response = chain.run(
            parent_company=data['parent_company'],
            subsidiary=data['subsidiary'],
            transaction_type=data['transaction_type'],
            transaction_value=data['transaction_value'],
            market_conditions=data['market_conditions']
        )
        # Extract the JSON string from the response
        result = json.loads(response)
        return result
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
