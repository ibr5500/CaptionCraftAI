import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from transformers import AutoProcessor, BlipForConditionalGeneration

processor = AutoProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def caption_images(url):
    
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    img_elems = soup.find_all('img')

    with open("captions.txt", "w") as caption_file:
        for img_elem in img_elems:
            img_url = img_elem.get('src')

            if 'svg' in img_url or '1x1' in img_url:
                continue

            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif not img_url.startswith('http://') and not img_url.startswith('https://'):
                continue

            try:
                response = requests.get(img_url)
                raw_image = Image.open(BytesIO(response.content))

                if raw_image.size[0] * raw_image.size[1] < 400:
                    continue

                raw_image = raw_image.convert('RGB')
                
                inputs = processor(raw_image, return_tensors = "pt")

                outputs = model.generate(**inputs, max_new_tokens = 50)

                caption = processor.decode(outputs[0], skip_special_tokens = True)

                caption_file.write(f"{img_url}: {caption}\n")
            
            except Exception as e:
                print(f"Error processing image {img_url}: {e}")
                continue            

# caption_images("https://en.wikipedia.org/wiki/IBM")
caption_images("https://en.wikipedia.org/wiki/Fauna_of_Africa")
