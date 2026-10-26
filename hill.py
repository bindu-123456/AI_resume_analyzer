import numpy as np

def encrypt(text, key):
    text = text.upper().replace(" ", "")

    if len(text) % 2 != 0:
        text += 'X'

    result = ""

    for i in range(0, len(text), 2):
        a = ord(text[i]) - ord('A')
        b = ord(text[i + 1]) - ord('A')

        c1 = (key[0][0] * a + key[0][1] * b) % 26
        c2 = (key[1][0] * a + key[1][1] * b) % 26

        result += chr(c1 + ord('A'))
        result += chr(c2 + ord('A'))

    return result


def decrypt(cipher, key):
    det = int(round(np.linalg.det(key)))
    det = det % 26

    det_inv = None

    for i in range(26):
        if (det * i) % 26 == 1:
            det_inv = i
            break

    if det_inv is None:
        return "Decryption is not possible with this key."

    adj = np.array([
        [key[1][1], -key[0][1]],
        [-key[1][0], key[0][0]]
    ])

    inverse_key = (det_inv * adj) % 26
    inverse_key = inverse_key.astype(int)

    result = ""

    for i in range(0, len(cipher), 2):
        a = ord(cipher[i]) - ord('A')
        b = ord(cipher[i + 1]) - ord('A')

        p1 = (inverse_key[0][0] * a +
              inverse_key[0][1] * b) % 26

        p2 = (inverse_key[1][0] * a +
              inverse_key[1][1] * b) % 26

        result += chr(p1 + ord('A'))
        result += chr(p2 + ord('A'))

    return result


key = np.array([[3, 3], [2, 5]])

plaintext = input("Enter plaintext: ").upper().replace(" ", "")

ciphertext = encrypt(plaintext, key)
print("Encrypted text:", ciphertext)

decrypted_text = decrypt(ciphertext, key)
print("Decrypted text:", decrypted_text)