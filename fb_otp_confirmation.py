def validate_otp(otp_code):
    if len(otp_code) < 5:
        return "Invalid OTP. Please enter a 5 digit OTP."
    # ... Additional validation logic ...
    return "OTP is valid."

# Example prompt
otp_code = input("Please enter your OTP (5 digit): ")
validation_result = validate_otp(otp_code)
print(validation_result)