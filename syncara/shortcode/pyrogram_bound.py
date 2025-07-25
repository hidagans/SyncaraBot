# syncara/shortcode/pyrogram_bound.py
"""
Shortcode untuk bound methods Pyrogram.
"""

from syncara.console import console
import asyncio
import json
from datetime import datetime
from pyrogram import types

class PyrogramBoundShortcode:
    def __init__(self):
        self.handlers = {
            'PYROGRAM:CHAT_ARSIP': self.chat_arsip,
            'PYROGRAM:CHAT_UNARSIP': self.chat_unarsip,
            'PYROGRAM:CHAT_SET_JUDUL': self.chat_set_judul,
            'PYROGRAM:CHAT_SET_DESKRIPSI': self.chat_set_deskripsi,
            'PYROGRAM:CHAT_SET_FOTO': self.chat_set_foto,
            'PYROGRAM:CHAT_HAPUS_FOTO': self.chat_hapus_foto,
            'PYROGRAM:CHAT_BAN_MEMBER': self.chat_ban_member,
            'PYROGRAM:CHAT_UNBAN_MEMBER': self.chat_unban_member,
            'PYROGRAM:CHAT_RESTRICT_MEMBER': self.chat_restrict_member,
            'PYROGRAM:CHAT_PROMOTE_MEMBER': self.chat_promote_member,
            'PYROGRAM:CHAT_GET_MEMBER': self.chat_get_member,
            'PYROGRAM:CHAT_GET_MEMBERS': self.chat_get_members,
            'PYROGRAM:CHAT_ADD_MEMBERS': self.chat_add_members,
            'PYROGRAM:CHAT_JOIN': self.chat_join,
            'PYROGRAM:CHAT_LEAVE': self.chat_leave,
            'PYROGRAM:CHAT_MARK_UNREAD': self.chat_mark_unread,
            'PYROGRAM:CHAT_SET_PROTECTED': self.chat_set_protected,
            'PYROGRAM:CHAT_UNPIN_ALL': self.chat_unpin_all,
            'PYROGRAM:CHAT_DELETE': self.chat_delete,
            'PYROGRAM:CHAT_SET_SLOW_MODE': self.chat_set_slow_mode,
            'PYROGRAM:CHAT_GET_ONLINE_COUNT': self.chat_get_online_count,
            'PYROGRAM:CHAT_GET_EVENT_LOG': self.chat_get_event_log,
            'PYROGRAM:CHAT_BACKUP': self.chat_backup,
            'PYROGRAM:MESSAGE_REPLY_TEXT': self.message_reply_text,
            'PYROGRAM:MESSAGE_REPLY_PHOTO': self.message_reply_photo,
            'PYROGRAM:MESSAGE_REPLY_VIDEO': self.message_reply_video,
            'PYROGRAM:MESSAGE_REPLY_AUDIO': self.message_reply_audio,
            'PYROGRAM:MESSAGE_REPLY_DOCUMENT': self.message_reply_document,
            'PYROGRAM:MESSAGE_EDIT_TEXT': self.message_edit_text,
            'PYROGRAM:MESSAGE_EDIT_CAPTION': self.message_edit_caption,
            'PYROGRAM:MESSAGE_EDIT_MEDIA': self.message_edit_media,
            'PYROGRAM:MESSAGE_DELETE': self.message_delete,
            'PYROGRAM:MESSAGE_FORWARD': self.message_forward,
            'PYROGRAM:MESSAGE_COPY': self.message_copy,
            'PYROGRAM:MESSAGE_PIN': self.message_pin,
            'PYROGRAM:MESSAGE_UNPIN': self.message_unpin,
            'PYROGRAM:MESSAGE_DOWNLOAD_MEDIA': self.message_download_media,
            'PYROGRAM:MESSAGE_CLICK_INLINE_BUTTON': self.message_click_inline_button,
            'PYROGRAM:USER_GET_COMMON_CHATS': self.user_get_common_chats,
            'PYROGRAM:USER_GET_PROFILE_PHOTOS': self.user_get_profile_photos,
            'PYROGRAM:USER_BLOCK': self.user_block,
            'PYROGRAM:USER_UNBLOCK': self.user_unblock,
            'PYROGRAM:USER_SEND_MESSAGE': self.user_send_message,
            'PYROGRAM:USER_SEND_PHOTO': self.user_send_photo,
            'PYROGRAM:INLINE_QUERY_ANSWER': self.inline_query_answer,
            'PYROGRAM:JOIN_REQUEST_APPROVE': self.join_request_approve,
            'PYROGRAM:JOIN_REQUEST_DECLINE': self.join_request_decline,
            'PYROGRAM:JOIN_REQUEST_APPROVE_ALL': self.join_request_approve_all,
            'PYROGRAM:JOIN_REQUEST_DECLINE_ALL': self.join_request_decline_all,
        }
        
        self.descriptions = {
            'PYROGRAM:CHAT_ARSIP': 'Arsipkan chat ini. Usage: [PYROGRAM:CHAT_ARSIP:]',
            'PYROGRAM:CHAT_UNARSIP': 'Batal arsipkan chat ini. Usage: [PYROGRAM:CHAT_UNARSIP:]',
            'PYROGRAM:CHAT_SET_JUDUL': 'Set judul chat. Usage: [PYROGRAM:CHAT_SET_JUDUL:title]',
            'PYROGRAM:CHAT_SET_DESKRIPSI': 'Set deskripsi chat. Usage: [PYROGRAM:CHAT_SET_DESKRIPSI:description]',
            'PYROGRAM:CHAT_SET_FOTO': 'Set foto chat. Usage: [PYROGRAM:CHAT_SET_FOTO:photo]',
            'PYROGRAM:CHAT_HAPUS_FOTO': 'Hapus foto chat. Usage: [PYROGRAM:CHAT_HAPUS_FOTO:]',
            'PYROGRAM:CHAT_BAN_MEMBER': 'Ban member dari chat. Usage: [PYROGRAM:CHAT_BAN_MEMBER:user_id]',
            'PYROGRAM:CHAT_UNBAN_MEMBER': 'Unban member dari chat. Usage: [PYROGRAM:CHAT_UNBAN_MEMBER:user_id]',
            'PYROGRAM:CHAT_RESTRICT_MEMBER': 'Restrict member di chat. Usage: [PYROGRAM:CHAT_RESTRICT_MEMBER:user_id]',
            'PYROGRAM:CHAT_PROMOTE_MEMBER': 'Promote member di chat. Usage: [PYROGRAM:CHAT_PROMOTE_MEMBER:user_id]',
            'PYROGRAM:CHAT_GET_MEMBER': 'Get info member chat. Usage: [PYROGRAM:CHAT_GET_MEMBER:user_id]',
            'PYROGRAM:CHAT_GET_MEMBERS': 'Get daftar member chat. Usage: [PYROGRAM:CHAT_GET_MEMBERS:filter]',
            'PYROGRAM:CHAT_ADD_MEMBERS': 'Add member ke chat. Usage: [PYROGRAM:CHAT_ADD_MEMBERS:user_ids]',
            'PYROGRAM:CHAT_JOIN': 'Join chat ini. Usage: [PYROGRAM:CHAT_JOIN:]',
            'PYROGRAM:CHAT_LEAVE': 'Leave chat ini. Usage: [PYROGRAM:CHAT_LEAVE:]',
            'PYROGRAM:CHAT_MARK_UNREAD': 'Mark chat sebagai belum dibaca. Usage: [PYROGRAM:CHAT_MARK_UNREAD:]',
            'PYROGRAM:CHAT_SET_PROTECTED': 'Set protected content chat. Usage: [PYROGRAM:CHAT_SET_PROTECTED:enabled]',
            'PYROGRAM:CHAT_UNPIN_ALL': 'Unpin semua pesan di chat. Usage: [PYROGRAM:CHAT_UNPIN_ALL:]',
            'PYROGRAM:CHAT_DELETE': 'Delete chat ini. Usage: [PYROGRAM:CHAT_DELETE:]',
            'PYROGRAM:CHAT_SET_SLOW_MODE': 'Set slow mode chat. Usage: [PYROGRAM:CHAT_SET_SLOW_MODE:seconds]',
            'PYROGRAM:CHAT_GET_ONLINE_COUNT': 'Get jumlah member online. Usage: [PYROGRAM:CHAT_GET_ONLINE_COUNT:]',
            'PYROGRAM:CHAT_GET_EVENT_LOG': 'Get event log chat. Usage: [PYROGRAM:CHAT_GET_EVENT_LOG:limit]',
            'PYROGRAM:CHAT_BACKUP': 'Backup chat ini. Usage: [PYROGRAM:CHAT_BACKUP:include_media]',
            'PYROGRAM:MESSAGE_REPLY_TEXT': 'Reply pesan dengan teks. Usage: [PYROGRAM:MESSAGE_REPLY_TEXT:text]',
            'PYROGRAM:MESSAGE_REPLY_PHOTO': 'Reply pesan dengan foto. Usage: [PYROGRAM:MESSAGE_REPLY_PHOTO:photo:caption]',
            'PYROGRAM:MESSAGE_REPLY_VIDEO': 'Reply pesan dengan video. Usage: [PYROGRAM:MESSAGE_REPLY_VIDEO:video:caption]',
            'PYROGRAM:MESSAGE_REPLY_AUDIO': 'Reply pesan dengan audio. Usage: [PYROGRAM:MESSAGE_REPLY_AUDIO:audio:caption]',
            'PYROGRAM:MESSAGE_REPLY_DOCUMENT': 'Reply pesan dengan dokumen. Usage: [PYROGRAM:MESSAGE_REPLY_DOCUMENT:document:caption]',
            'PYROGRAM:MESSAGE_EDIT_TEXT': 'Edit teks pesan. Usage: [PYROGRAM:MESSAGE_EDIT_TEXT:text]',
            'PYROGRAM:MESSAGE_EDIT_CAPTION': 'Edit caption pesan. Usage: [PYROGRAM:MESSAGE_EDIT_CAPTION:caption]',
            'PYROGRAM:MESSAGE_EDIT_MEDIA': 'Edit media pesan. Usage: [PYROGRAM:MESSAGE_EDIT_MEDIA:media]',
            'PYROGRAM:MESSAGE_DELETE': 'Delete pesan ini. Usage: [PYROGRAM:MESSAGE_DELETE:]',
            'PYROGRAM:MESSAGE_FORWARD': 'Forward pesan ke chat lain. Usage: [PYROGRAM:MESSAGE_FORWARD:chat_id]',
            'PYROGRAM:MESSAGE_COPY': 'Copy pesan ke chat lain. Usage: [PYROGRAM:MESSAGE_COPY:chat_id]',
            'PYROGRAM:MESSAGE_PIN': 'Pin pesan ini. Usage: [PYROGRAM:MESSAGE_PIN:]',
            'PYROGRAM:MESSAGE_UNPIN': 'Unpin pesan ini. Usage: [PYROGRAM:MESSAGE_UNPIN:]',
            'PYROGRAM:MESSAGE_DOWNLOAD_MEDIA': 'Download media dari pesan. Usage: [PYROGRAM:MESSAGE_DOWNLOAD_MEDIA:filename]',
            'PYROGRAM:MESSAGE_CLICK_INLINE_BUTTON': 'Click inline button. Usage: [PYROGRAM:MESSAGE_CLICK_INLINE_BUTTON:button_data]',
            'PYROGRAM:USER_GET_COMMON_CHATS': 'Get common chats dengan user. Usage: [PYROGRAM:USER_GET_COMMON_CHATS:user_id]',
            'PYROGRAM:USER_GET_PROFILE_PHOTOS': 'Get profile photos user. Usage: [PYROGRAM:USER_GET_PROFILE_PHOTOS:user_id]',
            'PYROGRAM:USER_BLOCK': 'Block user. Usage: [PYROGRAM:USER_BLOCK:user_id]',
            'PYROGRAM:USER_UNBLOCK': 'Unblock user. Usage: [PYROGRAM:USER_UNBLOCK:user_id]',
            'PYROGRAM:USER_SEND_MESSAGE': 'Kirim pesan ke user. Usage: [PYROGRAM:USER_SEND_MESSAGE:user_id:text]',
            'PYROGRAM:USER_SEND_PHOTO': 'Kirim foto ke user. Usage: [PYROGRAM:USER_SEND_PHOTO:user_id:photo:caption]',
            'PYROGRAM:INLINE_QUERY_ANSWER': 'Jawab inline query. Usage: [PYROGRAM:INLINE_QUERY_ANSWER:results]',
            'PYROGRAM:JOIN_REQUEST_APPROVE': 'Approve join request. Usage: [PYROGRAM:JOIN_REQUEST_APPROVE:user_id]',
            'PYROGRAM:JOIN_REQUEST_DECLINE': 'Decline join request. Usage: [PYROGRAM:JOIN_REQUEST_DECLINE:user_id]',
            'PYROGRAM:JOIN_REQUEST_APPROVE_ALL': 'Approve semua join request. Usage: [PYROGRAM:JOIN_REQUEST_APPROVE_ALL:]',
            'PYROGRAM:JOIN_REQUEST_DECLINE_ALL': 'Decline semua join request. Usage: [PYROGRAM:JOIN_REQUEST_DECLINE_ALL:]',
        }
    
    # ==================== CHAT BOUND METHODS ====================
    
    async def chat_arsip(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Arsipkan chat"""
        chat = await client.get_chat(chat_id)
        result = await chat.arsip()
        return f"Chat '{chat.title or chat.first_name}' berhasil diarsipkan"
    
    async def chat_unarsip(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Batal arsipkan chat"""
        chat = await client.get_chat(chat_id)
        result = await chat.unarsip()
        return f"Chat '{chat.title or chat.first_name}' berhasil dibatalkan arsip"
    
    async def chat_set_judul(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Set judul chat"""
        title = kwargs.get('title', 'Judul Baru')
        chat = await client.get_chat(chat_id)
        result = await chat.set_judul(title)
        return f"Judul chat berhasil diubah menjadi '{title}'"
    
    async def chat_set_deskripsi(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Set deskripsi chat"""
        description = kwargs.get('description', 'Deskripsi baru')
        chat = await client.get_chat(chat_id)
        result = await chat.set_deskripsi(description)
        return f"Deskripsi chat berhasil diubah"
    
    async def chat_set_foto(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Set foto chat"""
        photo = kwargs.get('photo')
        if not photo:
            return "❌ Parameter foto diperlukan"
        
        chat = await client.get_chat(chat_id)
        result = await chat.set_foto(photo)
        return f"Foto chat berhasil diubah"
    
    async def chat_hapus_foto(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Hapus foto chat"""
        chat = await client.get_chat(chat_id)
        result = await chat.hapus_foto()
        return f"Foto chat berhasil dihapus"
    
    async def chat_ban_member(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Ban member dari chat"""
        ban_user_id = kwargs.get('user_id')
        if not ban_user_id:
            return "❌ Parameter user_id diperlukan"
        
        chat = await client.get_chat(chat_id)
        result = await chat.ban_member(ban_user_id)
        return f"User {ban_user_id} berhasil di-ban dari chat"
    
    async def chat_unban_member(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Unban member dari chat"""
        unban_user_id = kwargs.get('user_id')
        if not unban_user_id:
            return "❌ Parameter user_id diperlukan"
        
        chat = await client.get_chat(chat_id)
        result = await chat.unban_member(unban_user_id)
        return f"User {unban_user_id} berhasil di-unban dari chat"
    
    async def chat_restrict_member(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Restrict member di chat"""
        restrict_user_id = kwargs.get('user_id')
        if not restrict_user_id:
            return "❌ Parameter user_id diperlukan"
        
        # Default permissions (restricted)
        permissions = types.ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False
        )
        
        chat = await client.get_chat(chat_id)
        result = await chat.restrict_member(restrict_user_id, permissions)
        return f"User {restrict_user_id} berhasil dibatasi di chat"
    
    async def chat_promote_member(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Promote member di chat"""
        promote_user_id = kwargs.get('user_id')
        if not promote_user_id:
            return "❌ Parameter user_id diperlukan"
        
        # Default privileges (basic admin)
        privileges = types.ChatPrivileges(
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_promote_members=False,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True
        )
        
        chat = await client.get_chat(chat_id)
        result = await chat.promote_member(promote_user_id, privileges)
        return f"User {promote_user_id} berhasil dipromosikan di chat"
    
    async def chat_get_member(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Get info member dari chat"""
        get_user_id = kwargs.get('user_id', user_id)
        
        chat = await client.get_chat(chat_id)
        member = await chat.get_member(get_user_id)
        
        return f"Member Info:\n" \
               f"User: {member.user.first_name} (@{member.user.username})\n" \
               f"Status: {member.status}\n" \
               f"Join Date: {member.joined_date or 'N/A'}\n" \
               f"Promoted By: {member.promoted_by.first_name if member.promoted_by else 'N/A'}"
    
    async def chat_get_members(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Get daftar member dari chat"""
        limit = kwargs.get('limit', 10)
        
        chat = await client.get_chat(chat_id)
        members = await chat.get_members(limit=limit)
        
        member_list = []
        for member in members:
            member_list.append(f"- {member.user.first_name} (@{member.user.username}) - {member.status}")
        
        return f"Daftar Member (Top {limit}):\n" + "\n".join(member_list)
    
    async def chat_add_members(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Add member ke chat"""
        user_ids = kwargs.get('user_ids', [])
        if not user_ids:
            return "❌ Parameter user_ids diperlukan"
        
        chat = await client.get_chat(chat_id)
        result = await chat.add_members(user_ids)
        return f"Berhasil menambahkan {len(user_ids)} member ke chat"
    
    async def chat_join(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Join chat"""
        join_chat_id = kwargs.get('join_chat_id', chat_id)
        
        chat = await client.get_chat(join_chat_id)
        result = await chat.join()
        return f"Berhasil bergabung ke chat '{chat.title or chat.first_name}'"
    
    async def chat_leave(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Leave chat"""
        leave_chat_id = kwargs.get('leave_chat_id', chat_id)
        
        chat = await client.get_chat(leave_chat_id)
        result = await chat.leave()
        return f"Berhasil keluar dari chat '{chat.title or chat.first_name}'"
    
    async def chat_mark_unread(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Mark chat as unread"""
        chat = await client.get_chat(chat_id)
        result = await chat.mark_unread()
        return f"Chat berhasil ditandai sebagai belum dibaca"
    
    async def chat_set_protected(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Set protected content"""
        enabled = kwargs.get('enabled', True)
        
        chat = await client.get_chat(chat_id)
        result = await chat.set_protected_content(enabled)
        return f"Konten terlindungi berhasil {'diaktifkan' if enabled else 'dinonaktifkan'}"
    
    async def chat_unpin_all(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Unpin all messages"""
        chat = await client.get_chat(chat_id)
        result = await chat.unpin_all_messages()
        return f"Semua pesan berhasil di-unpin"
    
    async def chat_delete(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Delete chat (channel/supergroup)"""
        delete_chat_id = kwargs.get('delete_chat_id', chat_id)
        
        chat = await client.get_chat(delete_chat_id)
        result = await chat.delete_chat()
        return f"Chat berhasil dihapus"
    
    async def chat_set_slow_mode(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Set slow mode"""
        seconds = kwargs.get('seconds', 60)
        
        chat = await client.get_chat(chat_id)
        result = await chat.set_slow_mode(seconds)
        return f"Slow mode berhasil diatur ke {seconds} detik"
    
    async def chat_get_online_count(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Get online count"""
        chat = await client.get_chat(chat_id)
        count = await chat.get_online_count()
        return f"Jumlah member online: {count}"
    
    async def chat_get_event_log(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Get event log"""
        limit = kwargs.get('limit', 10)
        
        chat = await client.get_chat(chat_id)
        events = await chat.get_event_log(limit=limit)
        
        event_list = []
        for event in events:
            event_list.append(f"- {event.action} by {event.user.first_name} at {event.date}")
        
        return f"Event Log (Top {limit}):\n" + "\n".join(event_list)
    
    async def chat_backup(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Backup chat"""
        limit = kwargs.get('limit', 100)
        
        chat = await client.get_chat(chat_id)
        messages = await chat.backup_chat(limit=limit)
        return f"Backup berhasil: {len(messages)} pesan di-backup"
    
    # ==================== MESSAGE BOUND METHODS ====================
    
    async def message_reply_text(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Reply message dengan text"""
        reply_text = kwargs.get('text', 'Reply dari bound method')
        
        if message.reply_to_message:
            target_message = message.reply_to_message
        else:
            target_message = message
        
        result = await target_message.reply_text(reply_text)
        return f"Reply berhasil dikirim"
    
    async def message_reply_photo(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Reply message dengan photo"""
        photo = kwargs.get('photo')
        caption = kwargs.get('caption', 'Foto dari bound method')
        
        if not photo:
            return "❌ Parameter photo diperlukan"
        
        if message.reply_to_message:
            target_message = message.reply_to_message
        else:
            target_message = message
        
        result = await target_message.reply_photo(photo, caption=caption)
        return f"Reply foto berhasil dikirim"
    
    async def message_reply_video(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Reply message dengan video"""
        video = kwargs.get('video')
        caption = kwargs.get('caption', 'Video dari bound method')
        
        if not video:
            return "❌ Parameter video diperlukan"
        
        if message.reply_to_message:
            target_message = message.reply_to_message
        else:
            target_message = message
        
        result = await target_message.reply_video(video, caption=caption)
        return f"Reply video berhasil dikirim"
    
    async def message_reply_audio(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Reply message dengan audio"""
        audio = kwargs.get('audio')
        caption = kwargs.get('caption', 'Audio dari bound method')
        
        if not audio:
            return "❌ Parameter audio diperlukan"
        
        if message.reply_to_message:
            target_message = message.reply_to_message
        else:
            target_message = message
        
        result = await target_message.reply_audio(audio, caption=caption)
        return f"Reply audio berhasil dikirim"
    
    async def message_reply_document(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Reply message dengan document"""
        document = kwargs.get('document')
        caption = kwargs.get('caption', 'Document dari bound method')
        
        if not document:
            return "❌ Parameter document diperlukan"
        
        if message.reply_to_message:
            target_message = message.reply_to_message
        else:
            target_message = message
        
        result = await target_message.reply_document(document, caption=caption)
        return f"Reply document berhasil dikirim"
    
    async def message_edit_text(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Edit message text"""
        new_text = kwargs.get('text', 'Teks diedit dengan bound method')
        
        if message.reply_to_message:
            target_message = message.reply_to_message
        else:
            target_message = message
        
        result = await target_message.edit_text(new_text)
        return f"Teks pesan berhasil diedit"
    
    async def message_edit_caption(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Edit message caption"""
        new_caption = kwargs.get('caption', 'Caption diedit dengan bound method')
        
        if message.reply_to_message:
            target_message = message.reply_to_message
        else:
            target_message = message
        
        result = await target_message.edit_caption(new_caption)
        return f"Caption pesan berhasil diedit"
    
    async def message_edit_media(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Edit message media"""
        media = kwargs.get('media')
        
        if not media:
            return "❌ Parameter media diperlukan"
        
        if message.reply_to_message:
            target_message = message.reply_to_message
        else:
            target_message = message
        
        result = await target_message.edit_media(media)
        return f"Media pesan berhasil diedit"
    
    async def message_delete(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Delete message"""
        if message.reply_to_message:
            target_message = message.reply_to_message
        else:
            target_message = message
        
        result = await target_message.delete_message()
        return f"Pesan berhasil dihapus"
    
    async def message_forward(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Forward message"""
        to_chat_id = kwargs.get('to_chat_id', chat_id)
        
        if message.reply_to_message:
            target_message = message.reply_to_message
        else:
            target_message = message
        
        result = await target_message.forward_message(to_chat_id)
        return f"Pesan berhasil di-forward ke {to_chat_id}"
    
    async def message_copy(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Copy message"""
        to_chat_id = kwargs.get('to_chat_id', chat_id)
        
        if message.reply_to_message:
            target_message = message.reply_to_message
        else:
            target_message = message
        
        result = await target_message.copy_message(to_chat_id)
        return f"Pesan berhasil di-copy ke {to_chat_id}"
    
    async def message_pin(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Pin message"""
        if message.reply_to_message:
            target_message = message.reply_to_message
        else:
            target_message = message
        
        result = await target_message.pin_message()
        return f"Pesan berhasil di-pin"
    
    async def message_unpin(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Unpin message"""
        if message.reply_to_message:
            target_message = message.reply_to_message
        else:
            target_message = message
        
        result = await target_message.unpin_message()
        return f"Pesan berhasil di-unpin"
    
    async def message_download_media(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Download media from message"""
        file_name = kwargs.get('file_name', 'download_file')
        
        if message.reply_to_message:
            target_message = message.reply_to_message
        else:
            target_message = message
        
        if not target_message.media:
            return "❌ Pesan tidak memiliki media"
        
        result = await target_message.download_media(file_name)
        return f"Media berhasil didownload: {result}"
    
    async def message_click_inline_button(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Click inline button"""
        button_text = kwargs.get('button_text')
        button_data = kwargs.get('button_data')
        
        if message.reply_to_message:
            target_message = message.reply_to_message
        else:
            target_message = message
        
        result = await target_message.click_inline_button(button_text=button_text, button_data=button_data)
        return f"Inline button berhasil diklik: {result}"
    
    # ==================== USER BOUND METHODS ====================
    
    async def user_get_common_chats(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Get common chats with user"""
        target_user_id = kwargs.get('user_id', user_id)
        
        user = await client.get_users(target_user_id)
        chats = await user.get_common_chats()
        
        chat_list = []
        for chat in chats:
            chat_list.append(f"- {chat.title or chat.first_name} ({chat.id})")
        
        return f"Chat bersama dengan {user.first_name}:\n" + "\n".join(chat_list)
    
    async def user_get_profile_photos(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Get user profile photos"""
        target_user_id = kwargs.get('user_id', user_id)
        limit = kwargs.get('limit', 5)
        
        user = await client.get_users(target_user_id)
        photos = await user.get_profile_photos(limit=limit)
        
        return f"User {user.first_name} memiliki {len(photos)} foto profil"
    
    async def user_block(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Block user"""
        target_user_id = kwargs.get('user_id', user_id)
        
        user = await client.get_users(target_user_id)
        result = await user.block_user()
        
        return f"User {user.first_name} berhasil diblokir"
    
    async def user_unblock(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Unblock user"""
        target_user_id = kwargs.get('user_id', user_id)
        
        user = await client.get_users(target_user_id)
        result = await user.unblock_user()
        
        return f"User {user.first_name} berhasil dibuka blokir"
    
    async def user_send_message(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Send message to user"""
        # Parse params string jika ada
        params = kwargs.get('params', '')
        if params:
            # Format: user_id:text atau @username:text
            parts = params.split(':', 1)
            if len(parts) >= 2:
                target_user_str = parts[0].strip()
                text = parts[1].strip()
                
                # Handle username atau user_id
                if target_user_str.startswith('@'):
                    target_user_str = target_user_str[1:]
                
                # Try to resolve user
                try:
                    if target_user_str.isdigit():
                        target_user_id = int(target_user_str)
                    else:
                        # Try to get user by username
                        user_obj = await client.get_users(target_user_str)
                        target_user_id = user_obj.id
                except Exception as e:
                    console.error(f"Error resolving user {target_user_str}: {e}")
                    return f"❌ Tidak dapat menemukan user: {target_user_str}"
            else:
                return "❌ Format parameter salah. Gunakan: user_id:text atau @username:text"
        else:
            # Fallback ke kwargs
            target_user_id = kwargs.get('user_id', user_id)
            text = kwargs.get('text', 'Pesan dari bound method')
        
        try:
            user = await client.get_users(target_user_id)
            result = await client.send_message(
                chat_id=target_user_id,
                text=text
            )
            
            return f"Pesan berhasil dikirim ke {user.first_name}"
        except Exception as e:
            console.error(f"Error sending message to user {target_user_id}: {e}")
            return f"❌ Error mengirim pesan: {str(e)}"
    
    async def user_send_photo(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Send photo to user"""
        # Parse params string jika ada
        params = kwargs.get('params', '')
        if params:
            # Format: user_id:photo:caption atau @username:photo:caption
            parts = params.split(':', 2)
            if len(parts) >= 2:
                target_user_str = parts[0].strip()
                photo = parts[1].strip()
                caption = parts[2].strip() if len(parts) > 2 else 'Foto dari bound method'
                
                # Handle username atau user_id
                if target_user_str.startswith('@'):
                    target_user_str = target_user_str[1:]
                
                # Try to resolve user
                try:
                    if target_user_str.isdigit():
                        target_user_id = int(target_user_str)
                    else:
                        # Try to get user by username
                        user_obj = await client.get_users(target_user_str)
                        target_user_id = user_obj.id
                except Exception as e:
                    console.error(f"Error resolving user {target_user_str}: {e}")
                    return f"❌ Tidak dapat menemukan user: {target_user_str}"
            else:
                return "❌ Format parameter salah. Gunakan: user_id:photo:caption atau @username:photo:caption"
        else:
            # Fallback ke kwargs
            target_user_id = kwargs.get('user_id', user_id)
            photo = kwargs.get('photo')
            caption = kwargs.get('caption', 'Foto dari bound method')
        
        if not photo:
            return "❌ Parameter photo diperlukan"
        
        try:
            user = await client.get_users(target_user_id)
            result = await client.send_photo(
                chat_id=target_user_id,
                photo=photo,
                caption=caption
            )
            
            return f"Foto berhasil dikirim ke {user.first_name}"
        except Exception as e:
            console.error(f"Error sending photo to user {target_user_id}: {e}")
            return f"❌ Error mengirim foto: {str(e)}"

    # ==================== INLINE QUERY BOUND METHODS ====================
    
    async def inline_query_answer(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Answer inline query"""
        results = kwargs.get('results', [])
        
        if not results:
            return "❌ Parameter results diperlukan"
        
        # Simulasi inline query (untuk testing)
        return f"Inline query berhasil dijawab dengan {len(results)} hasil"
    
    # ==================== JOIN REQUEST BOUND METHODS ====================
    
    async def join_request_approve(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Approve join request"""
        target_user_id = kwargs.get('user_id', user_id)
        
        result = await client.approve_chat_join_request(chat_id, target_user_id)
        return f"Permintaan join dari user {target_user_id} berhasil disetujui"
    
    async def join_request_decline(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Decline join request"""
        target_user_id = kwargs.get('user_id', user_id)
        
        result = await client.decline_chat_join_request(chat_id, target_user_id)
        return f"Permintaan join dari user {target_user_id} berhasil ditolak"
    
    async def join_request_approve_all(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Approve all join requests"""
        result = await client.approve_all_chat_join_requests(chat_id)
        return f"Semua permintaan join berhasil disetujui"
    
    async def join_request_decline_all(self, user_id: int, chat_id: int, client, message, **kwargs):
        """Decline all join requests"""
        result = await client.decline_all_chat_join_requests(chat_id)
        return f"Semua permintaan join berhasil ditolak" 