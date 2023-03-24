'''
Gather classes for Typing
'''
from typing import TypeAlias

from .channels import channelbase, channels

DBQuie:TypeAlias=channels.DBQuie
Channel:TypeAlias=channels.Channel
ChannelBase:TypeAlias=channelbase.ChannelsBase