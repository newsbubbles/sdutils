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
from torch import autocast
from tqdm.auto import tqdm

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

class Scaffold:

	def __init__(self, device, scheduler, pipe):
		self.device = device
		self.scheduler = scheduler
		self.pipe = pipe

	def preprocess(self, image):
			w, h = image.size
			w, h = map(lambda x: x - x % 32, (w, h))  # resize to integer multiple of 32
			image = image.resize((w, h), resample=PIL.Image.LANCZOS)
			image = np.array(image).astype(np.float32) / 255.0
			image = image[None].transpose(0, 3, 1, 2)
			image = torch.from_numpy(image)
			return 2.*image - 1.

	def load_image(self, file_path):
		fp = file_path
		if os.path.exists(fp):
			print('Loading', fp)
			a = PIL.Image.open(fp).convert('RGB').resize((512, 512))
			return self.preprocess(a)
		else:
			print('NOT FOUND', fp)
			return None

	def load_index(self, file_path):
		if not os.path.exists(file_path):
			return []
		else:
			with open(file_path, 'r') as f:
				r = json.load(f)
			return r

	def save_index(self, index_map, file_path):
		with open(file_path, 'w+') as f:
			json.dump(index_map, f)
		return True		

	# Image2Image Generates and saves multiple images based on an input image or list of images and a list of seeds
	def generate(self, image_path: str, prompt: PromptGenerator, strength=0.5, seeds=None, num_seeds=10, fileid=None, filename=None, guidance_scale=7.5, ext='jpg', overwrite_strength=False, images=None, output_folder='_out/', verbose=False, image_index='map.json'):
		if seeds is None:
			seeds = sample(range(0, 999999999), num_seeds)
		file_id = '' if fileid is None else str(fileid) + '_'
		use_images = True if images is not None else False
		print('use images:', use_images, 'strength_o:', strength)
		index = self.load_index(image_index)
		for i, s in enumerate(seeds):
			generator = torch.Generator(device=self.device).manual_seed(s)
			with autocast(self.device):
					_prompt, _strength, _attr = prompt.generate()
					if overwrite_strength:
						_strength = strength
					im_, ich = None, None
					if use_images:
						ichi = random.choice(images)
						ich = os.path.basename(ichi)
						if type(ich) is tuple:
							_strength = ich[1]
							_ich = ich[0]
						else:
							_ich = ich
						ichs = _ich.split('.')
						im_ = self.load_image(ichi)
						uie = _ich
						file_id = ichs[0] + '_'
						input_path = ich
					if im_ is None:
						im_ = self.load_image(image_path)
						uie = ''
					if verbose:
						print(file_id, i, s, _strength, uie)
						print(_prompt)
					_im = self.pipe(prompt=_prompt, init_image=im_, strength=_strength, guidance_scale=guidance_scale, generator=generator)["sample"]
					im = _im[0]
					fn = file_id + str(i) + '_' + str(s) if filename is None else filename
					im.save(output_folder + fn + '.' + ext)
					index.append({'input': input_path if ich is None else ich, 'seed': s, 'strength': _strength, 'prompt': _prompt, 'attr': _attr})
					self.save_index(index, image_index)

	def video_to_gif(self, input_video, output_gif, scale=320, fps=15, loop=0):
		os.system('ffmpeg -i ' + input_video + ' -vf "fps=' + str(fps) + ',scale=' + str(scale) + ':-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop ' + str(loop) + ' ' + output_gif)

	# Video2Video Generates and saves a single output video from an input video
	def generate_video(self, input_path, prompt, seed=None, strength=0.5, guidance_scale=7.5, strength_r=1.0, _start=0, frame_range=[0, 9999999999], scratch_folder='_in/', output_folder='_out/', override_strength=False, out_path=None, make_thumbnail=False, thumb_folder='thumbs/', video_index='vidmap.json'):
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

		## load existing video attributes index
		index = self.load_index(video_index)

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
				self.generate(
					filepath, 
					prompt, 
					_strength if not override_strength else strength, 
					seeds=[seed], 
					filename=str(i).rjust(6, '0'), 
					ext='png', 
					guidance_scale=guidance_scale, 
					overwrite_strength=True, 
					output_folder=output_folder,
					image_index=None,
				)

		## save attributes map
		index.append({'input': input_path, 'seed': seed, 'strength': _strength, 'prompt': _prompt, 'attr': _attr})
		self.save_index(index, video_index)

		os.system('ffmpeg -i ' + output_folder + '%06d.png -c:v libx264 -vf fps=20 -pix_fmt yuv420p ' + out_path)

		if make_thumbnail:
			print('thumbs:', thumb_folder)
			os.system('mkdir -p ' + thumb_folder)
			gifname = os.path.basename(out_path).split('.')[0]
			gif_path = thumb_folder + gifname + '.gif'
			print('gif path:', gif_path)
			self.video_to_gif(out_path, gif_path)

	## Video2Videos Multiple videos from one video ##

	def generate_batch_videos(self, input_video, num_videos, prompt, strength=0.5, guidance_scale=7.5, seeds=None, scratch_folder='_in/', output_folder='_out/', frame_range=None, make_thumbnails=False):
		seeds = seeds if seeds is not None else sample(range(0, 999999999), num_videos)
		frame_range = frame_range if frame_range is not None else (0, 9999999999)
		vidname = os.path.basename(input_video).split('.')[0]
		sfv = scratch_folder + vidname + '/'
		ofv = output_folder + vidname + '/'

		os.system('shred -n 40 -u ' + ofv + '/*')

		for i, s in enumerate(seeds):

			print('Generating Video', s, 'Number:', i, 'of', num_videos, 'strength_o:', strength)

			self.generate_video(
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

	## instantiate the object with torch device, scheduler, and pipe
	device, scheduler, pipe = None, None, None
	scaffold = Scaffold(device, scheduler, pipe)

	## Generate a batch of 10 videos from some input video and a prompt template
	kws = {
		'phototype': ['portrait', 'profile'],
		'haircolor': ['blonde', 'brown', 'black'],
		'sex': ['man', 'woman'],
	}
	prompt_ = 'a $phototype photo of a $haircolor haired $sex.'
	prompt = PromptGenerator(prompt_, kws)

	scaffold.generate_batch_videos('input_video.mp4', 10, prompt, strength=0.35)

	## Generate a batch of 100 different images from one input image
	scaffold.generate('input_image.jpg', prompt, num_seeds=100, strength=0.7)

	## Generate a single video from that same prompt
	scaffold.generate_video('input_video.mp4', prompt)