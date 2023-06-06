import requests
import os
import	string
import argparse
from bs4 import BeautifulSoup
import	re
from urllib.parse import urljoin
import	signal
import	sys

valid_format = [".jpeg", ".jpg", ".png", ".gif", ".bmp"]
visited = set()

def	parser():
	parser = argparse.ArgumentParser(prog='spider', description="Scrap images in .jpeg, .jpg, .png, .gif or .bmp format in a defined URL.")
	parser.add_argument('URL', help='Url to scrap')
	parser.add_argument('-r', '--recursive', help='Recursively downloads the images in a URL received as a parameter', action='store_true')
	parser.add_argument('-l', '--level', help='Indicates the maximum depth level of the recursive download. If not indicated, it will be 5', type=int)
	parser.add_argument('-p', '--path', help='Indicates the path where the downloaded files will be saved. If not specified, ./data/ will be used.', default='./data/')
	args = parser.parse_args()
	if args.level:
		if args.level < 0:
			parser.error('--level can not be negative')
	if args.recursive:
		if args.level is None:
			args.level = 5
	elif not args.level:
		args.level = 0
	elif args.level is not None and not args.recursive:
		parser.error('--level can not be use without --recursive')
	return args

def	sanitize_folder_name(folder):
	if folder == './data/':
		return folder
	valid_chars = frozenset(string.ascii_letters + string.digits + "._-")
	sanitized_folder = ''.join(c for c in folder if c in valid_chars)
	return sanitized_folder

def	handle_signal(signal, frame):
	print("Spider has been interrupted... Exiting")
	sys.exit(0)

def	download(url, folder):
	if url.startswith("http"):
		if check_server_status(url):
			response = requests.get(url)
			if response.status_code == 200:
				sanitized_folder = sanitize_folder_name(folder)
				os.makedirs(sanitized_folder, exist_ok=True)
				filename = os.path.basename(url)
				filename = filename[-100:]
				filename = os.path.join(sanitized_folder, filename)
				try:
					with open(filename, "wb") as file:
						file.write(response.content)
				except OSError as e:
					print("Une erreur s'est produite lors de l'enregistrement du fichier :", e)
					return
	else:
		if(os.path.isfile(url)):
			sanitized_folder = sanitize_folder_name(folder)
			os.makedirs(sanitized_folder, exist_ok=True)
			filename = os.path.basename(url)
			filename = filename[-100:]
			filename = os.path.join(sanitized_folder, filename)
			try:
				with open(url, "rb") as source, open(filename, "wb") as destination:
					destination.write(source.read())
			except OSError as e:
					#print("Une erreur s'est produite lors de l'enregistrement du fichier :", e)
					return

def check_server_status(url):
	if url.startswith("http"):
		try:
			response = requests.get(url)
			if response.status_code == 200:
				return True
			else:
				return False
		except requests.exceptions.RequestException as e:
			#print("Une erreur s'est produite lors de la requete :", e)
			return False
	else:
		return False

def spider(url, index, folder):
	print(url)
	if index < 0 or url in visited:
		return
	visited.add(url)
	index = index - 1
	if os.path.isfile(url):
		with open(url, "r") as file:
			data = file.read()
			soup = BeautifulSoup(data, 'html.parser')
			img = soup.find_all("img")
			links = soup.find_all('a', href=True)
	elif check_server_status(url):
		data = requests.get(url)
		soup = BeautifulSoup(data.text, 'html.parser')
		img = soup.find_all("img")
		links = soup.find_all('a', href=True)
	else:
		print("Invalid URL")
		return
	image_srcs = []
	if img:
		for i in img:
			src = i.get("src")
			image_srcs.append(src)
	for src in image_srcs:
		if any(src.endswith(extension) for extension in valid_format):
			if re.match(r"^//", src):
				src = "https:" + src
			elif src.startswith("/"):
				src = "https:" + src
			elif src.startswith("./"):
				src = urljoin(url, src)
			download(src, folder)
	if index >= 0:
		for link in links:
			href = link['href']
			if href.startswith(url):
				if href not in visited:
					spider(href, index, folder)
			if href.startswith("#"):
				continue
			if href.startswith("/"):
				href = urljoin(url, href)
				if href not in visited:
					spider(href, index, folder)
			if re.match(r"^//", href):
				href = url + href
				if href not in visited:
					spider(href, index, folder)

if __name__ == "__main__":
	args = parser()
	base_url = args.URL
	index = args.level
	folder = args.path
	signal.signal(signal.SIGINT, handle_signal)
	spider(base_url, index, folder)
