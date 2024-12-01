import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
from os.path import join
import zipfile

# streamlit configuration
st.set_page_config(page_title='Bank Transactions Analysis', layout='wide')

# load data
# Define paths
compressed_path = join('data', 'bank_transactions.csv.zip')
extracted_path = join('data', 'bank_transactions.csv')

# Extract the CSV if not already done
if not os.path.exists(extracted_path):
    with zipfile.ZipFile(compressed_path, 'r') as zip_ref:
        zip_ref.extractall('data')

data_path = join('data', 'bank_transactions.csv')
df = pd.read_csv(data_path)

# data cleaning
df.dropna(inplace=True)
df['CustomerDOB'] = pd.to_datetime(df['CustomerDOB'], errors='coerce')
df['TransactionDate'] = pd.to_datetime(df['TransactionDate'], errors='coerce')

# calculate customer age
df['CustomerAge'] = (pd.to_datetime('today') - df['CustomerDOB']).dt.days // 365


# categorize balance
def categorize_balance(balance):
    if balance < 5000:
        return 'Low'
    elif 5000 <= balance < 20000:
        return 'Medium'
    else:
        return 'High'


# apply "categorize balance" function to create a new column
df['BalanceCategory'] = df['CustAccountBalance'].apply(categorize_balance)


# categorize transaction
def categorize_transaction(amount):
    if amount > 100000:
        return 'Loan'
    elif 20000 <= amount <= 100000:
        return 'Investment'
    elif amount < 20000:
        return 'Deposit/Withdrawal'
    else:
        return 'Other'


# apply "categorize transaction" function to create a new column
df['TransactionType'] = df['TransactionAmount (INR)'].apply(categorize_transaction)

# extract transaction details
df['TransactionYear'] = df['TransactionDate'].dt.year
df['TransactionMonth'] = df['TransactionDate'].dt.month
df['TransactionDay'] = df['TransactionDate'].dt.day


# categorize age group
def categorize_age(age):
    if age < 25:
        return 'Young'
    elif 25 <= age < 50:
        return 'Middle-Aged'
    else:
        return 'Senior'


# apply "categorize age group" function to create a new column
df['AgeGroup'] = df['CustomerAge'].apply(categorize_age)

# to check new calculated columns
# print(df.head())

# streamlit app title
st.title('Bank Transactions Analisys')

# columns for grid layout
col1, col2 = st.columns(2)


# customer age distribution
with col1:
    st.header('Customer Age Distribution')
    plt.figure(figsize=(6, 4))
    sns.histplot(df['CustomerAge'], bins=20, kde=True, color='blue')
    plt.title('Customer Age Distribution')
    plt.xlabel('Age')
    plt.ylabel('Frequency')
    st.pyplot(plt)

# customer distribution by balance category
with col2:
    st.header('Customer Distribution by Balance Category')
    plt.figure(figsize=(6, 4))
    sns.countplot(data=df, x='BalanceCategory', palette='viridis')
    plt.title('Customer Distribution by Balance Category')
    plt.xlabel('Balance Category')
    plt.ylabel('Number of Customers')
    plt.grid(axis='y', alpha=0.3)
    st.pyplot(plt)

# another row of columns for the next set of charts
col3, col4 = st.columns(2)

# monthly transcation trends (line chart)
with col3:
    st.header('Monthly Transcations Amount Trends')
    monthly_data = df.groupby('TransactionMonth')['TransactionAmount (INR)'].sum()
    plt.figure(figsize=(8, 5))
    sns.lineplot(x=monthly_data.index, y=monthly_data.values, marker='o', color='green')
    plt.title('Monthly Transaction Amount Trends')
    plt.xlabel('Month')
    plt.ylabel('Total Transaction Amonut (INR)')
    plt.xticks(ticks=range(1, 13), labels=[
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ])
    plt.grid(alpha=0.3)
    st.pyplot(plt)

# transaction type distribution (pie chart)
with col4:
    st.header('Transaction Type Distribution')
    transaction_counts = df['TransactionType'].value_counts()
    plt.figure(figsize=(5, 5))
    colors = plt.cm.Pastel1(range(len(transaction_counts)))  # Pastel colormap
    wedges, texts, autotexts = plt.pie(transaction_counts,
                                       autopct='%1.1f%%',
                                       startangle=90,
                                       colors=colors)

    # add a legend
    plt.legend(wedges, transaction_counts.index, title='Transaction Types', loc='center left', bbox_to_anchor=(1, -.5))
    plt.title('Transaction Type Distribution')
    plt.tight_layout()
    st.pyplot(plt)

# monthly transcation amounts by type (heatmap)
st.header('Monthly Transaction Amounts by Type (Heatmap)')
heatmap_data = df.pivot_table(index='TransactionMonth', columns='TransactionType', values='TransactionAmount (INR)', aggfunc='sum', fill_value=0)
plt.figure(figsize=(8, 5))
sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlGnBu')
plt.title('Monthly Transaction Amounts by Type')
plt.xlabel('Transaction Type')
plt.ylabel('Month')
st.pyplot(plt)

# transaction amounts by type (interactive bar chart)
st.header('Transaction Amounts by Type (Interactive Bar Chart)')
fig = px.bar(df, x='TransactionType', y='TransactionAmount (INR)', color='TransactionType',
             title='Transaction Amonuts by Type')

# Set the size of the plotly chart for better fit
fig.update_layout(
    width=600,
    height=600,
    title='Transaction Amounts by Type'
)
st.plotly_chart(fig)
