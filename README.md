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
- https://github.com/python-hyper/wsproto
- https://github.com/python-hyper/h11

You can just `pip install wsproto` and get both, but retro handhelds tend not
to have pip so you can just drop them into `src`.

## Usage
- Prepare a `config.json` to your needs
- `python src/main.py config.json`

## config.json
```json
{
    "rooms": [
        "<url>"
    ]
}
```

## Notes
A main thing missing is that in a lot of cases, the save file won't be able
to tell you if the goal has been completed. I might try to mod a flag into LADX
in the future.