import os.path
import sys
from PIL import Image, ImageDraw
import sm4


# convert the png file to list<int>
def read_png(png_path):
    stream_raw = []
    png = Image.open(png_path)
    width = png.size[0]
    height = png.size[1]

    rgb = png.convert('RGB')
    for i in range(width):
        for j in range(height):
            r, g, b = rgb.getpixel((i, j))
            stream_raw.append(r)
            stream_raw.append(g)
            stream_raw.append(b)
    return stream_raw, width, height


def generate_png(bytes, width, height, png_path):
    int_list = []
    pixel_list = []
    for b in bytes:
        int_list.append(int(b))
    for i in range(0,width*height*3,3):
        pixel_list.append((int_list[i],int_list[i+1],int_list[i+2]))
    image_out = Image.new('RGB', (width,height), (255,255,255))
    draw = ImageDraw.Draw(image_out)
    cnt = 0
    for i in range(width):
        for j in range(height):
            draw.point((i, j),fill=pixel_list[cnt])
            cnt = cnt + 1
    image_out.save(png_path,'png')


if __name__ == '__main__':
    print("[Note] Please input [img_path] [crypt_mode] [key]")
    print("[Note] Example input: {logo.png ECB1 123}")

    # read in the pngfile to generate the pixel list
    image_raw_path = sys.argv[1]
    stream_raw_int, width, height = read_png(image_raw_path)
    #convert the pixel list to bytes
    raw_bytes = bytes(stream_raw_int)

    encrypt_mode = sys.argv[2]
    key = sys.argv[3]

    if len(image_raw_path) == 0:
        print("[Error] image address not valid!")
        sys.exit(1)
    if len(key) < 16:
        print("[Error] too short key!")
        sys.exit(1)

    print("[Running] input checking finished!")
    print("[Running] begin processing!")
    if encrypt_mode == "ECB1":
        #encrypt the bytes by SM4_ECB
        out_bytes = sm4.encrypt_ECB(raw_bytes, key)
        out_name = os.path.splitext(image_raw_path)[0] + "_ECB_encrypt.png"
    elif encrypt_mode == "ECB0":
        #decrypt the bytes by SM4_ECB
        out_bytes = sm4.decrypt_ECB(raw_bytes, key)
        out_name = os.path.splitext(image_raw_path)[0] + "_ECB_decrypt.png"
    elif encrypt_mode == "CBC1":
        #encrypt the bytes by SM4_CBC
        out_bytes = sm4.encrypt_CBC(raw_bytes, key)
        out_name = os.path.splitext(image_raw_path)[0] + "_CBC_encrypt.png"
    elif encrypt_mode == "CBC0":
        #decrypt the bytes by SM4_CBC
        out_bytes = sm4.decrypt_CBC(raw_bytes, key)
        out_name = os.path.splitext(image_raw_path)[0] + "_CBC_decrypt.png"

    print("[Running] encrypt/decrypt process finished!")
    #convert the bytes to pixel list
    generate_png(out_bytes, width, height, out_name)
    print("[Finished] gengrate image " + out_name + "\n")


