# ikea web-scraper

This file contains the source code to scrape product information from ikeas website
built wth selenium.

![alt text](https://media.giphy.com/media/TIISk5oX45MpBHlVFn/giphy.gif)



# Schema

```
            results_dict = {
                "id": [],
                "url":[],
                "price": [],
                "description": [],
                "images":[],
                "Source":[]
            }
```
The project collects the following pieces of information 

1. URL - e.g. https://www.ikea.com/gb/en/p/muskot-plant-pot-white-30308201/
2. Price - e.g. £1.5
3. Description e.g. 'Plant pot, white 9 cm' 
4. Image - e.g. [data/Cabinets_ikea/kallax-shelving-unit-white-80275887/kallax-shelving-unit-white-80275887-x.jpg]
5. Source - e.g. IKEA




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
