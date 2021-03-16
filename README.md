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
The project collects the following pieces of information 

1. URL - e.g. https://www.ikea.com/gb/en/p/muskot-plant-pot-white-30308201/
2. Query - e.g. This is the search term. 'Plant+Pots'
3. Source - e.g. IKEA Website
4. Name - e.g. MUSKOT
5. Price - e.g. £1.5
6. Description e.g. 'Plant pot, white 9 cm' 
7. Dims Image - e.g. Schematic or singular image with white background with dimensions
8. Dimensions -  Dict of length Height and width. e.g {'Length: 11 cm, Weight: 0.39 kg, Diameter: 12 cm, Package(s): 1'}
9. Packaging - Details of packaging 
10. Details - e.g. Longer Description 'Decorate your home with plants combined with a plant pot to suit your style.
May be combined with the other plant pots in the MUSKOT series.'
11. Sustainabiliity - Any information on recycling or Sustainability
12. Images - JPG.s of all product images
13. Materials - Details of materials - 'Earthenware, Pigmented powder coating'




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
