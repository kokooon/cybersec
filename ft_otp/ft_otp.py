import argparse
import	sys
import	time
from cryptography.fernet import Fernet
import	hmac
import	struct

def	parser():
	parser = argparse.ArgumentParser(prog='ft_otp', description="ft_otp is a program that allows you to store an initial password in file, and that is capable of generating a new one time password every time it is requested.")
	parser.add_argument('-g', help='store in ft_otp.key a hexadecimal key of at least 64 characters.', type=str)
	parser.add_argument('-k', help='generates a new Time-based Temporary One Time password based on the key given as argument and prints it on the standard output')
	args = parser.parse_args()
	if not args.g and args.k is None:
		sys.exit("Error with arguments, Run ft_otp.py -h for help...")
	return args

def	validate_key(key):
	base = "1234567890abcdef"
	key = key.strip().decode('utf-8')
	if len(key) < 64 or not all (c in base for c in key):
		sys.exit("Invalid key. Need a 64 Hexadecimal key")

def	store_key():
	try:
		with open(args.g, "rb") as f:
			key = f.read()
	except Exception as e:
		print("Error: (open) " + args.g + " couldn't be opened", e)
		return
	validate_key(key)
	secret_key = Fernet.generate_key()
	with open("secret.key", "wb") as f:
		f.write(secret_key)
	fernet = Fernet(secret_key)
	encrypted_key = fernet.encrypt(key)
	with open("ft_otp.key", "wb") as f:
		f.write(encrypted_key)
	return

def generate_totp():
	try:
		with open(args.k, "rb") as f:
			ft_otp_key = f.read()
	except Exception as e:
		print("Error: (open) " + args.k + " couldn't be opened", e)
		return
	try:
		with open("secret.key", "rb") as f:
			secret_key = f.read()
	except Exception as e:
		print("Error: Secret_key needed for decryption", e)
		return
	fernet = Fernet(secret_key)
	decrypted_key = fernet.decrypt(ft_otp_key).decode('utf-8')
	try:
		byte_key = bytes.fromhex(decrypted_key)
	except Exception as e:
		print("Error: Unpair key: ", e)
		return
	intervals = struct.pack('>Q', int(time.time() // 30))
	hmac1 = hmac.new(byte_key, intervals, "sha1").digest()
	offset = hmac1[19] & 0xf
	otp = ((hmac1[offset]  & 0x7f) << 24
			| (hmac1[offset+1] & 0xff) << 16
			| (hmac1[offset+2] & 0xff) <<  8
			| (hmac1[offset+3] & 0xff)
			)
	otp %= 10 ** 6
	print("Time-based One-Time Password (TOTP):", str(otp).zfill(6))
	

if __name__ == "__main__":
	args = parser()
	if args.g:
		store_key()
	elif args.k:
		generate_totp()