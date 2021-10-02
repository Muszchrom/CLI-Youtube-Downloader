from pytube import YouTube, Playlist
from pytube import exceptions
from moviepy.editor import *
import os
import re


def input_link_loop(format_type):
    while True:
        link = input('Link/exit ~ ')
        if link == 'exit':
            return
        else:
            download_file(format_type, link)


def help_command(advanced=False):
    if advanced:
        print('=====================================')
        print('advanced commands')
        print('streams - display all streams')
        print('itag - (in video case) get by itag (only for mp4 and progressive)')
        print('=====================================')
        return
    print('=====================================')
    print('commands')
    print('exit - exit')
    print('video - download video')
    print('playlist - download whole playlist')
    print('audio - download audio')
    print('=====================================')


def print_streams(yt):
    print('=====================================\nPrinting streams')
    for stream in yt.streams:
        print(stream)
    print('=====================================')


def check_link(link):
    try:
        return YouTube(link)
    except exceptions.RegexMatchError:
        return


def get_qualities(yt, format_type):
    qualities = {}
    re_res = '[0-9]{3,}p'
    re_audio = '[0-9]{2,}kbps'

    print(yt.streams)

    if format_type == 'video':
        for stream in yt.streams.filter(file_extension="mp4"):
            x = get_qualities_helper(re_res, qualities, str(stream))
            if x:
                quality, itag = x
                qualities[quality] = itag

    elif format_type == 'audio':
        for stream in yt.streams:
            x = get_qualities_helper(re_audio, qualities, str(stream))
            if x:
                quality, itag = x
                qualities[quality] = itag

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
            return
        else:
            return [quality, itag]


def add_audio_to_video(audio_path, video_path, output_path):
    print('=====================================')
    print('Adding audio to video')
    clip = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    videoclip = clip.set_audio(audio)
    if not os.path.exists('downloaded'):
        os.mkdir('downloaded')
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

        chosen_quality = input('Choose quality/exit/advanced ~ ')
        if chosen_quality == 'exit':
            return

        elif chosen_quality == 'streams':
            print_streams(yt)

        elif chosen_quality == 'advanced':
            help_command(advanced=True)

        elif chosen_quality == 'itag':
            print('Command under development')
            pass
            # try:
            #     print(yt.streams.get_by_itag(int(chosen_quality)))
            #     if input('Download this stream? y/n: ').lower() == 'y':
            #         yt.streams.get_by_itag(int(chosen_quality)).download()
            #         print('Stream downloaded!')
            #         return
            #     else:
            #         return
            # except KeyError:
            #     print('Invalid quality')

        else:
            try:
                print(yt.streams.get_by_itag(quality[chosen_quality]))
                if input('Download this stream? y/n ~ ').lower() == 'y':
                    if format_type == 'video':
                        print('Downloading video...')
                        if yt.streams.get_by_itag(quality[chosen_quality]).is_progressive:
                            yt.streams.get_by_itag(quality[chosen_quality]).download(output_path="downloaded")
                            print('Video downloaded!')
                            return

                        yt.streams.get_by_itag(quality[chosen_quality]).download(output_path="temp/video")
                        print('Video downloaded!')

                        print('!Video has no audio, must download it separately')
                        download_file('audio', link, just_audio=False)

                        title = yt.streams.get_by_itag(quality[chosen_quality]).title
                        audio_path = f'temp/audio/{os.listdir("temp/audio")[0]}'
                        video_path = f'temp/video/{os.listdir("temp/video")[0]}'
                        final_path = f'downloaded/{title}.mp4'

                        if os.path.exists(video_path):
                            if os.path.exists(audio_path):
                                add_audio_to_video(audio_path, video_path, final_path)
                                os.remove(audio_path)
                            else:
                                print(f'Could not find file - {audio_path}')
                            os.remove(video_path)
                        else:
                            print(f'Could not find file - {video_path}')

                    elif format_type == 'audio':
                        print('Downloading audio...')
                        if just_audio:
                            yt.streams.get_by_itag(quality[chosen_quality]).download(output_path="temp/audio")
                            print('Audio downloaded\nFixing extension...')
                            audio_wrong_format = AudioFileClip(f'temp/audio/{os.listdir("temp/audio")[0]}')
                            audio_wrong_format.write_audiofile(f'downloaded/{yt.streams.get_by_itag(quality[chosen_quality]).title}.mp3')
                            os.remove(f'temp/audio/{os.listdir("temp/audio")[0]}')
                            print('Audio downloaded and saved as mp3!')
                        else:
                            yt.streams.get_by_itag(quality[chosen_quality]).download(output_path="temp/audio")
                            print('Audio downloaded!')
                return
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
        input_link_loop(command)

    elif command == 'audio':
        input_link_loop(command)
