import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

merge_df = pd.read_csv('merge_df.csv')

# Repeat Purchase Rate
repeat_purchases = merge_df.groupby(['customer_id', 'product_category_name_english']).size().reset_index(name='purchase_count')
repeat_purchases = repeat_purchases[repeat_purchases['purchase_count'] > 1]
repeat_purchases.sort_values(by='purchase_count', ascending=False)
repeat_purchase_rate = repeat_purchases.groupby('product_category_name_english')['customer_id'].nunique().reset_index()
total_customers = merge_df.groupby('product_category_name_english')['customer_id'].nunique().reset_index()
repeat_purchase_rate = repeat_purchase_rate.merge(total_customers, on='product_category_name_english', suffixes=('_repeat', '_total'))
repeat_purchase_rate['repeat_purchase_rate'] = repeat_purchase_rate['customer_id_repeat'] / repeat_purchase_rate['customer_id_total'] 
repeat_purchase_rate = repeat_purchase_rate.sort_values(by='repeat_purchase_rate', ascending=False) 

# Average Review Score
average_review_score = merge_df.groupby('product_category_name_english')['review_score'].mean().reset_index()
average_review_score.columns = ['Product Category', 'Average Review Score']

# 2 Columns Layout
col1, col2 = st.columns(2)

# Buttons untuk menampilkan data terbaik dan terburuk
with col1:
    show_best = st.button('Show Top 10 Best Product Categories')

with col2:
    show_worst = st.button('Show Top 10 Worst Product Categories')

# Menentukan data yang akan ditampilkan
if show_best:
    top_10_repeat = repeat_purchase_rate.sort_values(by='repeat_purchase_rate', ascending=False).head(10)
    top_10_review = average_review_score.sort_values(by='Average Review Score', ascending=False).head(10)
    st.title('Top 10 Best Product Categories')
else:
    top_10_repeat = repeat_purchase_rate.sort_values(by='repeat_purchase_rate', ascending=True).head(10)
    top_10_review = average_review_score.sort_values(by='Average Review Score', ascending=True).head(10)
    st.title('Top 10 Worst Product Categories')


# Plot Repeat Purchase Rate
fig, ax = plt.subplots(figsize=(12, 8))
ax.barh(top_10_repeat['product_category_name_english'], top_10_repeat['repeat_purchase_rate'], color='skyblue')
ax.set_xlabel('Repeat Purchase Rate')
ax.set_ylabel('Product Category')
ax.set_title('Repeat Purchase Rate')
ax.invert_yaxis()
st.pyplot(fig)

# Plot Average Review Score
fig, ax = plt.subplots(figsize=(12, 8))
ax.barh(top_10_review['Product Category'], top_10_review['Average Review Score'], color='lightgreen')
ax.set_xlabel('Average Review Score')
ax.set_ylabel('Product Category')
ax.set_title('Average Review Score')
ax.invert_yaxis()
st.pyplot(fig)

# Melakukan RFM Analisis untuk customer yang melakukan repeat purchase
# Menghitung Frekuensi pembelian
repeat_purchases = merge_df.groupby(['customer_id', 'product_category_name_english']).size().reset_index(name='purchase_count')
repeat_purchases = repeat_purchases[repeat_purchases['purchase_count'] > 1]
repeat_purchases = repeat_purchases.sort_values(by='purchase_count', ascending=False)
rfm_df = repeat_purchases.groupby('customer_id')['purchase_count'].sum().reset_index()
rfm_df.columns = ['customer_id', 'Frequency']

# Mengklasifikasi customer berdasarkan frekuensi pembelian
rfm_df['Class'] = pd.cut(
    rfm_df['Frequency'],
    bins=[0, 3, 8, 20, rfm_df['Frequency'].max()],
    labels=['Class1', 'Class2', 'Class3', 'Class4']
)

# Menghitung jumlah customer di setiap kelas
class_counts = rfm_df['Class'].value_counts().reset_index()
class_counts.columns = ['Class', 'Count']

# Display tabel jumlah customer di setiap kelas
st.subheader('Customer Class Counts')
st.table(class_counts)

# Membuat search bar untuk mencari kelas customer berdasarkan customer ID
st.subheader('Search Customer Class')
customer_id_input = st.text_input('Enter Customer ID: (Example: 270c23a11d024a44c896d1894b261a83)', '')

if customer_id_input:
    customer_info = rfm_df[rfm_df['customer_id'] == customer_id_input]
    if not customer_info.empty:
        customer_class = customer_info['Class'].values[0]
        customer_freq = customer_info['Frequency'].values[0]
        
        # Menampilkan produk yang dibeli customer berulang kali
        customer_purchases = repeat_purchases[repeat_purchases['customer_id'] == customer_id_input]
        
        st.write(f'Customer ID **{customer_id_input}** is in **{customer_class}** based on repeat purchases of **{customer_freq}** times.')
        
        if not customer_purchases.empty:
            st.write('**Repeatedly Purchased Products:**')
            st.table(customer_purchases[['product_category_name_english', 'purchase_count']].rename(columns={
                'product_category_name_english': 'Product Category',
                'purchase_count': 'Purchase Count'
            }))
        else:
            st.write('No repeated purchases found for this customer.')
    else:
        st.write('Customer ID not found.')