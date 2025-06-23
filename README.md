# BizCardX: Extracting Business Card Data with OCR
Bizcard is a Streamlit web application that allows users to upload Business card images, extract text data from them using OCR, and interact with the extracted data through a user-friendly GUI. It offers features to
review, modify and delete the stored information - all based on user authentication.

## Features

- Upload Business card images
- Extract text using easy OCR
- Store extracted text in SQLite
- Preview extracted information
- Modify and delete data as per the rquirement ( with authentication )

  ## Technologies Used

  - Python
  - easyOCR
  - Pandas
  - SQLite
  - Streamlit
 
  ## Install dependencies

  ! pip install easyocr
  ! pip install streamlit
  ! pip install streamlit_option_menu
  ! pip install numpy

  ## Usage

  - Launch the streamlit app : streamlit run app.py
  - Upload a Business card image
  - Extracted details will be displayed.
    User can
        . Save data to SQLite
        . Preview the data using 'Preview' option
        . Modify or Delete entries based on the authentication.
    
  
    
