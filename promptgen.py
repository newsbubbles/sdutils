import random, json
from string import Template
from random import sample

'''
	Prompt Generation from Template

	Includes
		Simple way to create prompt templates: prompt.generate()
		Random choice on variables given a map of choices
		Generation freezing for use with video to video utility
'''

class PromptGenerator:

	def __init__(self, prompt, kws, default_strength=0.5, frozen=False):
		self.prompt = prompt
		self.template = Template(prompt)
		self.keywords = kws
		self.strength = default_strength
		self.last_output = None
		self.frozen = frozen
		print(self.keywords)
		print(self.prompt)

	def freeze(self):
		self.frozen = True

	def unfreeze(self):
		self.frozen = False

	def get_map(self, kws=None, counts=None, use_random=True, use_average=True, use_max=True):
		if kws is None:
			kws = self.keywords
		o, m, b, x = {}, [], False, None

		# pass for choosing the keywords either using negate matrix or not
		for k, v in kws.items():
			# TODO: make a copy of v, then remove anything in negate[k]
			
			c = random.choice(v)
			o[k] = c if type(c) is not tuple else c[0]
			if type(c) is tuple:
				m.append(c[1])
				x = x if len(c) < 3 else c[2]
			
			# (average or max) m or use strength if no m
			l = len(m)
			t = 0
			if l > 0:
				if use_average:
					for i in m:
						t += i
					_m = t / l
				if use_max:
					_m = max(m)
			else:
				_m = self.strength

			b = type(c) is tuple and b == False

		# o is the dict map for the chosen words from the keywords
		# _m is a maximum or average strength given by any keywords that specify a given strength
		# b is a boolean value that just represents if any of the given values are tuples
		# x is a value which, if set, will be the extra text from the tuple in the value
		return o, _m, b, x

	def generate(self, force=False):
		# return frozen output if required
		if not force:
			if self.frozen and self.last_output is not None:
				return self.last_output

		m, _m, _b, x = self.get_map()

		#translate to final prompt and strength
		_strength = _m
		_extra = '' if x is None else x
		_prompt = self.template.substitute(**m) + _extra
		_prompt = _prompt.strip()

		self.last_output = (_prompt, _strength, m)
		return self.last_output

if __name__ == "__main__":

	'''## The keyword map ###

		It is a dict of lists that can include string values or tuples
		The map serves the purpose of mapping some defined value at random to some keyword included in the prompt template

		if a tuple is len 2, this is a float value that overrides default strength
		if a tuple is len 3, the third value is an extra text to be added at the end of the prompt
		if a tuple is len 4, a negation matrix is passed which negates specific values in other keywords that should not be included in the final choice of values
	'''

	kws = {
			'clothing': [
					'neopunk',
					'neonpunk',
					'cyberpunk',
					'solarpunk',
					'tribalpunk',
					'junglepunk',
			],
			'accessories': [
					'a helmet',
					'sunglasses',
					'bracelets',
					'military boots',
					'a pleather jacket',
					'fantasy gear',
			],
			'sex': [
					'man',
					'woman',
					'cyborg man',
					'cyborg woman',
					'android man',
					'android woman',
			],
			'timeofday': [
					'night',
					'sunset',
			],
			'place': [
					'city',
					'theme park',
					'new york',
					'los angeles',
					'paris',
					'tokyo',
					'london',
					'madrid',
					'mumbai',
					'new dehli',
					'mexico city',
					'bangkok',
					'kuala lumpur',
					'berlin',
					'helsinki',
					'marrakesh',
					'seattle',
					'megalopolis',
					'megacity',
					'taiwan',
					'hong kong',
					'beirut',
					'johannesburg',
			],
			'placestyle': [
					'alien',
					'abandoned',
					'!!neon-lit!!',
					'busy',
					'rusty',
					'!!red district!! of',
					'destroyed',
					'burning',
					'post-apocalyptic',
					'desertified',
			],
			'background': [
					'flying cars and spaceships',
					'a suspended highway',
					'a large avenue',
					'a busy intersection',
					'megastructures',
					'weird architecture buildings',
					'!!futuristic architecture!! buildings',
					'a space port',
					'a sea port with futuristic yachts and commercial boats',
					'a desert',
					'a jungle',
					'an alien landscape',
					'strange colored clouds',
					'people stepping into futuristic flying vehicles',
					'people walking across an intersection',
					'nobody',
			],
			'realism': [
					'ultra-realistic',
					'realistic',
					'movie still',
			],
			'media': [
					'photo',
					'Cycles Render',
					'digital photo',

			],
			'photography': [
					'aperture',
					'autochrome',
					'blue hour lighting',
					'circular polarizer',
					'depth of field 100mm',
					'depth of field 270mm',
					'hdr effect',
					'high exposure', 
					'rule of thirds',
			],
	}

	# The prompt should explain the scene in the image with extra details as keywords
	# it is a template that gets processed with a random sampling from the kw map space
	# notice that it uses the dollar sign inf front of a key from the keyword map above to represent a part of the prompt
	prompt = 'a $sex with $clothing clothing and $accessories standing in the middle of a street in a futuristic $placestyle $place at $timeofday with $background in the background. $photography photography. HD $media, !!$realism!!'

	p_ = PromptGenerator(prompt, kws, strength=0.4)

	for i in range(0, 3):
		print(p_.generate())