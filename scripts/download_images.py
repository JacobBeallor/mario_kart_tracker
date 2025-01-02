import os
import requests
from urllib.parse import urlparse
from pathlib import Path

def download_image(url, save_path):
    """
    Download an image from a URL and save it to the specified path
    
    Args:
        url (str): URL of the image to download
        save_path (str): Path where the image should be saved
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save the image
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Successfully downloaded: {save_path}")
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")

def download_images(url_dict):
    """
    Download images from a dictionary of URLs
    
    Args:
        url_dict (dict): Dictionary with categories as keys and lists of (filename, url) tuples as values
            Example: {
                'characters': [('mario.png', 'http://example.com/mario.png'), ...],
                'vehicles': [('standard_kart.png', 'http://example.com/kart.png'), ...],
                ...
            }
    """
    base_path = Path("../images")
    
    for category, images in url_dict.items():
        for filename, url in images:
            save_path = base_path / category / filename
            download_image(url, str(save_path))

if __name__ == "__main__":
    images_to_download = {
        "characters": [
            ("mario.png", "https://mk8dxbuilder.com/img/drivers/Mario.png"),
            ("luigi.png", "https://mk8dxbuilder.com/img/drivers/Luigi.png"),
            ("peach.png", "https://mk8dxbuilder.com/img/drivers/Peach.png"),
            ("daisy.png", "https://mk8dxbuilder.com/img/drivers/Daisy.png"),
            ("rosalina.png", "https://mk8dxbuilder.com/img/drivers/Rosalina.png"),
            ("tanooki_mario.png", "https://mk8dxbuilder.com/img/drivers/Tanooki%20Mario.png"),
            ("cat_peach.png", "https://mk8dxbuilder.com/img/drivers/Cat%20Peach.png"),
            ("yoshi.png", "https://mk8dxbuilder.com/img/drivers/Yoshi.png"),
            ("toad.png", "https://mk8dxbuilder.com/img/drivers/Toad.png"),
            ("koopa_troopa.png", "https://mk8dxbuilder.com/img/drivers/Koopa%20Troopa.png"),
            ("shy_guy.png", "https://mk8dxbuilder.com/img/drivers/Shy%20Guy.png"),
            ("lakitu.png", "https://mk8dxbuilder.com/img/drivers/Lakitu.png"),
            ("toadette.png", "https://mk8dxbuilder.com/img/drivers/Toadette.png"),
            ("king_boo.png", "https://mk8dxbuilder.com/img/drivers/King%20Boo.png"),
            ("baby_mario.png", "https://mk8dxbuilder.com/img/drivers/Baby%20Mario.png"),
            ("baby_luigi.png", "https://mk8dxbuilder.com/img/drivers/Baby%20Luigi.png"),
            ("baby_peach.png", "https://mk8dxbuilder.com/img/drivers/Baby%20Peach.png"),
            ("baby_daisy.png", "https://mk8dxbuilder.com/img/drivers/Baby%20Daisy.png"),
            ("baby_rosalina.png", "https://mk8dxbuilder.com/img/drivers/Baby%20Rosalina.png"),
            ("metal_mario.png", "https://mk8dxbuilder.com/img/drivers/Metal%20Mario.png"),
            ("pink_gold_peach.png", "https://mk8dxbuilder.com/img/drivers/Pink%20Gold%20Peach.png"),
            ("wario.png", "https://mk8dxbuilder.com/img/drivers/Wario.png"),
            ("waluigi.png", "https://mk8dxbuilder.com/img/drivers/Waluigi.png"),
            ("donkey_kong.png", "https://mk8dxbuilder.com/img/drivers/Donkey%20Kong.png"),
            ("bowser.png", "https://mk8dxbuilder.com/img/drivers/Bowser.png"),
            ("dry_bones.png", "https://mk8dxbuilder.com/img/drivers/Dry%20Bones.png"),
            ("bowser_jr.png", "https://mk8dxbuilder.com/img/drivers/Bowser%20Jr.png"),
            ("dry_bowser.png", "https://mk8dxbuilder.com/img/drivers/Dry%20Bowser.png"),
            ("lemmy.png", "https://mk8dxbuilder.com/img/drivers/Lemmy.png"),
            ("larry.png", "https://mk8dxbuilder.com/img/drivers/Larry.png"),
            ("wendy.png", "https://mk8dxbuilder.com/img/drivers/Wendy.png"),
            ("ludwig.png", "https://mk8dxbuilder.com/img/drivers/Ludwig.png"),
            ("iggy.png", "https://mk8dxbuilder.com/img/drivers/Iggy.png"),
            ("roy.png", "https://mk8dxbuilder.com/img/drivers/Roy.png"),
            ("morton.png", "https://mk8dxbuilder.com/img/drivers/Morton.png"),
            ("inkling_girl.png", "https://mk8dxbuilder.com/img/drivers/Inkling%20Girl.png"),
            ("inkling_boy.png", "https://mk8dxbuilder.com/img/drivers/Inkling%20Boy.png"),
            ("link.png", "https://mk8dxbuilder.com/img/drivers/Link.png"),
            ("villager_m.png", "https://mk8dxbuilder.com/img/drivers/Villager%20(M).png"),
            ("villager_f.png", "https://mk8dxbuilder.com/img/drivers/Villager%20(F).png"),
            ("isabelle.png", "https://mk8dxbuilder.com/img/drivers/Isabelle.png"),
            ("mii.png", "https://mk8dxbuilder.com/img/drivers/Mii.png"),
        ],
        "vehicles": [
            ("standard_kart.png", "https://mk8dxbuilder.com/img/bodies/Standard%20Kart.png"),
            ("pipe_frame.png", "https://mk8dxbuilder.com/img/bodies/Pipe%20Frame.png"),
            ("mach_8.png", "https://mk8dxbuilder.com/img/bodies/Mach%208.png"),
            ("steel_driver.png", "https://mk8dxbuilder.com/img/bodies/Steel%20Driver.png"),
            ("cat_cruiser.png", "https://mk8dxbuilder.com/img/bodies/Cat%20Cruiser.png"),
            ("circuit_special.png", "https://mk8dxbuilder.com/img/bodies/Circuit%20Special.png"),
            ("tri_speeder.png", "https://mk8dxbuilder.com/img/bodies/Tri-Speeder.png"),
            ("badwagon.png", "https://mk8dxbuilder.com/img/bodies/Badwagon.png"),
            ("prancer.png", "https://mk8dxbuilder.com/img/bodies/Prancer.png"),
            ("biddybuggy.png", "https://mk8dxbuilder.com/img/bodies/Biddybuggy.png"),
            ("landship.png", "https://mk8dxbuilder.com/img/bodies/Landship.png"),
            ("sneeker.png", "https://mk8dxbuilder.com/img/bodies/Sneeker.png"),
            ("sports_coupe.png", "https://mk8dxbuilder.com/img/bodies/Sports%20Coupe.png"),
            ("gold_standard.png", "https://mk8dxbuilder.com/img/bodies/Gold%20Standard.png"),
            ("standard_bike.png", "https://mk8dxbuilder.com/img/bodies/Standard%20Bike.png"),
            ("comet.png", "https://mk8dxbuilder.com/img/bodies/Comet.png"),
            ("sport_bike.png", "https://mk8dxbuilder.com/img/bodies/Sport%20Bike.png"),
            ("the_duke.png", "https://mk8dxbuilder.com/img/bodies/The%20Duke.png"),
            ("flame_rider.png", "https://mk8dxbuilder.com/img/bodies/Flame%20Rider.png"),
            ("varmint.png", "https://mk8dxbuilder.com/img/bodies/Varmint.png"),
            ("mr_scooty.png", "https://mk8dxbuilder.com/img/bodies/Mr%20Scooty.png"),
            ("jet_bike.png", "https://mk8dxbuilder.com/img/bodies/Jet%20Bike.png"),
            ("yoshi_bike.png", "https://mk8dxbuilder.com/img/bodies/Yoshi%20Bike.png"),
        ],
        "tires": [
            ("standard.png", "https://mk8dxbuilder.com/img/tires/Standard.png"),
            ("monster.png", "https://mk8dxbuilder.com/img/tires/Monster.png"),
            ("roller.png", "https://mk8dxbuilder.com/img/tires/Roller.png"),
            ("slim.png", "https://mk8dxbuilder.com/img/tires/Slim.png"),
            ("slick.png", "https://mk8dxbuilder.com/img/tires/Slick.png"),
            ("metal.png", "https://mk8dxbuilder.com/img/tires/Metal.png"),
            ("button.png", "https://mk8dxbuilder.com/img/tires/Button.png"),
            ("off_road.png", "https://mk8dxbuilder.com/img/tires/Off-Road.png"),
            ("sponge.png", "https://mk8dxbuilder.com/img/tires/Sponge.png"),
            ("wood.png", "https://mk8dxbuilder.com/img/tires/Wood.png"),
            ("cushion.png", "https://mk8dxbuilder.com/img/tires/Cushion.png"),
            ("blue_standard.png", "https://mk8dxbuilder.com/img/tires/Blue%20Standard.png"),
            ("hot_monster.png", "https://mk8dxbuilder.com/img/tires/Hot%20Monster.png"),
            ("azure_roller.png", "https://mk8dxbuilder.com/img/tires/Azure%20Roller.png"),
            ("crimson_slim.png", "https://mk8dxbuilder.com/img/tires/Crimson%20Slim.png"),
            ("cyber_slick.png", "https://mk8dxbuilder.com/img/tires/Cyber%20Slick.png"),
        ],
        "gliders": [
            ("super_glider.png", "https://mk8dxbuilder.com/img/gliders/Super%20Glider.png"),
            ("cloud_glider.png", "https://mk8dxbuilder.com/img/gliders/Cloud%20Glider.png"),
            ("wario_wing.png", "https://mk8dxbuilder.com/img/gliders/Wario%20Wing.png"),
            ("waddle_wing.png", "https://mk8dxbuilder.com/img/gliders/Waddle%20Wing.png"),
            ("peach_parasol.png", "https://mk8dxbuilder.com/img/gliders/Peach%20Parasol.png"),
            ("parachute.png", "https://mk8dxbuilder.com/img/gliders/Parachute.png"),
            ("parafoil.png", "https://mk8dxbuilder.com/img/gliders/Parafoil.png"),
            ("flower_glider.png", "https://mk8dxbuilder.com/img/gliders/Flower%20Glider.png"),
            ("bowser_kite.png", "https://mk8dxbuilder.com/img/gliders/Bowser%20Kite.png"),
            ("plane_glider.png", "https://mk8dxbuilder.com/img/gliders/Plane%20Glider.png"),
            ("mktv_parafoil.png", "https://mk8dxbuilder.com/img/gliders/MKTV%20Parafoil.png"),
            ("gold_glider.png", "https://mk8dxbuilder.com/img/gliders/Gold%20Glider.png"),
            ("paper_glider.png", "https://mk8dxbuilder.com/img/gliders/Paper%20Glider.png"),
        ],
    }
    
    download_images(images_to_download) 