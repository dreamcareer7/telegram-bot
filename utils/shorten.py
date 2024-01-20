import pyshorteners

def get_shorten_url_from_long_url(url:str):
    long_url = input(url)
    
    #TinyURL shortener service
    type_tiny = pyshorteners.Shortener()
    short_url = type_tiny.tinyurl.short(long_url)
    
    print("The Shortened URL is: " + short_url)

    return short_url