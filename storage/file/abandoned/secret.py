"""原加密逻辑"""
# 逻辑如下
# A为所有者，B为使用者
# A调用decrypt_files(密码)，无论是否加密，成功解密，yaml和数据库复原，可直接查看；
# B调用decrypt_files()，无论是否加密，成功加密，yaml和数据库上锁，不可直接查看，但不影响使用
import os
import base64
from pathlib import Path
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# 只需要在main里面调用 decrypt_files() 即可

KEY_FILE = Path("lrobot/secret/.key")


# 解密文件
def decrypt_files(password: str):
    config_dir = Path("lrobot/secret")
    yaml_files = config_dir.glob("*.yaml")
    db_files = config_dir.glob("*.db")
    all_files = list(config_dir.glob("*.yaml")) + list(config_dir.glob("*.db"))
    key = generate_key(password)
    with open(KEY_FILE, "rb") as f:
        stored_key = f.read()

    if key == stored_key:
        for file_path in all_files:
            if is_encrypted(file_path):
                try:
                    decrypt_file(file_path, key)
                    print(f"Decrypted: {file_path}")
                except Exception:
                    print(f"Failed to decrypt {file_path} with provided password.")
                    continue
    else:
        for file_path in all_files:
            if not is_encrypted(file_path):
                encrypt_file(file_path, stored_key)
                print(f"Encrypted: {file_path}")

        # 虚拟数据库连接
        create_virtual_db()


# 第一次调用，储存密钥
def save_key(password: str):
    key = generate_key(password)
    with open(KEY_FILE, "wb") as f:
        f.write(key)


# 通过密码生成加密密钥
def generate_key(password: str):
    kdf = PBKDF2HMAC(
        algorithm=SHA256(),
        length=32,
        salt=b"LRobot",
        iterations=100000,
    )
    return kdf.derive(password.encode())


# 加密单个文件
def encrypt_file(file_path: Path, key: bytes):
    try:
        with open(file_path, "rb") as f:
            plaintext = f.read()
        aesgcm = AESGCM(key)  # 创建 AESGCM 加密器
        nonce = os.urandom(12)  # 生成随机的 nonce
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        encrypted_data = b"ENCRYPTED" + nonce + ciphertext  # 在前面加上标记
        encrypted_data = base64.b64encode(
            encrypted_data
        )  # 使用 base64 编码存储加密数据
        # 写入加密数据到文件
        with open(file_path, "wb") as f:
            f.write(encrypted_data)
    except Exception as e:
        print(f"Error encrypting file '{file_path}': {e}")


# 解密单个文件
def decrypt_file(file_path: Path, key: bytes):
    try:
        with open(file_path, "rb") as f:
            encrypted_data = base64.b64decode(f.read())
        encrypted_data = encrypted_data[len(b"ENCRYPTED") :]
        nonce = encrypted_data[:12]  # 前 12 字节是 nonce
        ciphertext = encrypted_data[12:]  # 剩余的是加密后的内容
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        with open(file_path, "wb") as f:
            f.write(plaintext)
        print(f"File '{file_path}' decrypted successfully.")
    except Exception as e:
        print(f"Error decrypting file '{file_path}': {e}")


# 检测文件是否已加密
def is_encrypted(file_path: Path):
    try:
        with open(file_path, "rb") as f:
            encrypted_data = base64.b64decode(f.read())
            if encrypted_data.startswith(b"ENCRYPTED"):
                return True
            else:
                return False
    except Exception as e:
        return False


# 以下为 config 里面的实现读取加密文件
def load_configs(self):
    config_dir = Path("lrobot/secret")
    config_files = config_dir.glob("*.yaml")
    with open(KEY_FILE, "rb") as f:
        key = f.read()
    for file_path in config_files:
        if is_encrypted(file_path):
            with open(file_path, "rb") as encrypted_file:
                encrypted_data = base64.b64decode(encrypted_file.read())
            encrypted_data = encrypted_data[len(b"ENCRYPTED") :]
            aesgcm = AESGCM(key)
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            aesgcm = AESGCM(key)
            try:
                plaintext = aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
                loaded_config = yaml.safe_load(plaintext) or {}
                self._config.update(loaded_config)
            except Exception as e:
                print(f"Failed to load encrypted file {file_path}: {e}")
        else:
            with open(file_path, "r", encoding="utf-8") as file:
                loaded_config = yaml.safe_load(file) or {}
                self._config.update(loaded_config)
