from pytube import YouTube, Playlist
from pytube import exceptions
from moviepy.editor import *
import os
import re


def help_command():
    print('=====================================')
    print('commands')
    print('exit - exit')
    print('video - download video')
    print('playlist - download whole playlist')
    print('audio - download audio')
    print('=====================================')


def advanced_help_command():
    print('=====================================')
    print('advanced commands')
    print('streams - display all streams')
    print('itag - (in video case) get by itag (only for mp4 and progressive)')
    print('=====================================')


def check_link(link):
    try:
        return YouTube(link)
    except exceptions.RegexMatchError:
        return False


def get_qualities(yt, format_type):
    qualities = {}
    re_res = '[0-9]{3,}p'
    re_audio = '[0-9]{2,}kbps'

    if format_type == 'video':
        for stream in yt.streams.filter(file_extension="mp4"):
            try:
                quality, itag = get_qualities_helper(re_res, qualities, str(stream))
                qualities[quality] = itag
            except TypeError:
                pass

    elif format_type == 'audio':
        for stream in yt.streams:
            try:
                quality, itag = get_qualities_helper(re_audio, qualities, str(stream))
                qualities[quality] = itag
            except TypeError:
                pass

    return qualities


def get_qualities_helper(re_quality, qualities, stream):
    re_itag = 'itag="[0-9]+"'
    quality = re.findall(re_quality, str(stream))
    itag = re.findall(re_itag, str(stream))

    if quality:
        [quality] = quality
        quality = quality
        [itag] = itag
        itag = itag[6:-1]

        if quality in qualities:
            pass
        else:
            return quality, itag


def add_audio_to_video(audio_path, video_path, output_path):
    print('=====================================')
    print('Adding audio to video')
    clip = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    videoclip = clip.set_audio(audio)
    videoclip.write_videofile(output_path)
    print('=====================================')
    print('Done!')


def download_file(format_type, link, just_audio=True):

        yt = check_link(link)
        if not yt:
            print('Invalid link')
            return

        quality = get_qualities(yt, format_type)
        if not quality:
            return

        displayed_qualities = []
        for key in quality:
            displayed_qualities.append(key)

        print(f'*************************************\n{yt.title}\n*************************************')
        print(f'quality: {displayed_qualities}')

        while True:

            chosen_quality = input('Choose quality/exit/advanced: ')
            if chosen_quality == 'exit':
                break

            elif chosen_quality == 'streams':
                print('=====================================\nPrinting streams')
                for stream in yt.streams:
                    print(stream)
                print('=====================================')

            elif chosen_quality == 'advanced':
                advanced_help_command()

            elif chosen_quality == 'itag':
                try:
                    print(yt.streams.get_by_itag(int(chosen_quality)))
                    if input('Download this stream? y/n: ').lower() == 'y':
                        yt.streams.get_by_itag(int(chosen_quality)).download()
                        print('Stream downloaded!')
                        break
                    else:
                        break
                except KeyError:
                    print('Invalid quality')

            else:
                try:
                    print(yt.streams.get_by_itag(quality[chosen_quality]))
                    if input('Download this video? y/n: ').lower() == 'y':
                        if format_type == 'video':
                            yt.streams.get_by_itag(quality[chosen_quality]).download(output_path="temp/video")
                            print('Video downloaded')
                            title = yt.streams.get_by_itag(quality[chosen_quality]).title
                            if not yt.streams.get_by_itag(quality[chosen_quality]).is_progressive:
                                print('Video has no audio, must download it separately')
                                download_file('audio', link, just_audio=False)

                                video_path_mp4 = f'temp/video/{title}.mp4'
                                audio_path_mp3 = f'temp/audio/{title}.mp3'
                                audio_path_webm = f'temp/audio/{title}.webm'
                                final_path = f'downloaded/{title}.mp4'

                                if os.path.exists(video_path_mp4):
                                    if os.path.exists(audio_path_mp3):
                                        add_audio_to_video(audio_path_mp3, video_path_mp4, final_path)
                                        os.remove(audio_path_mp3)
                                    elif os.path.exists(audio_path_webm):
                                        add_audio_to_video(audio_path_webm, video_path_mp4, final_path)
                                        os.remove(audio_path_webm)
                                    else:
                                        print(f'Could not find file - {audio_path_mp3} / {audio_path_webm}')
                                    os.remove(video_path_mp4)
                                else:
                                    print(f'Could not find file - {video_path_mp4}')

                                break
                            else:
                                path = f'temp/video/{title}.mp4'
                                if os.path.exists(path):
                                    os.replace(path, f'downloaded/{title}.mp4')
                                break

                        elif format_type == 'audio':
                            if just_audio:
                                yt.streams.get_by_itag(quality[chosen_quality]).download(output_path="downloaded")
                            else:
                                yt.streams.get_by_itag(quality[chosen_quality]).download(output_path="temp/audio")
                            print('Audio downloaded!')
                            break
                    else:
                        break
                except KeyError:
                    print('Invalid quality')


print('Welcome to YouTube downloader')
print('To start working just paste link to video or playlist')
print('Type "help" for commands')
print('Type "exit" to exit')
while True:
    command = input('~ ')

    if command == 'help':
        help_command()

    elif command == 'exit':
        break

    elif command == 'playlist':
        p = Playlist(command)
        try:
            for vid in p.videos:
                print(vid.streams)
        except KeyError:
            print('KeyError')

    elif command == 'video':
        while True:
            link = input('Link/exit ~ ')
            if link == 'exit':
                break
            else:
                download_file('video', link)

    elif command == 'audio':
        while True:
            link = input('Link/exit ~ ')
            if link == 'exit':
                break
            else:
                download_file('audio', link)
