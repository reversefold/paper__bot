import re

from twitchbot import PubSubTopics, Mod, get_pubsub
import twitchbot
import twitchbot.pubsub.models
import twitchbot.pubsub.pubsub_follow
import twitchbot.channel


config = twitchbot.Config(
    twitchbot.CONFIG_FOLDER / 'follower_autoban.json',
    ban_regexes=[{"regex": r"^h[o0][s5][s5].*312.*$", "flags": 2}],
)


class PubSubSubscriberMod(Mod):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        ban_regexes = config.ban_regexes
        if not ban_regexes:
            ban_regexes = []
        elif not isinstance(ban_regexes, list):
            ban_regexes = [ban_regexes]
        self.ban_regexes = [re.compile(r["regex"], r.get("flags")) for r in ban_regexes]

    async def on_connected(self):
        for channel_name, channel_config in config.channels.items():
            await get_pubsub().listen_to_channel(
                channel_name,
                [PubSubTopics.follows],
                access_token=channel_config["access_token"],
            )

    async def on_pubsub_received(self, raw: "PubSubData"):
        # this should print any errors received from twitch
        print(raw.raw_data)

    async def on_pubsub_user_follow(
        self,
        raw: twitchbot.models.PubSubData,
        data: twitchbot.pubsub.pubsub_follow.PubSubFollow,
    ):
        print(twitchbot.channel.channels)
        print(f"New follower {data.follower_username} {data.follower_id}")
        for ban_re in self.ban_regexes:
            if ban_re.match(data.follower_username):
                print(f"Banning {data.follower_username} ({data.follower_id})")
                channel = await data.get_channel()
                await channel.send_command(f"ban {data.follower_username}")
