# VideoEncoder - a telegram bot for compressing/encoding videos in h264 format.
# Copyright (c) 2021 WeebTime/VideoEncoder
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import time

from pyrogram.errors.exceptions.bad_request_400 import (MessageIdInvalid,
                                                        MessageNotModified)
from pyrogram.types import Message

from .. import data, download_dir, upload_doc
from .ffmpeg import encode, get_duration, get_thumbnail
from .progress import progress_for_pyrogram


async def on_task_complete():
    del data[0]
    if len(data) > 0:
        await handle_task(data[0])


async def handle_task(message: Message):
    try:
        msg = await message.reply_text("<code>Downloading video...</code>")
        c_time = time.time()
        filepath = await message.download(
            file_name=download_dir,
            progress=progress_for_pyrogram,
            progress_args=("Downloading...", msg, c_time))
        await msg.edit_text('<code>Encoding...</code>')
        new_file = await encode(filepath, message, msg)
        if new_file:
            await msg.edit_text("<code>Video Encoded, getting metadata...</code>")
            await handle_upload(new_file, message, msg)
            await msg.edit_text('Video Encoded Successfully!')
        else:
            await message.reply_text("<code>Something wents wrong while encoding your file.</code>")
            os.remove(filepath)
    except MessageNotModified:
        pass
    except MessageIdInvalid:
        await msg.edit_text('Download Cancelled!')
    except Exception as e:
        await msg.edit_text(f"<code>{e}</code>")
    await on_task_complete()


async def handle_upload(new_file, message, msg):
    # Variables
    c_time = time.time()
    filename = os.path.basename(new_file)
    duration = get_duration(new_file)
    thumb = get_thumbnail(new_file, download_dir, duration / 4)
    height = 1280
    width = 720
    # Upload
    if upload_doc is True:
        await message.reply_document(
            new_file,
            caption=filename,
            parse_mode=None,
            progress=progress_for_pyrogram,
            progress_args=("Uploading ...", msg, c_time)
        )
    else:
        await message.reply_video(
            new_file,
            supports_streaming=True,
            parse_mode=None,
            caption=filename,
            thumb=thumb,
            duration=duration,
            width=width,
            height=height,
            progress=progress_for_pyrogram,
            progress_args=("Uploading ...", msg, c_time)
        )
        