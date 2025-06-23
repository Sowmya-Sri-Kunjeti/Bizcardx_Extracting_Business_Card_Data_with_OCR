



import easyocr
import numpy as np
import pandas as pd
import re
from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu
import io
import sqlite3

def input_image_to_text(path):

  input_img = Image.open(path)

  input_img_np_array = np.array(input_img)

  reader = easyocr.Reader(['en'])
  text_result = reader.readtext(input_img_np_array, detail = 0)

  return text_result, input_img


def extracted_text_to_dict(sample_text):
  extracted_dict = {"NAME" : [], "DESIGNATION" : [], "COMPANY_NAME" : [], "CONTACT" : [], "EMAIL" : [], "WEBSITE" : [], "ADDRESS" : [],
                    "PINCODE" : []}


  extracted_dict["NAME"].append(sample_text[0])
  extracted_dict["DESIGNATION"].append( sample_text[1])

  for i in range(2, len(sample_text)):

    if "@" in sample_text[i] and ".com" in sample_text[i]:
      extracted_dict["EMAIL"].append( sample_text[i])

    elif "www" in sample_text[i].lower() or ".com" in sample_text[i]:
      extracted_dict["WEBSITE"].append( sample_text[i])

    elif (sample_text[i].startswith("+")) or ("-" in sample_text[i] and sample_text[i].replace("-", "").isdigit()):
      extracted_dict["CONTACT"].append( sample_text[i])

    elif ("Tamil Nadu" in sample_text[i] or "TamilNadu" in sample_text[i] or sample_text[i].isdigit() ) and ";" not in sample_text[i]:
      extracted_dict["PINCODE"].append( sample_text[i][-7:])

    elif re.match(r'^[A-Za-z]',sample_text[i]) and "." not in sample_text[i] and "," not in sample_text[i] :
      extracted_dict["COMPANY_NAME"].append(sample_text[i])

    else:
      remove_semicolon_and_comma = re.sub(r'[,;]', "" , sample_text[i])
      extracted_dict["ADDRESS"].append(remove_semicolon_and_comma)

  print(extracted_dict["ADDRESS"])

  if "TamilNadu" not in extracted_dict["ADDRESS"][0] and "Tamil Nadu" not in extracted_dict["ADDRESS"][0]:
    extracted_dict["ADDRESS"].append("TamilNadu")


  print(extracted_dict["ADDRESS"])

  for key, value in extracted_dict.items():
    if len(value) > 0:
      concatenate = " ".join(value)
      extracted_dict[key] = [concatenate]

    else:
      value = "NA"
      extracted_dict[key] = [value]

  return extracted_dict

# Streamlit section

st.set_page_config(layout = "wide")

st.markdown(
            """
            <style>
            .stApp {
              #background-color : #FFF5EE;
              background: linear-gradient(to top left, #ffccff 0%, #99ccff 100%)
                    }
            </style>
            """,
            unsafe_allow_html = True
)

st.title("             BIZCARDX : Extracting Business Card Data with OCR")

home_image = Image.open("/content/Screenshot 2025-06-10 185238.png")

with st.sidebar:

  selection = option_menu("Main Menu", ["Home", "Upload & Modify", "Delete"])

if selection == "Home":

  col1, col2 = st.columns(2)

  with col1 :
    st.image(home_image, use_container_width = False)


  with col2:
    st.write("")
    st.write("")
    st.markdown(
                """
                <p style = 'font-size : 16px'>
                <span style = 'color : blue ;'><strong> Technologies Used: </strong></span>
                <span style = 'color : black ;'> Python, easy OCR, Streamlit, SQL, Data Extraction </span>
                </p>
                """,
                unsafe_allow_html = True)

    st.markdown(
                """
                <span style = 'color : green ; '><strong> About : </strong></span>
                <span style = 'color : black ;'> Bizcard is an application designed to extract relevant information from Business cards. </span>
                """,
                unsafe_allow_html = True)

    st.markdown( '''
                <span style = 'color : black ;'>The main purpose of the Streamlit application is to allow users to upload an image of the business card
                                                and extract relevant information like Name, Designation, Company, Contact information etc.
                                                The power of Optical Character Recognition provided by easy OCR is leveraged to extract text from the image.
                                                The extracted information should then be displayed in the applications's GUI.
                                                In addition, users are allowed to save the extracted information into a database along with the uploaded
                                                business card image with the click of a button.
                                                It also allows the user to Read the data, Preview the data,Update the data and Delete the data as per the authentication 
                                                given to the user credentials.
                                                 </span>
                ''',
                unsafe_allow_html = True)

elif selection == "Upload & Modify":
  img = st.file_uploader("Upload an image", type = ["png", "jpg","jpeg"])

  if img is not None:
    st.image(img, width = 300)
    text_img , inp_img = input_image_to_text(img)

    text_img_dict = extracted_text_to_dict(text_img)

    if text_img_dict:
      st.success("Text from the input image is extracted successfully")

    text_img_dict_to_df = pd.DataFrame(text_img_dict)

    # Conversion of an image into bytes format.

    img_bytes = io.BytesIO()
    inp_img.save(img_bytes, format = "PNG")
    image_data = img_bytes.getvalue()

    # Converting bytes into a dictionary

    data = {'IMAGE':[image_data]}

    # converting the above dictionary into a data frame.

    image_df = pd.DataFrame(data)
    total_df = pd.concat([text_img_dict_to_df, image_df], axis = 1)

    st.dataframe(total_df)

    button_1 = st.button("Save to Database", use_container_width = True)

    if button_1:

      mydb = sqlite3.connect("bizcard.db")
      mycursor = mydb.cursor()

      # Creation of required tables in the database.
      create_table_query = '''CREATE TABLE IF NOT EXISTS bizcard_details (name varchar(200),
                                                                            designation varchar(200),
                                                                            company_name varchar(250),
                                                                            contact varchar(225),
                                                                            email varchar(225),
                                                                            website varchar(225),
                                                                            address varchar(500),
                                                                            pincode int,
                                                                            image text)'''

      mycursor.execute(create_table_query)
      mydb.commit()

      # Inserting values into the table created.


      insert_table_query = ''' INSERT INTO bizcard_details (name, designation, company_name, contact, email, website, address, pincode, image)
                                              VALUES ( ? , ? , ? , ? , ? , ? , ? , ? , ? )'''

      insert_data = total_df.values.tolist()[0]
      mycursor.execute(insert_table_query, insert_data)
      mydb.commit()

      st.success("Saved to database successfully")

  method = st.radio("Select the Method", ["None" , "Preview" , "Modify"], index = 0)

  if method == "None":
    st.write("")

  if img and method == "Preview":

    mydb = sqlite3.connect("bizcard.db")
    mycursor = mydb.cursor()
    select_query = " SELECT * FROM bizcard_details "

    mycursor.execute(select_query)
    result = mycursor.fetchall()
    mydb.commit()

    result_df = pd.DataFrame(result, columns = ("NAME" , "DESIGNATION" , "COMPANY_NAME" , "CONTACT" , "EMAIL" , "WEBSITE" , "ADDRESS" , "PINCODE" , "IMAGE"))
    st.dataframe(result_df)


  elif method == "Modify":

    user_name = st.text_input("Enter the user name to proceed")
    password = st.text_input("Enter the password to proceed")

    if user_name and password:

      if user_name == "sowmya" and password == "sowmya":


        mydb = sqlite3.connect("bizcard.db")
        mycursor = mydb.cursor()
        select_query = " SELECT * FROM bizcard_details "

        mycursor.execute(select_query)
        result = mycursor.fetchall()
        mydb.commit()

        result_df = pd.DataFrame(result, columns = ("NAME" , "DESIGNATION" , "COMPANY_NAME" , "CONTACT" , "EMAIL" , "WEBSITE" , "ADDRESS" , "PINCODE" , "IMAGE"))

        col1, col2 = st.columns(2)
        with col1:

          selected_name = st.selectbox("Select the name", result_df["NAME"])

        df_3 = result_df[result_df["NAME"] == selected_name]



        df_4 = df_3.copy()



        col1, col2 = st.columns(2)
        with col1:
          mo_name = st.text_input("Enter the name to be modified as", df_3["NAME"].unique()[0])
          mo_designation = st.text_input("Enter the designation to be modified as", df_3["DESIGNATION"].unique()[0])
          mo_company_name = st.text_input("Enter the company name to be modified as", df_3["COMPANY_NAME"].unique()[0])
          mo_contact = st.text_input("Enter the contact to be modified as", df_3["CONTACT"].unique()[0])
          mo_email = st.text_input("Enter the email to be modified as", df_3["EMAIL"].unique()[0])

          df_4["NAME"] = mo_name
          df_4["DESIGNATION"] = mo_designation
          df_4["COMPANY_NAME"] = mo_company_name
          df_4["CONTACT"] = mo_contact
          df_4["EMAIL"] = mo_email

        with col2:
          mo_website = st.text_input("Enter the website to be modified as", df_3["WEBSITE"].unique()[0])
          mo_address = st.text_input("Enter the address to be modified as", df_3["ADDRESS"].unique()[0])
          mo_pincode = st.text_input("Enter the pincode to be modified as", df_3["PINCODE"].unique()[0])
          # mo_image = st.text_input("Enter the image to be modified as", df_3["IMAGE"].unique()[0])

          df_4["WEBSITE"] = mo_website
          df_4["ADDRESS"] = mo_address
          df_4["PINCODE"] = mo_pincode
          #df_4["IMAGE"] = mo_image

        col1, col2 = st.columns(2)

        with col1:
          button_3 = st.button("Modify the details in Database", use_container_width = True)

          if button_3:
            mydb = sqlite3.connect("bizcard.db")
            mycursor = mydb.cursor()

            mycursor.execute(f"DELETE FROM bizcard_details WHERE NAME = '{selected_name}'")
            mydb.commit()

            insert_table_query = ''' INSERT INTO bizcard_details (name, designation, company_name, contact, email, website, address, pincode, image)
                                                  VALUES ( ? , ? , ? , ? , ? , ? , ? , ? , ? )'''

            insert_data = df_4.values.tolist()[0]
            mycursor.execute(insert_table_query, insert_data)
            mydb.commit()

            st.success("Database is updated successfully")

      else:
        st.write("The credentials entered are incorrect")



elif selection == "Delete":

  mydb = sqlite3.connect("bizcard.db")
  mycursor = mydb.cursor()

  col1, col2 = st.columns(2)

  with col1:

    select_query = "SELECT NAME FROM bizcard_details"

    mycursor.execute(select_query)
    result_1 = mycursor.fetchall()
    mydb.commit()

    names = []

    for i in result_1:
      names.append(i[0])

    name_select = st.selectbox("Select the name", names)

  with col2:

    select_query = f"SELECT DESIGNATION FROM bizcard_details WHERE NAME = '{name_select}'"

    mycursor.execute(select_query)
    result_2 = mycursor.fetchall()
    mydb.commit()

    designations = []

    for i in result_2:
      designations.append(i[0])

    designation_select = st.selectbox("Select the designation", designations)


  if name_select and designation_select:
    col1, col2, col3 = st.columns(3)

    with col1:
      st.write(f"Selected Name : {name_select}")
      st.write("")
      st.write(f"Selected Designation : {designation_select}")

    with col2:
      st.write("")
      st.write("")
      st.write("")
      st.write("")

      remove = st.button("Click to Delete", use_container_width = True)

      if remove:
        mycursor.execute(f"DELETE FROM bizcard_details WHERE NAME = '{name_select}' AND DESIGNATION = '{designation_select}'")
        mydb.commit()

        st.warning("Data is deleted successfully")

