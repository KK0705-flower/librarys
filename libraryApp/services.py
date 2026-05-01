import requests

url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:'

def main(isbn):
    req_url = url + isbn
    response = requests.get(req_url)
    return response.text

if __name__ == "__main__":
    while True:
        isbn_input = input("input ISBN >>>")
        print(main(isbn_input))