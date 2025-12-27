from nonebot import get_plugin_config, on_regex
from nonebot.params import RegexDict

from nonebot_plugin_nearcade_reporter.config import Config
from nonebot_plugin_nearcade_reporter.network import NearcadeHttp

config = get_plugin_config(Config)
nearcade = NearcadeHttp(config.api_token)

print(f"config pattern: {config.update_attendance_match.pattern}")

arcade_attendance = on_regex(config.update_attendance_match.pattern)


@arcade_attendance.handle()
async def _(args: dict[str, str] = RegexDict()):
    arcade_matcher = config.update_attendance_match.arcade_group_name
    count_matcher = config.update_attendance_match.count_group_name
    arcade_name = args.get(arcade_matcher)
    if not arcade_name:
        ...  # Should not happen due to regex
    count = args.get(count_matcher)
    if not count:
        ...  # Should not happen due to regex
    arcade_id = config.find_arcade_by_alias(arcade_name)
    if arcade_id[0] == -1:
        await arcade_attendance.finish(f"未找到机厅：{arcade_name}")
    await nearcade.update_attendance(arcade_name, int(count))
    reply_msg = config.update_attendance_match.reply_message.format(
        arcade_name=arcade_name, count=count
    )
    await arcade_attendance.finish(f"{reply_msg}")
