# Code to combine audio and image into an MP4
'''
Creating an MP4 File with Image and Audio
'''

from moviepy.editor import AudioFileClip, ImageClip

def create_mp4_with_image_and_audio(image_file, audio_file, output_file, fps=24):
    # Load the audio file
    audio_clip = AudioFileClip(audio_file)

    # Create a video clip from an image
    video_clip = ImageClip(image_file, duration=audio_clip.duration)

    # Set the fps for the video clip
    video_clip = video_clip.set_fps(fps)

    # Set the audio of the video clip as the audio clip
    video_clip = video_clip.set_audio(audio_clip)

    # Write the result to a file
    video_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')

