import streamlit as st
import cv2
import os
import numpy as np
import mysql.connector
import pandas as pd
from gtts import gTTS
import pygame
import time
import os
from datetime import date 
from datetime import datetime
from deepface import DeepFace
import plotly.graph_objects as go


# --- CONFIGURATION ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'retail'
}

FACE_IMAGE_FOLDER = "face_images"

st.set_page_config(layout="wide", page_title="Retail360", page_icon="🛍️")

# --- DATABASE CONNECTION ---
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# --- CAPTURE FACE ---
def capture_face():
    cap = cv2.VideoCapture(0)
    captured = False
    image_path = None

    st.info("Press 's' to capture the image")
    while not captured:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to grab frame")
            break

        cv2.imshow("Press 's' to capture", frame)
        key = cv2.waitKey(1)
        if key == ord('s'):
            image_path = os.path.join(FACE_IMAGE_FOLDER, "captured_face.jpg")
            cv2.imwrite(image_path, frame)
            captured = True
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return image_path

# --- MATCH FACE ---
def match_face(uploaded_face_path):
    for filename in os.listdir(FACE_IMAGE_FOLDER):
        db_image_path = os.path.join(FACE_IMAGE_FOLDER, filename)
        try:
            result = DeepFace.verify(uploaded_face_path, db_image_path, enforce_detection=False)
            if result['verified']:
                return int(filename.split('_')[0])
        except Exception as e:
            print(f"Error comparing faces: {e}")
    return None

def greet_with_voice(text):
    tts = gTTS(text=text, lang='en')
    filename = "welcome.mp3"
    tts.save(filename)

    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Wait for audio to finish
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.quit()
    os.remove(filename)

# --- SHOW CUSTOMER INFO ---
def show_customer_info(customer_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch customer profile
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
    customer = cursor.fetchone()

    if not customer:
        st.error("Customer not found.")
        return

    #st.success(f"👋 Welcome {customer['first_name']}! Check out our new arrivals.")
    # Prepare and display message
    welcome_msg = f"👋 Welcome {customer['first_name']}! Check out our new arrivals."
    st.success(welcome_msg)
    
    # Voice greet the message
    greet_with_voice(f"Welcome {customer['first_name']}, check out our new arrivals!")

    # Customer Profile Header
    st.markdown("""
        <div style="background-color: #f0f8ff; padding: 12px 20px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="text-align:center;">🎯 Customer Profile</h2>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        image_path = os.path.join(FACE_IMAGE_FOLDER, f"{customer_id}_face.jpg")
        st.image(image_path, width=220)
        st.markdown(f"<h5 style='text-align:center; margin-top:10px;'>{customer['first_name']}</h5>", unsafe_allow_html=True)

    with col2:
        left, right = st.columns(2)
        with left:
            st.markdown(f"**Customer ID:** {customer['customer_id']}")
            st.markdown(f"**Last Name:** {customer.get('last_name', '-')}")
            st.markdown(f"**Email:** [{customer['email']}](mailto:{customer['email']})")
            st.markdown(f"**DOB:** {customer['date_of_birth']}")
            st.markdown(f"**City:** {customer['city']}")
            st.markdown(f"**ZIP:** {customer.get('zip_code', '-')}")
            st.markdown(f"**Registered On:** {customer.get('registration_date', '-')}")

        with right:
            st.markdown(f"**First Name:** {customer['first_name']}")
            st.markdown(f"**Gender:** {customer['gender']}")
            st.markdown(f"**Phone:** {customer['phone_number']}")
            st.markdown(f"**Address:** {customer.get('address', '-')}")
            st.markdown(f"**State:** {customer.get('state', '-')}")
            st.markdown(f"**Country:** {customer.get('country', '-')}")
            st.markdown(f"**Loyalty Tier:** {customer.get('loyalty_tier', 'N/A')}")

    # Recent Purchases
    st.markdown("""
        <div style="background-color: #f0f8ff; padding: 12px 20px; border-radius: 10px; margin-top: 30px; margin-bottom: 10px;">
            <h2 style="text-align:center;">🛍️ Recent Purchases</h2>
        </div>
    """, unsafe_allow_html=True)

    cursor.execute("""
        SELECT product_name, category, total_amount, purchase_date 
        FROM purchases_data_model 
        WHERE customer_id = %s 
        ORDER BY purchase_date DESC 
        LIMIT 5
    """, (customer_id,))
    df_purchases = pd.DataFrame(cursor.fetchall())
    if not df_purchases.empty:
        st.dataframe(df_purchases)
    else:
        st.info("No purchases yet.")

    # Personalized Offers
    st.markdown("""
        <div style="background-color: #f0f8ff; padding: 12px 20px; border-radius: 10px; margin-top: 30px; margin-bottom: 10px;">
            <h2 style="text-align:center;">🎁 Personalized Offers</h2>
        </div>
    """, unsafe_allow_html=True)

    if df_purchases.empty:
        st.write("No recent purchase categories to match offers with.")
    else:
        if 'category' in df_purchases.columns:
            last_categories = df_purchases['category'].unique().tolist()
            if last_categories:
                placeholders = ','.join(['%s'] * len(last_categories))
                query = f"""
                    SELECT offer_title, category, discount_percent, valid_till 
                    FROM offers 
                    WHERE category IN ({placeholders})
                    AND valid_till >= CURDATE()
                    ORDER BY valid_till DESC
                    LIMIT 5
                """
                cursor.execute(query, tuple(last_categories))
                rows = cursor.fetchall()
                if rows:
                    df_offers = pd.DataFrame(rows)
                    st.dataframe(df_offers)
                else:
                    st.write("No personalized offers found for your recent purchases.")
            else:
                st.write("No recent purchase categories to match offers with.")
        else:
            st.write("Category information not available in purchase data.")


    # Purchase Insights
    st.markdown("""
        <div style="background-color: #f0f8ff; padding: 12px 20px; border-radius: 10px; margin-top: 30px; margin-bottom: 10px;">
            <h2 style="text-align:center;">📈 Purchase Insights</h2>
        </div>
    """, unsafe_allow_html=True)

    col_graph1, col_graph2 = st.columns(2)

    with col_graph1:
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM purchases_data_model 
            WHERE customer_id = %s 
            GROUP BY category
        """, (customer_id,))
        df_category = pd.DataFrame(cursor.fetchall())
        if not df_category.empty:
            fig_bar = go.Figure(data=[
            go.Bar(
                x=df_category['category'],
                y=df_category['count'],
                marker_color='indianred'
            )
            ])
            fig_bar.update_layout(
                title="Purchase Frequency by Category",
                xaxis_title="Product Category",
                yaxis_title="Number of Purchases",
                template='plotly_white'
            )
            st.plotly_chart(fig_bar)

        else:
            st.info("No category-wise data available.")

    with col_graph2:
        cursor.execute("SELECT SUM(total_amount) as total_spent FROM purchases_data_model WHERE customer_id = %s", (customer_id,))
        total_spent = cursor.fetchone()['total_spent'] or 0
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_spent,
            title={'text': "Total Customer Spend"},
            gauge={
                'axis': {'range': [None, 60000]},
                'bar': {'color': "green"},
            },
            number={'prefix': "₹", 'valueformat': ".1f"}
        ))
        st.plotly_chart(fig)

    conn.close()

# --- REGISTER NEW CUSTOMER ---
def register_customer(captured_image_path):
    st.warning("Face not recognized. Please register.")
    with st.form("registration_form"):
        firstname = st.text_input("First Name")
        lastname = st.text_input("Last Name")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        dob = st.date_input("Date of Birth", min_value=datetime(1900, 7, 24), max_value=datetime(2025, 7, 24))
        city = st.text_input("City")
        state = st.text_input("State")
        zipcode = st.text_input("Zip Code")
        country = st.text_input("Country")
        email = st.text_input("Email")
        phone_number = st.text_input("Phone")
        submitted = st.form_submit_button("Register")

    if submitted:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customers (first_name, last_name, gender, date_of_birth, city, state, zip_code, country, email, phone_number, registration_date, image_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, '')
        """, (firstname, lastname, gender, dob, city, state, zipcode, country, email, phone_number, date.today()))
        conn.commit()
        new_id = cursor.lastrowid

        new_filename = f"{new_id}_face.jpg"
        new_relative_path = os.path.join("face_images", new_filename)  # This goes into DB
        new_absolute_path = os.path.join(FACE_IMAGE_FOLDER, new_filename)
        os.rename(captured_image_path, new_absolute_path)
        cursor.execute("UPDATE customers SET image_path = %s WHERE customer_id = %s", (new_relative_path, new_id))
        conn.commit()
        conn.close()

        st.success("Registration successful! Please restart app to recognize.")

# --- MAIN ---
def main():
    st.markdown("""
        <div style="background-color: #f0f8ff; padding: 12px 20px; border-radius: 10px; margin-bottom: 20px;">
            <h1 style="text-align:center;font-weight:bold;">🛍️ Retail360.AI: Autonomous Retail Experience</h1>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <h3 style="text-align:center;">Smart Entry with Face Recognition</h3>
    """, unsafe_allow_html=True)
    if 'captured' not in st.session_state:
        if st.button("📷 Capture Face"):
            image_path = capture_face()
            if image_path:
                st.session_state['captured'] = image_path

    if 'captured' in st.session_state:
        st.image(st.session_state['captured'], caption="Captured Face", width=300)
        if st.button("🗑️ Clear Image"):
            del st.session_state['captured']
            st.rerun()
        else:
            matched_id = match_face(st.session_state['captured'])
            if matched_id:
                show_customer_info(matched_id)
            else:
                register_customer(st.session_state['captured'])

if __name__ == "__main__":
    os.makedirs(FACE_IMAGE_FOLDER, exist_ok=True)
    main()
