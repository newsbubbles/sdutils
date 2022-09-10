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

	def stats(self):
		x = 1
		l = len(self.keywords)
		for k, v in self.keywords.items():
			x *= len(v)
		print(l, 'dimensions', x, 'unique possibilities')
		return l, x

if __name__ == "__main__":

	'''## The keyword map ###

		It is a dict of lists that can include string values or tuples
		The map serves the purpose of mapping some defined value at random to some keyword included in the prompt template

		if a tuple is len 2, this is a float value that overrides default strength
		if a tuple is len 3, the third value is an extra text to be added at the end of the prompt
		if a tuple is len 4, a negation matrix is passed which negates specific values in other keywords that should not be included in the final choice of values
	'''
	_prompt = 'A $height, $composure $sex $action $timeofday'

	data = {
	  'height': [
	    'tall',
	    'short',
	    'average height'
	  ],
	  'composure': [
	    'fat',
	    'skinny',
	    'lanky',
	    'fit',
	    'muscular',
	    'wide shouldered',
	  ],
	  'sex': [
	    'man',
	    'woman',
	  ],
	  'action': [
	    'walking on a tightrope',
	    'drinking a coffee',
	    'playing soccer',
	    'doing yoga',
	    'on a trapese',
	    'dressed as a clown',
	  ],
	  'timeofday': [
	    'at night',
	    'in the morning',
	    'in the afternoon',
	    'at dawn',
	    'at sunset',
	    'during a hailstorm',
	  ],
	}

	prompt = PromptGenerator(_prompt, data)

	for i in range(0, 10):
	  print(prompt.generate())