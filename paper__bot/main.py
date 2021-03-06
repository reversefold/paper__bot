import asyncio
import logging

import discord
import twitchbot
from twitchbot.util import twitch_api_util

LOG = logging.getLogger(__name__)


class PaperTwitchBot(twitchbot.BaseBot):
    pass


@twitchbot.Command("so", help="shoutout!", syntax="<channel>", permission="so")
async def shoutout(msg: twitchbot.Message, *args):
    if not args:
        return
    channel_name = args[0]
    if not channel_name:
        return
    if channel_name[0] == "@":
        channel_name = channel_name[1:]
    so_msg = f"Go check out https://twitch.tv/{channel_name}"
    try:
        channel_info = await twitch_api_util.get_channel_info(channel_name)
        if channel_info:
            if channel_info.game_name:
                so_msg += f", last seen in the {channel_info.game_name} category"
            else:
                LOG.error(f"No game name for channel {channel_name}")
        else:
            LOG.error(f"No data found for channel {channel_name}")
    except Exception:
        LOG.exception(f"Exception getting channel info for {channel_name}")
    await msg.reply(so_msg)


class PaperDiscordBot(discord.Client):
    async def on_connect(self):
        LOG.info("Connected")

    async def on_ready(self):
        LOG.info(f"Logged on as {self.user}")

    async def on_guild_join(self, guild):
        LOG.info(f"Joined guild {guild.name}")

    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            to_send = f"Welcome {member.mention} to {guild.name}!"
            await guild.system_channel.send(to_send)

    async def on_message(self, message):
        LOG.info("Message from {0.author}: {0.content}".format(message))


def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO
    )

    discord_config = twitchbot.Config(
        twitchbot.CONFIG_FOLDER / "discordbot.json",
    )

    loop = asyncio.get_event_loop()
    try:
        intents = discord.Intents()  # .default()
        intents.guilds = True
        intents.members = True
        discord_bot = PaperDiscordBot(intents=intents)
        try:
            loop.create_task(PaperTwitchBot().mainloop())
            loop.create_task(discord_bot.start(discord_config.bot_token))
            # import ipdb; ipdb.set_trace()
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(discord_bot.close())
    finally:
        loop.close()


if __name__ == "__main__":
    main()
