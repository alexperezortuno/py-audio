
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
python -m tts -t "¡Hola como estas! " -p true --to-lang es --output su_num_es
python -m tts -t "¡Hola como estas! " -p true -l es --output su_num_es -f wav
python -m tts -t "¡Hola como estas! " -l es -s 8000 -c 1 -f wav --output su_num_es -b 160
```

---

### Usage Translator

declare the environment variable `OPENAI_API_KEY`
declare the environment variable `DEEPSEEK_API_KEY`

example for your idle:

```
PYTHONUNBUFFERED=1;OPENAI_API_KEY=<OPENAPI_API_VALUE>;DEEPSEEK_API_KEY=<DEEPSEEK_API_VALUE>
```

if you are using bash, you can use the following command:

```shell
export PYTHONUNBUFFERED=1; export OPENAI_API_KEY=<OPENAPI_API_VALUE>; export DEEPSEEK_API_KEY=<DEEPSEEK_API_VALUE> && python -m translator
```

```shell
python -m translator
```

```shell
python -m translator --service openai --to-lang es  # Use OpenAI
```

```shell
python -m translator --service deepseek --to-lang es  # Use DeepSeek
```

```shell
python -m translator --service deepseek --to-lang es -t "Am I wasting my life on a theory that can never be proven? Maybe, but how great is Game of Thrones? "
```
```shell
python -m translator --service deepseek --record --to-lang en --chunk-duration 10 # Record the translation
```

```shell
python -m translator --service deepseek --record --continuous --from-lang es --to-lang en --chunk-duration 10 # Record the translation continuously
```

```shell
python -m translator --service deepseek -r --from-lang es --to-lang en --chunk-duration 5
```

| Argument         | Description                                                        |
|------------------|--------------------------------------------------------------------|
| --service        | The service to use for translation. Options: `openai`, `deepseek`. |
| --to-lang        | The language to translate to.                                      |
 | --from-lag       | The language from translate                                        |
| --record         | Record the translation.                                            |
| --continuous     | Record the translation continuously.                               |
| --chunk-duration | The duration of each chunk in seconds.                             |
| --output         | The output file name.                                              |
| --format         | The format of the output file. Options: `wav`, `mp3`.              |

