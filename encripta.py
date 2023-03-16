import base64
from cryptography.fernet import Fernet

# dados criptografados
data = {"content": "725cd5204cf64987a39a6622884527e0", "iv": "e6174b11cd2a18fc", "tag": {"data": [26, 91, 205, 206, 134, 22, 167, 101, 110, 27, 155, 100, 41, 99, 34, 135], "type": "Buffer"}}

# chave de criptografia (32 bytes)
password = b'SqqUUMnwEVUCBYT7p/0Zfz4Cq2eazHqQ'
kdf = Fernet.generate_key()
key = Fernet(base64.urlsafe_b64encode(kdf))

# decodificar o IV e o conteúdo criptografado
iv = bytes.fromhex(data['iv'])
content = base64.b16decode(data['content'])

# criar um objeto Fernet com a chave
fernet = Fernet(key)

# descriptografar o conteúdo
decrypted_data = fernet.decrypt(content)

# converter dados para texto
decoded_data = decrypted_data.decode('utf-8')

print(decoded_data)


