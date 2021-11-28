from bot.lib import bot
import uvloop
import os

if os.name != "nt":
    import uvloop

    uvloop.install()

if __name__ == "__main__":
    bot.run()
