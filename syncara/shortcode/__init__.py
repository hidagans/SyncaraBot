from .group_management import GroupManagementShortcode
from .users_management import UserManagementShortcode
from .userbot_management import UserbotManagementShortcode
from .music_management import MusicManagementShortcode

# Initialize all shortcode handlers
group_management = GroupManagementShortcode()
user_management = UserManagementShortcode()
userbot_management = UserbotManagementShortcode()
music_management = MusicManagementShortcode()

# Combine all handlers
SHORTCODE_HANDLERS = {}
SHORTCODE_HANDLERS.update(group_management.handlers)
SHORTCODE_HANDLERS.update(user_management.handlers)
SHORTCODE_HANDLERS.update(userbot_management.handlers)
SHORTCODE_HANDLERS.update(music_management.handlers)

# Combine all descriptions
SHORTCODE_DESCRIPTIONS = {}
SHORTCODE_DESCRIPTIONS.update(group_management.descriptions)
SHORTCODE_DESCRIPTIONS.update(user_management.descriptions)
SHORTCODE_DESCRIPTIONS.update(userbot_management.descriptions)
SHORTCODE_DESCRIPTIONS.update(music_management.descriptions)