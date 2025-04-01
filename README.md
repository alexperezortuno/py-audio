
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

### Usage TTS

```shell
python -m tts -t "¡Hi, how are you doing! " -p true
python -m tts -t "¡Hola como estas! " -p true -l es
python -m tts -t "¡Hola como estas! " -p true -l es
python -m tts -t "¡Hola como estas! " -p true -l es --output su_num_es
python -m tts -t "¡Hola como estas! " -p true -l es --output su_num_es -f wav
python -m tts -t "¡Hola como estas! " -l es -s 8000 -c 1 -f wav --output su_num_es -b 160
```

---

### Usage Translator

declare the environment variable `OPENAI_API_KEY`
declare the environment variable `DEEPSEEK_API_KEY`

```shell
python -m translator
```

```shell
python -m translator --service openai --language es  # Usa OpenAI
python -m translator --service deepseek --language es  # Usa DeepSeek
```

```shell
python -m translator --service deepseek --language es -t "Am I wasting my life on a theory that can never be proven? Maybe, but how great is Game of Thrones? "
```


