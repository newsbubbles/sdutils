"""
	GenUtil: Video2Video, Image2Image Utility Functions
		github: https://github.com/newsbubbles/sd-utils
		Stable Diffusion image and video generation utility functions

		Environment Requirements: ffmpeg, shred

		Includes
			Image loading and pre-processing with pytorch
			Image to Image generation function
			Batch image generation function
			Video generation function
			Video Thumbnail GIF generation function
			Keyframe based prompt switching
			Batch video generation function
			In-painting
			Latent space exploration function (outpainting)
			Text Inversion function
			Prompt Generator utilities
				Keyword/attribute based mapping function
				Randomized attribute insertion upon generation
				Attribute freezing (used for video consistency)
			Output to map json files for automated access to properties of each output

"""

import random, os, json, time
from string import Template
from random import sample

import torch
import PIL
from PIL import Image
import numpy as np

try:
	from promptgen import PromptGenerator
except Exception as pe:
	try:
		from .promptgen import PromptGenerator
	except:
		pass

def preprocess(image):
		w, h = image.size
		w, h = map(lambda x: x - x % 32, (w, h))  # resize to integer multiple of 32
		image = image.resize((w, h), resample=PIL.Image.LANCZOS)
		image = np.array(image).astype(np.float32) / 255.0
		image = image[None].transpose(0, 3, 1, 2)
		image = torch.from_numpy(image)
		return 2.*image - 1.

def load_image(file_path):
	fp = file_path
	if os.path.exists(fp):
		print('Loading', fp)
		a = PIL.Image.open(fp).convert('RGB').resize((512, 512))
		return preprocess(a)
	else:
		print('NOT FOUND', fp)
		return None

# Image2Image Generates and saves multiple images based on an input image or list of images and a list of seeds
def generate(image_path: str, prompt: PromptGenerator, strength=0.5, seeds=None, num_seeds=10, fileid=None, filename=None, guidance_scale=7.5, ext='jpg', overwrite_strength=False, images=None, output_folder='_out/', verbose=False, device="cuda"):
	if seeds is None:
		seeds = sample(range(0, 999999999), num_seeds)
	file_id = '' if fileid is None else str(fileid) + '_'
	use_images = True if images is not None else False
	print('use images:', use_images, 'strength_o:', strength)
	for i, s in enumerate(seeds):
		generator = torch.Generator(device=device).manual_seed(s)
		with autocast(device):
				_prompt, _strength, _attr = prompt.generate()
				if overwrite_strength:
					_strength = strength
				im_ = None
				if use_images:
					ich = random.choice(images)
					if type(ich) is tuple:
						_strength = ich[1]
						_ich = ich[0]
					else:
						_ich = ich
					ichs = _ich.split('.')
					im_ = load_image(_ich)
					uie = _ich
					file_id = ichs[0] + '_'
				if im_ is None:
					im_ = load_image(image_path)
					uie = ''
				if verbose:
					print(file_id, i, s, _strength, uie)
					print(_prompt)
				_im = pipe(prompt=_prompt, init_image=im_, strength=_strength, guidance_scale=guidance_scale, generator=generator)["sample"]
				im = _im[0]
				fn = file_id + str(i) + '_' + str(s) if filename is None else filename
				im.save(output_folder + fn + '.' + ext)

def video_to_gif(input_video, output_gif, scale=320, fps=15, loop=0):
	os.system('ffmpeg -i ' + input_video + ' -vf "fps=' + str(fps) + ',scale=' + str(scale) + ':-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop ' + str(loop) + ' ' + output_gif)

# Video2Video Generates and saves a single output video from an input video
def generate_video(input_path, prompt, seed=None, strength=0.5, guidance_scale=7.5, strength_r=1.0, _start=0, frame_range=[0, 9999999999], scratch_folder='_in/', output_folder='_out/', override_strength=False, out_path=None, make_thumbnail=False, thumb_folder='thumbs/'):
	if seed is None:
		seeds = sample(range(0, 999999999), 1)
		seed = seeds[0]
	out_path = out_path if out_path is not None else 'out_' + str(seed) + '.mp4'
	
	_prompt, _strength, _attr = prompt.generate(force=True)
	prompt.freeze()

	# Scratch Folder generation
	print('strength_o:', strength)
	print('input:', input_path)
	print('scratch:', scratch_folder)
	print('outdir:', output_folder)
	print('output:', out_path)
	if not os.path.exists(input_path):
		print('Path does not exist:', input_path)
		return None
	os.system('mkdir -p ' + output_folder)
	input_f_exists = os.path.exists(scratch_folder)
	print('scratch folder exists?', input_f_exists)
	if not input_f_exists:
		os.system('mkdir -p ' + scratch_folder)
		os.system('ffmpeg -i ' + input_path + ' ' + scratch_folder + '%06d.png')

	## load existing video attributes map
	_lv = []
	if os.path.exists('vidmap.json'):
		with open('vidmap.json', 'r') as f:
			_lv = json.load(f)

	# get the frame file names from the scratch folder
	d = os.listdir(scratch_folder)
	d.sort()

	## Perform frame-by-frame generation
	ld = min(len(d), frame_range[1] - frame_range[0])
	for i, f in enumerate(d):
		if frame_range[0] <= i < frame_range[1]:
			print(i, 'of', ld)
			filepath = scratch_folder + f
			
			#print(filepath)
			generate(
				filepath, 
				prompt, 
				_strength if not override_strength else strength, 
				seeds=[seed], 
				filename=str(i).rjust(6, '0'), 
				ext='png', 
				guidance_scale=guidance_scale, 
				overwrite_strength=True, 
				output_folder=output_folder
			)

	## save attributes map
	_lv.append((input_path, seed, _strength, _prompt, _attr))
	with open('vidmap.json', 'w+') as f:
		json.dump(_lv, f)

	os.system('ffmpeg -i ' + output_folder + '%06d.png -c:v libx264 -vf fps=20 -pix_fmt yuv420p ' + out_path)

	if make_thumbnail:
		print('thumbs:', thumb_folder)
		os.system('mkdir -p ' + thumb_folder)
		gifname = os.path.basename(out_path).split('.')[0]
		gif_path = thumb_folder + gifname + '.gif'
		print('gif path:', gif_path)
		video_to_gif(out_path, gif_path)

## Video2Videos Multiple videos from one video ##

def generate_batch_videos(input_video, num_videos, prompt, strength=0.5, guidance_scale=7.5, seeds=None, scratch_folder='_in/', output_folder='_out/', frame_range=None, make_thumbnails=False):
	seeds = seeds if seeds is not None else sample(range(0, 999999999), num_videos)
	frame_range = frame_range if frame_range is not None else (0, 9999999999)
	vidname = os.path.basename(input_video).split('.')[0]
	sfv = scratch_folder + vidname + '/'
	ofv = output_folder + vidname + '/'

	os.system('shred -n 40 -u ' + ofv + '/*')

	for i, s in enumerate(seeds):

		print('Generating Video', s, 'Number:', i, 'of', num_videos, 'strength_o:', strength)

		generate_video(
				input_video, 
				prompt, 
				s, 
				strength=strength, 
				guidance_scale=guidance_scale,
				frame_range=frame_range,
				override_strength=True,
				scratch_folder=sfv,
				output_folder=ofv,
				make_thumbnail=make_thumbnails,
		)


if __name__ == "__main__":

	## Generate a batch of 10 videos from some input video and a prompt template
	kws = {
		'phototype': ['portrait', 'profile'],
		'haircolor': ['blonde', 'brown', 'black'],
		'sex': ['man', 'woman'],
	}
	prompt_ = 'a $phototype photo of a $haircolor haired $sex.'
	prompt = PromptGenerator(prompt_, kws)

	generate_batch_videos('input_video.mp4', 10, prompt, strength=0.35)

	## Generate a batch of 100 different images from one input image
	generate('input_image.jpg', prompt, num_seeds=100, strength=0.7)

	## Generate a single video from that same prompt
	generate_video('input_video.mp4', prompt)