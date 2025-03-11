import re
from spellchecker import SpellChecker

def clean_and_correct_text(text):
    """
    Clean and correct spelling in a given text.
    
    Args:
        text (str): Input text with potential spelling errors
        
    Returns:
        tuple: (cleaned_text, corrected_text)
    """
    # Original text for reference
    print("Original Text:", text)
    
    # Basic text cleanup
    cleaned_text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Remove special characters
    cleaned_text = cleaned_text.lower()  # Normalize case
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()  # Handle multiple spaces and trim
    
    # Spell checking
    spell = SpellChecker()
    
    # Find misspelled words
    words = cleaned_text.split()
    misspelled = spell.unknown(words)
    
    # Print misspelled words and their corrections
    if misspelled:
        print("\nMisspelled words found:")
        for word in misspelled:
            correction = spell.correction(word)
            print(f"  {word} -> {correction}")
    
    # Apply corrections to all words
    corrected_words = []
    for word in words:
        if word in misspelled:
            corrected_words.append(spell.correction(word))
        else:
            corrected_words.append(word)
    
    corrected_text = " ".join(corrected_words)
    
    return cleaned_text, corrected_text

# Example usage
if __name__ == "__main__":
    sample_text = "Ths is an exmple of a noisyy sentence with errrs."
    cleaned, corrected = clean_and_correct_text(sample_text)
    
    print("\nCleaned Text:", cleaned)
    print("Corrected Text:", corrected)
    
    # Try with another example
    print("\n--- Another Example ---")
    another_text = "Artficial intellgence is changin how we interct with technlogy."
    cleaned2, corrected2 = clean_and_correct_text(another_text)
    
    print("\nCleaned Text:", cleaned2)
    print("Corrected Text:", corrected2)



# (myenv) harish $ python noisy_text_handling.py 
# Original Text: Ths is an exmple of a noisyy sentence with errrs.

# Misspelled words found:
#   errrs -> errors
#   exmple -> example
#   noisyy -> noisy
#   ths -> the

# Cleaned Text: ths is an exmple of a noisyy sentence with errrs
# Corrected Text: the is an example of a noisy sentence with errors

# --- Another Example ---
# Original Text: Artficial intellgence is changin how we interct with technlogy.

# Misspelled words found:
#   changin -> changing
#   interct -> interact
#   technlogy -> technology
#   artficial -> artificial
#   intellgence -> intelligence

# Cleaned Text: artficial intellgence is changin how we interct with technlogy
# Corrected Text: artificial intelligence is changing how we interact with technology