# AP Save Data Client
This is a weird thing that I might be the only audience for.

I really like playing LADX on my Miyoo Mini Plus,
I also like to play Archipelago asyncs.

The Miyoo can't handle a connection to the normal client,
so I had this idea to build a client that runs off of the save file instead.

So, this client will read a save file,
check in with an Archipelago room,
and rewrite the save file with updates.

## Usage
- Edit `config.yaml` to your needs
- `pip install -r src/requirements.txt`
- `python src/main.py config.yaml`

## Notes
A main thing missing is that in a lot of cases, the save file won't be able
to tell you if the goal has been completed. I might try to mod a flag into LADX
in the future.