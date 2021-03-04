# ikea web-scraper

This file contains the source code to scrape product information from ikeas website
built wth selenium.

# Schema

```
            results_dict = {
                "id": [],
                "query":[]
                "url":[],
                "source":[],
                "name": [],
                "price": [],
                "description": [],
                "dims_image": [],
                "dimensions": [],
                "packaging": [],
                "details": [],
                "sustainability": [],
                "images":[],
                "materials":[]
            }
```

This file contains the source code to scrape product information from ikeas website

## Installation
To get started make sure you are running python3. The script writes a data file
to both AWS and locally too. For AWS deployment make sure you have set up your own
credentials.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss
what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
