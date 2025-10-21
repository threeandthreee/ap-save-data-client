# AP Save Data Client
This is a weird thing that I might be the only audience for.

I really like playing LADX on my Miyoo Mini Plus,
I also like to play Archipelago asyncs.

The Miyoo can't handle a connection to the normal client,
so I had this idea to build a client that runs off of the save file instead.

So, this client will read a save file,
check in with an Archipelago room,
and rewrite the save file with updates.

## Libraries
Retro handhelds tend not to have pip so I went with pure python libraries.
Use `build.py` to collect dependencies.

## Usage
- Prepare a json config file to your needs
- `python src/main.py path/to/config.json`

## Usage on retro handheld
- Ensure your handheld can run python 3
- `python build.py` to collect dependencies.
- Place contents of src on device somewhere.
- Prepare a json config file to your needs, place on device.
- Set up a shell script to run the sync script. Where you place it will depend on the device/firmware.

Example shell script:
``` bash
#! /bin/bash
python /path/to/ap-save-data-client/main.py /path/to/config.json
```

## Config Example
``` json
{
    "base": {
        "host": "archipelago.gg",
        "base_path": "/path/to/your/saves/"
    },
    "games": [
        {
            "label": "my example game",
            "port": 12345,
            "name": "Player1",
            "password": "secret",
            "handler": "ladx",
            "save_file": "path/from/base_path/to/save_file.srm"
        }
    ]
}
```

The base object is optional, each game object gets merged onto it when processed, so you can set common options.
