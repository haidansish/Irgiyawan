def extract_tokens_from_page(page_content):
    import re
    # Properly escaping backslashes in the regex pattern
    pattern = r'\\d+'  # Example of escaping, adjust accordingly based on actual usage
    tokens = re.findall(pattern, page_content)
    return tokens
