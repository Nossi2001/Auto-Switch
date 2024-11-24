
def szyfr_cezara(tekst, klucz):
    alfabet = "AĄBCĆDEĘFGHIJKLŁMNŃOÓPRSŚTUWYZŹŻ"
    szyfrogram = ""
    for znak in tekst.upper():
        if znak in alfabet:
            indeks = (alfabet.index(znak) + klucz) % len(alfabet)
            szyfrogram += alfabet[indeks]
        else:
            szyfrogram += znak
    return szyfrogram


def deszyfruj_cezara(tekst, klucz):
    alfabet = "AĄBCĆDEĘFGHIJKLŁMNŃOÓPRSŚTUWYZŹŻ"
    tekst_jawny = ""
    for znak in tekst.upper():
        if znak in alfabet:
            indeks = (alfabet.index(znak) - klucz) % len(alfabet)
            tekst_jawny += alfabet[indeks]
        else:
            tekst_jawny += znak
    return tekst_jawny


def brute_force_cezara(tekst):
    alfabet = "AĄBCĆDEĘFGHIJKLŁMNŃOÓPRSŚTUWYZŹŻ"
    for klucz in range(len(alfabet)):
        odszyfrowany = ""
        for znak in tekst.upper():
            if znak in alfabet:
                indeks = (alfabet.index(znak) - klucz) % len(alfabet)
                odszyfrowany += alfabet[indeks]
            else:
                odszyfrowany += znak
        print(f"Klucz {klucz}: {odszyfrowany}")

def caesar_cipher(text, key):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ciphertext = ""
    for char in text.upper():
        if char in alphabet:
            index = (alphabet.index(char) + key) % len(alphabet)
            ciphertext += alphabet[index]
        else:
            ciphertext += char
    return ciphertext


def decrypt_caesar(text, key):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    plaintext = ""
    for char in text.upper():
        if char in alphabet:
            index = (alphabet.index(char) - key) % len(alphabet)
            plaintext += alphabet[index]
        else:
            plaintext += char
    return plaintext


def brute_force_caesar(text):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for key in range(len(alphabet)):
        decrypted = ""
        for char in text.upper():
            if char in alphabet:
                index = (alphabet.index(char) - key) % len(alphabet)
                decrypted += alphabet[index]
            else:
                decrypted += char
        print(f"Key {key}: {decrypted}")


# Example usage:

# plaintext = "BE STRONG, PROTECT YOUR REGIMENT AND SIX FLAGS."
# key = 0
# encrypted = caesar_cipher(plaintext, key)
# print(f"Encrypted text: {encrypted}")
#
# decrypted = decrypt_caesar(encrypted, key)
# print(f"Decrypted text with key {key}: {decrypted}")
#
# # Brute-force decryption
# ciphertext = encrypted
# print("\nBrute-force decryption attempts:")
# brute_force_caesar(ciphertext)


# tekst_jawny = "MĘżny bądź, chroń pułk twój i sześć flag."
# # klucz = 5
# # zaszyfrowany = szyfr_cezara(tekst_jawny, klucz)
# # print(f"Zaszyfrowany tekst : {zaszyfrowany}")
# # odszyfrowany = deszyfruj_cezara(zaszyfrowany,klucz)
# # print(f"Odszyfrowany teskt z kluczem: {odszyfrowany}")
#
# zaszyfrowany = "PJĆRĄ ĘEHC, FŁWŚS UŻÓŃ ŹATN M YBIZG KODL."
# brute_force_cezara(zaszyfrowany)