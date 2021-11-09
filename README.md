# SM4_image_crypto
encrypt/decrypt image via SM4 algorithm ECB/CBC mode

### Code structure 

##### main.py

该文件主要包含程序的几个部分：图像读入为字节流，系统参数的输入与处理，字节流生成图像

图像读为字节流部分，采用PIL的Image组件进行png的图像读入：

```python
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
```

返回图像的数据以及大小。

系统参数的输入与处理部分负责参数的识别与检测，并且根据参数选择执行分支：

```python
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
```



系统输入的参数有三个，分别为待处理图像的路径，加密模式（ECB或CBC以及加密或解密），最后是密钥的输入，之后根据读入的参数进行执行分支的选择：

```python
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
```

最后通过加密/解密后的字节流分析，生成图像：

```python
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
```

##### sm4.py

首先是根据输入的足够长的口令生成用于加密的密钥：

```python
def gen_key_encrypt(key):
    sk = [0]*32
    key = byte2list(bytes(key,'utf-8'))
    MK = [0, 0, 0, 0]
    k = [0]*36
    for i in range(4):
        MK[i] = byte2int(key[i*4:i*4+4])
    k[0:4] = xor(MK[0:4], FK[0:4])
    for i in range(32):
        k[i + 4] = k[i] ^ round_key(k[i + 1] ^ k[i + 2] ^ k[i + 3] ^ CK[i])
        sk[i] = k[i + 4]
    return sk
```

```python
def gen_key_decrypt(key):
    sk = gen_key_encrypt(key)
    for idx in range(16):
        t = sk[idx]
        sk[idx] = sk[31 - idx]
        sk[31 - idx] = t
    return sk
```

接着根据生成的密钥分加密模式和加解密选择进行处理，这里选择ECB和CBC的加密进行展示：

ECB加密模块：

```python
def encrypt_ECB(bytes, key):
    sk = gen_key_encrypt(key)
    data_p = padding(byte2list(bytes))
    out_bytes = []
    for i in range(0, len(data_p), 16):
        out_bytes += one_round(data_p[i:i+16], sk)
    return list2byte(out_bytes)
```

CBC加密模块：

```python
def encrypt_CBC(bytes, key):
    iv = byte2list(b'\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00')
    tmp = [0]*16
    sk = gen_key_encrypt(key)
    out_bytes = []
    data_p = padding(byte2list(bytes))
    for i in range(0, len(data_p), 16):
        tmp[0:16] = xor(data_p[i:i+16], iv[0:16])
        out_bytes += one_round(tmp[0:16], sk)
        iv = copy.deepcopy(out_bytes[i:i+16])
    return list2byte(out_bytes)
```

### Usage

使用命令行进行图像加密，输入格式及样例如下：

```bash
python3 main.py {img_path} {encrypt_mode} {encrypt_key}
```

如果采用ECB模式加密图像"logo.png"，密钥为"qwertyuiopasdfghjkl"的话，应键入如下命令：

```bash
python3 main.py logo.png ECB1 qwertyuiopasdfghjkl
```

如果采用ECB模式解密图像"logo_ECB_encrypt.png"，密钥为"qwertyuiopasdfghjkl"的话，应键入如下命令：

```bash
python3 main.py logo_ECB_encrypt.png ECB0 qwertyuiopasdfghjkl
```

如果采用CBC模式加密图像"logo.png"，密钥为"qwertyuiopasdfghjkl"的话，应键入如下命令：

```bash
python3 main.py logo.png CBC1 qwertyuiopasdfghjkl
```

如果采用CBC模式解密图像"logo_CBC_encrypt.png"，密钥为"qwertyuiopasdfghjkl"的话，应键入如下命令：

```bash
python3 main.py logo_CBC_encrypt.png CBC0 qwertyuiopasdfghjkl
```

运行截图如下：

ECB加解密：

```bash
(venv) (base) JiangJundeMacBook-Pro:SM4 jiangjun$ python3 main.py logo.png ECB1 qwertyuiopasdfghjkl
[Note] Please input [img_path] [crypt_mode] [key]
[Note] Example input: {logo.png ECB1 123}
[Running] input checking finished!
[Running] begin processing!
[Running] encrypt/decrypt process finished!
[Finished] gengrate image logo_ECB_encrypt.png

(venv) (base) JiangJundeMacBook-Pro:SM4 jiangjun$ python3 main.py logo_ECB_encrypt.png ECB0 qwertyuiopasdfghjkl
[Note] Please input [img_path] [crypt_mode] [key]
[Note] Example input: {logo.png ECB1 123}
[Running] input checking finished!
[Running] begin processing!
[Running] encrypt/decrypt process finished!
[Finished] gengrate image logo_ECB_encrypt_ECB_decrypt.png
```

CBC加解密：

```bash
(venv) (base) JiangJundeMacBook-Pro:SM4 jiangjun$ python3 main.py logo.png CBC1 qwertyuiopasdfghjkl
[Note] Please input [img_path] [crypt_mode] [key]
[Note] Example input: {logo.png ECB1 123}
[Running] input checking finished!
[Running] begin processing!
[Running] encrypt/decrypt process finished!
[Finished] gengrate image logo_CBC_encrypt.png

(venv) (base) JiangJundeMacBook-Pro:SM4 jiangjun$ python3 main.py logo_CBC_encrypt.png CBC0 qwertyuiopasdfghjkl
[Note] Please input [img_path] [crypt_mode] [key]
[Note] Example input: {logo.png ECB1 123}
[Running] input checking finished!
[Running] begin processing!
[Running] encrypt/decrypt process finished!
[Finished] gengrate image logo_CBC_encrypt_CBC_decrypt.png
```





