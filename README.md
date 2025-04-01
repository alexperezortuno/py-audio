
### Requirements

```shell
pip install -r requirements.txt
```

### Ubuntu

```shell
 sudo apt install libportaudio2
```

if you use conda, you can install it with:

```shell
conda install -c conda-forge gcc=12.1.0
```

---

### Usage

```shell
python -m tts -t "¡Hi, how are you doing! " -p true
python -m tts -t "¡Hola como estas! " -p true -l es
python -m tts -t "¡Hola como estas! " -p true -l es
python -m tts -t "¡Hola como estas! " -p true -l es --output su_num_es
python -m tts -t "¡Hola como estas! " -p true -l es --output su_num_es -f wav
python -m tts -t "¡Hola como estas! " -l es -s 8000 -c 1 -f wav --output su_num_es -b 160
```
