import os, json

'''
	NFTDataMapper
		Responsible for transforming Scaffold map data into a metadata standard format
		Formats Supported: OpenSea
'''
class NFTDataMapper:

	def __init__(self, name, asset_url, data, url=None, prompt=None, attr_map=None, value_map=None, exclude=None):
		self.name = name
		self.data = data 		# required: data in the Scaffold format with attr as a key
		self.map = attr_map		# if used only include attributes in the map {'old_attr_name': 'new_attr_name', ...}
		self.valmap = value_map # if used, allows remap of attribute values
		self.has_valmap = value_map is not None
		self.prompt = prompt	# if used override prompt from data
		self.asset_url = asset_url
		self.url = url
		self.exclude = exclude 	# if used, exclude all attributes from list

	# retrieve a value from the data or from data.attr and perform value transcription if necessary
	def get(self, key):
		if key is None:
			return ''
		o = ''
		if key in self.data:
			o = self.data[key]
		else:
			if key in self.data['attr']:
				o = self.data['attr'][key]
				if self.has_valmap:
					if o in self.valmap:
						o = self.valmap[o]
		return o

	# retrieve a key from the attribute key map
	def _attr(self, key):
		if self.map is None:
			return key
		if key in self.map:
			return self.map[key]
		else:
			return key

	# retrieve a value that is mapped from 
	def attr(self, key):
		return self.get(self._attr(key))

	def filter(self, key):
		if self.exclude is None:
			return True
		return key not in self.exclude

	def opensea(self, out_path=None):
		attr = []
		for k, v in self.data['attr'].items():
			if self.filter(k):
				attr.append({'trait_type': self._attr(k), 'value': self.get(k)})
		o = {
			'description': self.get('description'),
			'external_url': self.url,
			'image': self.asset_url,
			'name': self.name,
			'attributes': attr,
			'comment': 'https://docs.opensea.io/docs/metadata-standards',
		}
		if out_path is not None:
			with open(out_path, 'w+') as f:
				json.dump(o, f)
		return o

	def enjin(self, out_path):
		return None
