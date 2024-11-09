import smtplib
import serial
import os
import json
import shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from deepface import DeepFace

# Initialize serial communication on COM1 with baud rate 9600
s = serial.Serial('COM1',9600)

# List of authorized target images
target_images = ["nayana.jpg","alan.jpg","nebu.jpg"]

# Variable to track if detection occurred
Detection=False

# Setup port number and server name
smtp_port = 587                 # Standard secure SMTP port
smtp_server = "smtp.gmail.com"  # Google SMTP Server

# Sender and receiver email addresses
email_from = "lockersender@gmail.com"
email_to = "lockerreceiver@gmail.com"

# Application-specific password for email sender
pswd = "jreesysnmnvqbfsr" 

# Email subject
subject = "Theft Detected!!!"

# Function to send email with an image attachment 
def send_emails(email_to):

        # Email body content
        body = f"""
        Theft Detected before Smart Locker
        Theft Image Attatched!
        """

        # Create MIME object for email content
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = email_to
        msg['Subject'] = subject

        # Attach the email body to the MIME object
        msg.attach(MIMEText(body, 'plain'))

        # Define the image filename(captured image) to attach
        filename = "image_selected.jpg"

        # Open the image file in binary mode
        attachment= open(filename, 'rb')  

        # Encode attachment as base64
        attachment_package = MIMEBase('application', 'octet-stream')
        attachment_package.set_payload((attachment).read())
        encoders.encode_base64(attachment_package)
        attachment_package.add_header('Content-Disposition', "attachment; filename= " + filename)
        msg.attach(attachment_package)

        # Convert message to string format
        text = msg.as_string()

        # Connect to the SMTP server
        print("Connecting to server...")
        TIE_server = smtplib.SMTP(smtp_server, smtp_port)
        TIE_server.starttls() # Start TLS for security
        TIE_server.login(email_from, pswd) # Log in to the email server
        print("Succesfully connected to server")
        print()

        # Send email to the specified recipient
        print(f"Sending email to: {email_to}...")
        TIE_server.sendmail(email_from, email_to, text)
        print(f"Email sent to: {email_to}")
        print()

        # Close the SMTP server connection
        TIE_server.quit()

# Function to compare captured image with target images using DeepFace
def compare_images(img1_path, img2_path):
    try:
        # Perform facial verification using DeepFace
        result = DeepFace.verify(
            img1_path=img1_path,
            img2_path=img2_path,
            model_name="Facenet",
        )
        Detection=True # Set detection flag to True if any face is detected
    except ValueError as e:
        # Handle error if face is not detected properly    
        print(f"Face not detected properly: {e}")
        Detection=False # Set detection flag to False
        
    if Detection:
        print(json.dumps(result, indent=2)) # Print verification result in JSON format
        if result['verified']:
            print("The person is not a Theft.")
            return "Match"
        else:
            return "Not Match"
    else:
        return "Failed"
        
# Infinite loop to keep checking for locker access requests            
while True:
      print("Smart Locker System")
      serial_data = s.read() # Read serial data

      # If signal indicating an image is captured is received
      if(serial_data == b'a'):
          # Define the root path where captured image is stored
          root_path = r"C:\Users\HP\AppData\Local\Temp\VSM Studio"
          image_file = None # Initialize variable to hold image file path

          # Search for the captured image in the specified directory
          for root, dirs, files in os.walk(root_path):
              for file in files:
                  if file == 'image00000.jpg':
                      image_file = os.path.join(root, file)
                      break
              if image_file:
                  break

          # Copy the captured image to a new location for comparison      
          if image_file:
              source_image = r"C:\Users\HP\image_selected.jpg"
              shutil.copy(image_file, source_image)
              
          # Compare the captured image with each target image
          for target_image in target_images:
              status=compare_images(source_image, target_image)
              if status=="Match":
                  s.write(b'b') # Send confirmation signal to indicate a face is detected
                  s.write(b'c') # Send confirmation signal to unlock locker
                  break
              if status=="Failed":
                  s.write(b'd') # Send signal indicating failure in detecting a face
                  break
             
          # If no match is found
          if status=="Not Match":            
              s.write(b'b') # Send confirmation signal to indicate a face is detected
              s.write(b'e') # Send signal indicating potential theft
              print("Theft detected sending image on mail")
              send_emails(email_to) # Call function to send email alert

        
        
     
        
 
