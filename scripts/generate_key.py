from cryptography.fernet import Fernet
import os

def generate_encryption_key():
    # Generate a new Fernet key
    key = Fernet.generate_key()
    
    # Read existing .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    env_contents = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_contents = f.readlines()
    
    # Update or add ENCRYPTION_KEY
    key_found = False
    for i, line in enumerate(env_contents):
        if line.startswith('ENCRYPTION_KEY='):
            env_contents[i] = f'ENCRYPTION_KEY={key.decode()}\n'
            key_found = True
            break
    if not key_found:
        env_contents.append(f'ENCRYPTION_KEY={key.decode()}\n')
    
    # Write back to .env file
    with open(env_path, 'w') as f:
        f.writelines(env_contents)
    
    print("Generated new encryption key and updated .env file")

if __name__ == "__main__":
    generate_encryption_key() 