import os
import json
import requests
from urllib.parse import urlparse
from PIL import Image
import firebase_admin
from firebase_admin import credentials, storage


def initialize_firebase():
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': '<Firebase Storage Bucket Url>'
    })


def download_image(url, folder):
    try:
        response = requests.get(url)
        response.raise_for_status()
        url_path = urlparse(url).path
        filename = os.path.basename(url_path)
        filepath = os.path.join(folder, filename)

        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Image downloaded: {filepath}")
        return filepath
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None


def convert_image_to_png(image_path):
    try:
        with Image.open(image_path) as img:
            png_path = os.path.splitext(image_path)[0] + ".png"
            img.save(png_path, 'PNG')
            print(f"Converted image saved: {png_path}")
            return png_path
    except Exception as e:
        print(f"Failed to convert {image_path} to PNG: {e}")
        return None


def upload_image_to_firebase(image_path):
    try:
        bucket = storage.bucket()
        blob = bucket.blob(os.path.basename(image_path))
        blob.upload_from_filename(image_path)
        blob.make_public()
        print(f"Image uploaded to Firebase: {blob.public_url}")
        return blob.public_url
    except Exception as e:
        print(f"Failed to upload {image_path} to Firebase: {e}")
        return None


def replace_urls_in_json(obj, url_mapping):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "image" and value in url_mapping:
                obj[key] = url_mapping[value]
            else:
                replace_urls_in_json(value, url_mapping)
    elif isinstance(obj, list):
        for item in obj:
            replace_urls_in_json(item, url_mapping)


def extract_image_urls(obj):
    image_urls = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "image" and isinstance(value, str):
                image_urls.append(value)
            else:
                image_urls.extend(extract_image_urls(value))
    elif isinstance(obj, list):
        for item in obj:
            image_urls.extend(extract_image_urls(item))
    return image_urls


def main(json_input, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    image_urls = extract_image_urls(json_input)
    url_mapping = {}

    for url in image_urls:
        image_path = download_image(url, download_folder)
        if image_path:
            png_path = convert_image_to_png(image_path)
            if png_path:
                firebase_url = upload_image_to_firebase(png_path)
                if firebase_url:
                    url_mapping[url] = firebase_url

    replace_urls_in_json(json_input, url_mapping)

    with open('updated_json.json', 'w') as f:
        json.dump(json_input, f, indent=4)
    print("Updated JSON saved to updated_json.json")


if __name__ == "__main__":
    json_input = """
                                   [
                                     {
                                       "id": 1,
                                       "title": "Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops",
                                       "price": 109.95,
                                       "description": "Your perfect pack for everyday use and walks in the forest. Stash your laptop (up to 15 inches) in the padded sleeve, your everyday",
                                       "category": "men's clothing",
                                       "image": "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg",
                                       "rating": {
                                         "rate": 3.9,
                                         "count": 120
                                       }
                                     },
                                     {
                                       "id": 2,
                                       "title": "Mens Casual Premium Slim Fit T-Shirts ",
                                       "price": 22.3,
                                       "description": "Slim-fitting style, contrast raglan long sleeve, three-button henley placket, light weight & soft fabric for breathable and comfortable wearing. And Solid stitched shirts with round neck made for durability and a great fit for casual fashion wear and diehard baseball fans. The Henley style round neckline includes a three-button placket.",
                                       "category": "men's clothing",
                                       "image": "https://fakestoreapi.com/img/71-3HjGNDUL._AC_SY879._SX._UX._SY._UY_.jpg",
                                       "rating": {
                                         "rate": 4.1,
                                         "count": 259
                                       }
                                     },
                                     {
                                       "id": 3,
                                       "title": "Mens Cotton Jacket",
                                       "price": 55.99,
                                       "description": "great outerwear jackets for Spring/Autumn/Winter, suitable for many occasions, such as working, hiking, camping, mountain/rock climbing, cycling, traveling or other outdoors. Good gift choice for you or your family member. A warm hearted love to Father, husband or son in this thanksgiving or Christmas Day.",
                                       "category": "men's clothing",
                                       "image": "https://fakestoreapi.com/img/71li-ujtlUL._AC_UX679_.jpg",
                                       "rating": {
                                         "rate": 4.7,
                                         "count": 500
                                       }
                                     },
                                     {
                                       "id": 4,
                                       "title": "Mens Casual Slim Fit",
                                       "price": 15.99,
                                       "description": "The color could be slightly different between on the screen and in practice. / Please note that body builds vary by person, therefore, detailed size information should be reviewed below on the product description.",
                                       "category": "men's clothing",
                                       "image": "https://fakestoreapi.com/img/71YXzeOuslL._AC_UY879_.jpg",
                                       "rating": {
                                         "rate": 2.1,
                                         "count": 430
                                       }
                                     },
                                     {
                                       "id": 5,
                                       "title": "John Hardy Women's Legends Naga Gold & Silver Dragon Station Chain Bracelet",
                                       "price": 695,
                                       "description": "From our Legends Collection, the Naga was inspired by the mythical water dragon that protects the ocean's pearl. Wear facing inward to be bestowed with love and abundance, or outward for protection.",
                                       "category": "jewelery",
                                       "image": "https://fakestoreapi.com/img/71pWzhdJNwL._AC_UL640_QL65_ML3_.jpg",
                                       "rating": {
                                         "rate": 4.6,
                                         "count": 400
                                       }
                                     },
                                     {
                                       "id": 6,
                                       "title": "Solid Gold Petite Micropave ",
                                       "price": 168,
                                       "description": "Satisfaction Guaranteed. Return or exchange any order within 30 days.Designed and sold by Hafeez Center in the United States. Satisfaction Guaranteed. Return or exchange any order within 30 days.",
                                       "category": "jewelery",
                                       "image": "https://fakestoreapi.com/img/61sbMiUnoGL._AC_UL640_QL65_ML3_.jpg",
                                       "rating": {
                                         "rate": 3.9,
                                         "count": 70
                                       }
                                     },
                                     {
                                       "id": 7,
                                       "title": "White Gold Plated Princess",
                                       "price": 9.99,
                                       "description": "Classic Created Wedding Engagement Solitaire Diamond Promise Ring for Her. Gifts to spoil your love more for Engagement, Wedding, Anniversary, Valentine's Day...",
                                       "category": "jewelery",
                                       "image": "https://fakestoreapi.com/img/71YAIFU48IL._AC_UL640_QL65_ML3_.jpg",
                                       "rating": {
                                         "rate": 3,
                                         "count": 400
                                       }
                                     },
                                     {
                                       "id": 8,
                                       "title": "Pierced Owl Rose Gold Plated Stainless Steel Double",
                                       "price": 10.99,
                                       "description": "Rose Gold Plated Double Flared Tunnel Plug Earrings. Made of 316L Stainless Steel",
                                       "category": "jewelery",
                                       "image": "https://fakestoreapi.com/img/51UDEzMJVpL._AC_UL640_QL65_ML3_.jpg",
                                       "rating": {
                                         "rate": 1.9,
                                         "count": 100
                                       }
                                     },
                                     {
                                       "id": 9,
                                       "title": "WD 2TB Elements Portable External Hard Drive - USB 3.0 ",
                                       "price": 64,
                                       "description": "USB 3.0 and USB 2.0 Compatibility Fast data transfers Improve PC Performance High Capacity; Compatibility Formatted NTFS for Windows 10, Windows 8.1, Windows 7; Reformatting may be required for other operating systems; Compatibility may vary depending on user’s hardware configuration and operating system",
                                       "category": "electronics",
                                       "image": "https://fakestoreapi.com/img/61IBBVJvSDL._AC_SY879_.jpg",
                                       "rating": {
                                         "rate": 3.3,
                                         "count": 203
                                       }
                                     },
                                     {
                                       "id": 10,
                                       "title": "SanDisk SSD PLUS 1TB Internal SSD - SATA III 6 Gb/s",
                                       "price": 109,
                                       "description": "Easy upgrade for faster boot up, shutdown, application load and response (As compared to 5400 RPM SATA 2.5” hard drive; Based on published specifications and internal benchmarking tests using PCMark vantage scores) Boosts burst write performance, making it ideal for typical PC workloads The perfect balance of performance and reliability Read/write speeds of up to 535MB/s/450MB/s (Based on internal testing; Performance may vary depending upon drive capacity, host device, OS and application.)",
                                       "category": "electronics",
                                       "image": "https://fakestoreapi.com/img/61U7T1koQqL._AC_SX679_.jpg",
                                       "rating": {
                                         "rate": 2.9,
                                         "count": 470
                                       }
                                     },
                                     {
                                       "id": 11,
                                       "title": "Silicon Power 256GB SSD 3D NAND A55 SLC Cache Performance Boost SATA III 2.5",
                                       "price": 109,
                                       "description": "3D NAND flash are applied to deliver high transfer speeds Remarkable transfer speeds that enable faster bootup and improved overall system performance. The advanced SLC Cache Technology allows performance boost and longer lifespan 7mm slim design suitable for Ultrabooks and Ultra-slim notebooks. Supports TRIM command, Garbage Collection technology, RAID, and ECC (Error Checking & Correction) to provide the optimized performance and enhanced reliability.",
                                       "category": "electronics",
                                       "image": "https://fakestoreapi.com/img/71kWymZ+c+L._AC_SX679_.jpg",
                                       "rating": {
                                         "rate": 4.8,
                                         "count": 319
                                       }
                                     },
                                     {
                                       "id": 12,
                                       "title": "WD 4TB Gaming Drive Works with Playstation 4 Portable External Hard Drive",
                                       "price": 114,
                                       "description": "Expand your PS4 gaming experience, Play anywhere Fast and easy, setup Sleek design with high capacity, 3-year manufacturer's limited warranty",
                                       "category": "electronics",
                                       "image": "https://fakestoreapi.com/img/61mtL65D4cL._AC_SX679_.jpg",
                                       "rating": {
                                         "rate": 4.8,
                                         "count": 400
                                       }
                                     },
                                     {
                                       "id": 13,
                                       "title": "Acer SB220Q bi 21.5 inches Full HD (1920 x 1080) IPS Ultra-Thin",
                                       "price": 599,
                                       "description": "21. 5 inches Full HD (1920 x 1080) widescreen IPS display And Radeon free Sync technology. No compatibility for VESA Mount Refresh Rate: 75Hz - Using HDMI port Zero-frame design | ultra-thin | 4ms response time | IPS panel Aspect ratio - 16: 9. Color Supported - 16. 7 million colors. Brightness - 250 nit Tilt angle -5 degree to 15 degree. Horizontal viewing angle-178 degree. Vertical viewing angle-178 degree 75 hertz",
                                       "category": "electronics",
                                       "image": "https://fakestoreapi.com/img/81QpkIctqPL._AC_SX679_.jpg",
                                       "rating": {
                                         "rate": 2.9,
                                         "count": 250
                                       }
                                     },
                                     {
                                       "id": 14,
                                       "title": "Samsung 49-Inch CHG90 144Hz Curved Gaming Monitor (LC49HG90DMNXZA) – Super Ultrawide Screen QLED ",
                                       "price": 999.99,
                                       "description": "49 INCH SUPER ULTRAWIDE 32:9 CURVED GAMING MONITOR with dual 27 inch screen side by side QUANTUM DOT (QLED) TECHNOLOGY, HDR support and factory calibration provides stunningly realistic and accurate color and contrast 144HZ HIGH REFRESH RATE and 1ms ultra fast response time work to eliminate motion blur, ghosting, and reduce input lag",
                                       "category": "electronics",
                                       "image": "https://fakestoreapi.com/img/81Zt42ioCgL._AC_SX679_.jpg",
                                       "rating": {
                                         "rate": 2.2,
                                         "count": 140
                                       }
                                     },
                                     {
                                       "id": 15,
                                       "title": "BIYLACLESEN Women's 3-in-1 Snowboard Jacket Winter Coats",
                                       "price": 56.99,
                                       "description": "Note:The Jackets is US standard size, Please choose size as your usual wear Material: 100% Polyester; Detachable Liner Fabric: Warm Fleece. Detachable Functional Liner: Skin Friendly, Lightweigt and Warm.Stand Collar Liner jacket, keep you warm in cold weather. Zippered Pockets: 2 Zippered Hand Pockets, 2 Zippered Pockets on Chest (enough to keep cards or keys)and 1 Hidden Pocket Inside.Zippered Hand Pockets and Hidden Pocket keep your things secure. Humanized Design: Adjustable and Detachable Hood and Adjustable cuff to prevent the wind and water,for a comfortable fit. 3 in 1 Detachable Design provide more convenience, you can separate the coat and inner as needed, or wear it together. It is suitable for different season and help you adapt to different climates",
                                       "category": "women's clothing",
                                       "image": "https://fakestoreapi.com/img/51Y5NI-I5jL._AC_UX679_.jpg",
                                       "rating": {
                                         "rate": 2.6,
                                         "count": 235
                                       }
                                     },
                                     {
                                       "id": 16,
                                       "title": "Lock and Love Women's Removable Hooded Faux Leather Moto Biker Jacket",
                                       "price": 29.95,
                                       "description": "100% POLYURETHANE(shell) 100% POLYESTER(lining) 75% POLYESTER 25% COTTON (SWEATER), Faux leather material for style and comfort / 2 pockets of front, 2-For-One Hooded denim style faux leather jacket, Button detail on waist / Detail stitching at sides, HAND WASH ONLY / DO NOT BLEACH / LINE DRY / DO NOT IRON",
                                       "category": "women's clothing",
                                       "image": "https://fakestoreapi.com/img/81XH0e8fefL._AC_UY879_.jpg",
                                       "rating": {
                                         "rate": 2.9,
                                         "count": 340
                                       }
                                     },
                                     {
                                       "id": 17,
                                       "title": "Rain Jacket Women Windbreaker Striped Climbing Raincoats",
                                       "price": 39.99,
                                       "description": "Lightweight perfet for trip or casual wear---Long sleeve with hooded, adjustable drawstring waist design. Button and zipper front closure raincoat, fully stripes Lined and The Raincoat has 2 side pockets are a good size to hold all kinds of things, it covers the hips, and the hood is generous but doesn't overdo it.Attached Cotton Lined Hood with Adjustable Drawstrings give it a real styled look.",
                                       "category": "women's clothing",
                                       "image": "https://fakestoreapi.com/img/71HblAHs5xL._AC_UY879_-2.jpg",
                                       "rating": {
                                         "rate": 3.8,
                                         "count": 679
                                       }
                                     },
                                     {
                                       "id": 18,
                                       "title": "MBJ Women's Solid Short Sleeve Boat Neck V ",
                                       "price": 9.85,
                                       "description": "95% RAYON 5% SPANDEX, Made in USA or Imported, Do Not Bleach, Lightweight fabric with great stretch for comfort, Ribbed on sleeves and neckline / Double stitching on bottom hem",
                                       "category": "women's clothing",
                                       "image": "https://fakestoreapi.com/img/71z3kpMAYsL._AC_UY879_.jpg",
                                       "rating": {
                                         "rate": 4.7,
                                         "count": 130
                                       }
                                     },
                                     {
                                       "id": 19,
                                       "title": "Opna Women's Short Sleeve Moisture",
                                       "price": 7.95,
                                       "description": "100% Polyester, Machine wash, 100% cationic polyester interlock, Machine Wash & Pre Shrunk for a Great Fit, Lightweight, roomy and highly breathable with moisture wicking fabric which helps to keep moisture away, Soft Lightweight Fabric with comfortable V-neck collar and a slimmer fit, delivers a sleek, more feminine silhouette and Added Comfort",
                                       "category": "women's clothing",
                                       "image": "https://fakestoreapi.com/img/51eg55uWmdL._AC_UX679_.jpg",
                                       "rating": {
                                         "rate": 4.5,
                                         "count": 146
                                       }
                                     },
                                     {
                                       "id": 20,
                                       "title": "DANVOUY Womens T Shirt Casual Cotton Short",
                                       "price": 12.99,
                                       "description": "95%Cotton,5%Spandex, Features: Casual, Short Sleeve, Letter Print,V-Neck,Fashion Tees, The fabric is soft and has some stretch., Occasion: Casual/Office/Beach/School/Home/Street. Season: Spring,Summer,Autumn,Winter.",
                                       "category": "women's clothing",
                                       "image": "https://fakestoreapi.com/img/61pHAEJ4NML._AC_UX679_.jpg",
                                       "rating": {
                                         "rate": 3.6,
                                         "count": 145
                                       }
                                     },
                                   {
                                       "id": 21,
                                       "title": "Rolex Submariner",
                                       "price": 12500.00,
                                       "description": "Automatic, Stainless Steel, Waterproof, Luxury Watch",
                                       "category": "men's clothing",
                                       "image": "https://images-cdn.ubuy.co.in/635accf179b8dc1c1c52fe34-rolex-submariner-mechanical-automatic.jpg",
                                       "rating": {
                                         "rate": 4.8,
                                         "count": 250
                                       }
                                     },
                                     {
                                       "id": 22,
                                       "title": "Omega Speedmaster",
                                       "price": 5200.00,
                                       "description": "Chronograph, Stainless Steel, Moonwatch",
                                       "category": "men's clothing",
                                       "image": "https://images-cdn.ubuy.co.in/64f7557e5059112b8910baf0-omega-speedmaster-professional-moonwatch.jpg",
                                       "rating": {
                                         "rate": 4.7,
                                         "count": 300
                                       }
                                     },
                                     {
                                       "id": 23,
                                       "title": "Tag Heuer Carrera",
                                       "price": 3500.00,
                                       "description": "Automatic, Stainless Steel, Chronograph",
                                       "category": "men's clothing",
                                       "image": "https://cdn1.ethoswatches.com/media/catalog/product/cache/6e5de5bc3d185d8179cdc7258143f41a/t/a/tag-heuer-carrera-cbn201c-fc6542-large.jpg",
                                       "rating": {
                                         "rate": 4.5,
                                         "count": 150
                                       }
                                     },
                                     {
                                       "id": 24,
                                       "title": "Seiko Diver's Watch",
                                       "price": 450.00,
                                       "description": "Automatic, Stainless Steel, Water-Resistant",
                                       "category": "men's clothing",
                                       "image": "https://www.seikowatches.com/in-en/-/media/HtmlUploader/GlobalEn/Seiko/Home/products/prospex/special/55th-anniversary-limited-2nd/assets/image/main_l_img.png",
                                       "rating": {
                                         "rate": 4.3,
                                         "count": 200
                                       }
                                     },
                                     {
                                       "id": 25,
                                       "title": "Casio G-Shock",
                                       "price": 99.00,
                                       "description": "Digital, Resin, Shock-Resistant",
                                       "category": "men's clothing",
                                       "image": "https://www.casio.com/content/dam/casio/product-info/locales/in/en/timepiece/product/watch/G/GB/GBA/gba-900uu-5a/assets/GBA-900UU-5A.png.transform/main-visual-sp/image.png",
                                       "rating": {
                                         "rate": 4.6,
                                         "count": 400
                                       }
                                     },
                                     {
                                       "id": 26,
                                       "title": "Silk Necktie",
                                       "price": 25.00,
                                       "description": "100% Silk, Classic Design, Formal Wear",
                                       "category": "men's clothing",
                                       "image": "https://fakestoreapi.com/img/silk_necktie.jpg",
                                       "rating": {
                                         "rate": 4.4,
                                         "count": 80
                                       }
                                     },
                                     {
                                       "id": 27,
                                       "title": "Paisley Tie",
                                       "price": 15.00,
                                       "description": "Polyester, Paisley Pattern, Fashionable",
                                       "category": "men's clothing",
                                       "image": "https://fakestoreapi.com/img/paisley_tie.jpg",
                                       "rating": {
                                         "rate": 4.2,
                                         "count": 65
                                       }
                                     },
                                     {
                                       "id": 28,
                                       "title": "Striped Silk Tie",
                                       "price": 30.00,
                                       "description": "100% Silk, Striped Pattern, Business Wear",
                                       "category": "men's clothing",
                                       "image": "https://fakestoreapi.com/img/striped_silk_tie.jpg",
                                       "rating": {
                                         "rate": 4.5,
                                         "count": 90
                                       }
                                     },
                                     {
                                       "id": 29,
                                       "title": "Bow Tie",
                                       "price": 12.00,
                                       "description": "Polyester, Pre-Tied, Classic Style",
                                       "category": "men's clothing",
                                       "image": "https://fakestoreapi.com/img/bow_tie.jpg",
                                       "rating": {
                                         "rate": 4.1,
                                         "count": 40
                                       }
                                     },
                                     {
                                       "id": 30,
                                       "title": "Knitted Tie",
                                       "price": 20.00,
                                       "description": "Cotton, Knitted Design, Casual Wear",
                                       "category": "men's clothing",
                                       "image": "https://fakestoreapi.com/img/knitted_tie.jpg",
                                       "rating": {
                                         "rate": 4.3,
                                         "count": 50
                                       }
                                     },
                                     {
                                       "id": 31,
                                       "title": "Levi's 501 Original Fit Jeans",
                                       "price": 69.99,
                                       "description": "100% Cotton, Button Fly, Straight Leg",
                                       "category": "men's clothing",
                                       "image": "https://fakestoreapi.com/img/levis_501.jpg",
                                       "rating": {
                                         "rate": 4.6,
                                         "count": 500
                                       }
                                     },
                                     {
                                       "id": 32,
                                       "title": "Dockers Classic Fit Khakis",
                                       "price": 45.00,
                                       "description": "Cotton Blend, Pleated Front, Classic Fit",
                                       "category": "men's clothing",
                                       "image": "https://fakestoreapi.com/img/dockers_khakis.jpg",
                                       "rating": {
                                         "rate": 4.4,
                                         "count": 300
                                       }
                                     },
                                         {
                                           "id": 33,
                                           "title": "Adidas Track Pants",
                                           "price": 50.00,
                                           "description":"Polyester, Elastic Waist, Athletic Wear",
                                       "category": "men's clothing",
                                       "image": "https://fakestoreapi.com/img/adidas_trackpants.jpg",
                                       "rating": {
                                         "rate": 4.7,
                                         "count": 350
                                       }
                                     },
                                     {
                                       "id": 34,
                                       "title": "Wrangler Relaxed Fit Jeans",
                                       "price": 39.99,
                                       "description": "Cotton Blend, Relaxed Fit, Durable",
                                       "category": "men's clothing",
                                       "image": "https://fakestoreapi.com/img/wrangler_jeans.jpg",
                                       "rating": {
                                         "rate": 4.5,
                                         "count": 200
                                       }
                                     },
                                     {
                                       "id": 35,
                                       "title": "Under Armour Joggers",
                                       "price": 55.00,
                                       "description": "Polyester, Tapered Leg, Athletic Fit",
                                       "category": "men's clothing",
                                       "image": "https://fakestoreapi.com/img/underarmour_joggers.jpg",
                                       "rating": {
                                         "rate": 4.6,
                                         "count": 250
                                       }
                                     }
                                   ]
                                   """

    json_data = json.loads(json_input)
    download_folder = "downloaded_images"

    initialize_firebase()
    main(json_data, download_folder)
