import os
import subprocess
import dotenv

def decrypt (filepath_in: str='.env.enc', filepath_out='.env'):
    command = ['openssl', 'aes-256-cbc', '-salt', '-pbkdf2', '-d', '-in', os.path.abspath(filepath_in), '-out', os.path.abspath(filepath_out)]
    subprocess.run(command)
    
def load_dotenv (filepath_env='.env'):
    dotenv.load_dotenv(os.path.abspath(filepath_env))
    return {'BOT_TOKEN': os.getenv('BOT_TOKEN')}