import email
from email import policy
from pathlib import Path
import PyPDF2
import os

def read_pdf_content(pdf_path):
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def read_msg_file(file_path):
    # Create attachments directory if it doesn't exist
    Path("attachments").mkdir(exist_ok=True)
    
    # Open the MSG file
    msg = extract_msg.Message(file_path)
    
    # Print email details
    print("\n=== Email Contents ===")
    print(f"Subject: {msg.subject}")
    print(f"From: {msg.sender}")
    print(f"To: {msg.to}")
    print(f"Date: {msg.date}")
    print("\n=== Email Body ===")
    print(msg.body)
    
    # Handle attachments
    if msg.attachments:
        print("\n=== Attachments ===")
        for attachment in msg.attachments:
            filename = attachment.getFilename()
            print(f"Found attachment: {filename}")
            
            # Save attachment to the attachments folder
            attachment_path = Path("attachments") / filename
            with open(attachment_path, "wb") as f:
                f.write(attachment.data)
            print(f"Saved attachment to: {attachment_path}")
            
            # If attachment is PDF, read and print its content
            if filename.lower().endswith('.pdf'):
                print(f"\n=== PDF Content: {filename} ===")
                pdf_content = read_pdf_content(attachment_path)
                print(pdf_content)
    else:
        print("\nNo attachments found.")
    
    msg.close()

def read_eml_file(file_path):
    # Create attachments directory if it doesn't exist
    Path("attachments").mkdir(exist_ok=True)
    
    # Open and parse the EML file
    with open(file_path, 'rb') as f:
        msg = email.message_from_binary_file(f, policy=policy.default)
    
    # Print email details
    print("\n=== Email Contents ===")
    print(f"Subject: {msg['subject']}")
    print(f"From: {msg['from']}")
    print(f"To: {msg['to']}")
    print(f"Date: {msg['date']}")
    
    # Handle body and attachments
    for part in msg.walk():
        if part.get_content_maintype() == 'text' and part.get_content_subtype() == 'plain':
            print("\n=== Email Body ===")
            print(part.get_content())
            
        elif part.get_content_disposition() == 'attachment':
            filename = part.get_filename()
            if filename:
                print(f"\nFound attachment: {filename}")
                
                # Save attachment to the attachments folder
                attachment_path = Path("attachments") / filename
                with open(attachment_path, "wb") as f:
                    f.write(part.get_payload(decode=True))
                print(f"Saved attachment to: {attachment_path}")
                
                # If attachment is PDF, read and print its content
                if filename.lower().endswith('.pdf'):
                    print(f"\n=== PDF Content: {filename} ===")
                    pdf_content = read_pdf_content(attachment_path)
                    print(pdf_content)

if __name__ == "__main__":
    # Specify the path to your MSG file
    msg_file = "test email.msg"
    
    try:
        read_msg_file(msg_file)
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Specify the path to your EML file
    eml_file = "test email.eml"
    
    try:
        read_eml_file(eml_file)
    except Exception as e:
        print(f"Error: {str(e)}")