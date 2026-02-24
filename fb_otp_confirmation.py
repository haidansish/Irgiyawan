# OTP Confirmation

# other import statements...


def validate_otp(otp_code):
    # Change length check from 6 to 5
    return len(otp_code) == 5


def prompt_for_otp():
    otp_code = input("Kode Verifikasi (5 digit): ")  # Update prompt message
    if not validate_otp(otp_code):
        print("OTP is not valid!")
        return None
    return otp_code

# other code in the file...
