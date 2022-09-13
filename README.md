# sdutils: Stable Diffusion Utility Wrapper

Stable Diffusion General utilities wrapper including: Video to Video, Image to Image, Template Prompt Generation system and more, for use with any stable diffusion model.

Note, this is by far not a finished project and it will be continously improved upon. This was kept as modular as possible save for including torch code in the `genutils.generate` function. I am doing this because as I use stable diffusion in code, I realize the need for specific things.

## Features
* Easy prompt randomization
* Image2Image generation witih seed control
* Video2Video generation with seed control and overrides
* Multiple Image to Multiple Image generation
* Batch Processing for Image2Image and Video2Video - Get as many as you want from one input
* Outputs all seeds, strengths and prompts generated into a file called vidmap.json
* Stores all output videos and images with seed data and index number for easy association with stored map

`PromptGenerator` *promptgen.py* a standalone class that generates prompts based on possibilities you give it so that you can easily change out any word or phrase in your prompt with a random entry from a list of possibilities.  It makes prompt templates re-usable, just change the data to get different prompts

`Scaffold` *genutils.py* a standalone class that holds all the utility functions and takes a (device, scheduler, pipe) from the torch environment thus wrapping the initial Stable Diffusion functionality and utility functions into one class, and expanding on that functionality with a Video2Video function, and batching.

*sdunlock.py* includes an unlocked version of the pipelines for Text to Image and Image to Image.

## The greatest standalone feature here: PromptGenerator

This is a unique (afaik) way to separate your data you want to rotate/randomize in your prompt and your prompt itself.

Imagine you have a prompt:  
```python
_prompt = 'A tall, skinny man walking along a tight rope at night.'
```

But you want to have options for how the man looks, what he's doing and when, plus you want Stable Diffusion to render from those options randomly or in a rotating fashion. Let's even go so far as to say you want that to be different on every new image you render.  What do you do?  You make your prompt like this:
```python
_prompt = 'A $height, $composure $sex $action $timeofday'
```

Then you give your prompt what to fill in for that template
```python
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
```

Add it to a prompt generator object
```python
prompt = PromptGenerator(_prompt, data)
```

Then every time you call prompt.generate() function it will give you a new generated text prompt
```python
for i in range(0, 10):
  print(prompt.generate())
```

This should output something along these lines:
```python
('A average height, fat woman walking on a tightrope during a hailstorm', 0.5, {'height': 'average height', 'composure': 'fat', 'sex': 'woman', 'action': 'walking on a tightrope', 'timeofday': 'during a hailstorm'})

('A tall, fat woman dressed as a clown in the morning', 0.5, {'height': 'tall', 'composure': 'fat', 'sex': 'woman', 'action': 'dressed as a clown', 'timeofday': 'in the morning'})

('A short, skinny woman on a trapese at dawn', 0.5, {'height': 'short', 'composure': 'skinny', 'sex': 'woman', 'action': 'on a trapese', 'timeofday': 'at dawn'})

('A short, fit woman walking on a tightrope at sunset', 0.5, {'height': 'short', 'composure': 'fit', 'sex': 'woman', 'action': 'walking on a tightrope', 'timeofday': 'at sunset'})

('A tall, fat woman drinking a coffee at sunset', 0.5, {'height': 'tall', 'composure': 'fat', 'sex': 'woman', 'action': 'drinking a coffee', 'timeofday': 'at sunset'})

('A average height, wide shouldered man drinking a coffee at dawn', 0.5, {'height': 'average height', 'composure': 'wide shouldered', 'sex': 'man', 'action': 'drinking a coffee', 'timeofday': 'at dawn'})

('A tall, fat man dressed as a clown at night', 0.5, {'height': 'tall', 'composure': 'fat', 'sex': 'man', 'action': 'dressed as a clown', 'timeofday': 'at night'})

('A tall, wide shouldered woman drinking a coffee at dawn', 0.5, {'height': 'tall', 'composure': 'wide shouldered', 'sex': 'woman', 'action': 'drinking a coffee', 'timeofday': 'at dawn'})

('A tall, fat man doing yoga at sunset', 0.5, {'height': 'tall', 'composure': 'fat', 'sex': 'man', 'action': 'doing yoga', 'timeofday': 'at sunset'})

('A average height, wide shouldered woman walking on a tightrope at sunset', 0.5, {'height': 'average height', 'composure': 'wide shouldered', 'sex': 'woman', 'action': 'walking on a tightrope', 'timeofday': 'at sunset'})

```

The tuple that `prompt.generate()` outputs is `(prompt, strength, data_map)`

* `prompt` - The prompt string to feed to your diffusion model
* `strength` - For use with img2img and video2video
* `data_map` - You can use this if you want to store the attributes of your creations in an index file for instance, this is used in `Scaffold` for example

## How to use PromptGenerator and Scaffold with Stable Diffusion

First thing first, you have to include the libraries
```python
from promptgen import PromptGenerator
from genutils import Scaffold
```

Make sure to have your `device`, `scheduler` and `pipe` declared in your torch code, then put them in the scaffold ...
```python
scaffold = Scaffold(device, scheduler, pipe)
```

## Prompt Generation and data setup
Setting up a new Prompt with different possible outputs
```python
map = {
  'attribute1': ['tall', 'short', 'lumpy'],
  'attribute2': ['headed', 'framed', 'legged'],
  ...
}
prompt = PromptGenerator('A self portrait of a $attribute1 $attribute2 person', map)
```

What about getting a text prompt from this?
```python
text_prompt, strength, prompt_data = prompt.generate()

```

## Examples

### Image2Image Example generating 1 image with a random seed
```python
img_path = 'path_to_some_image.jpg'

scaffold.generate(
  img_path,
  prompt,
  num_seeds = 1
)
```

### Image2Image Generate Many Images with different seeds from one Image
```python
scaffold.generate(
  img_path,
  prompt,
  num_seeds = 100
)
```

### Video2Video Example
```python
video_path = 'path_to_some_video.mp4'
map = { ... }
prompt = PromptGenerator( ... )

scaffold.generate_video(
  video_path,
  prompt
)
```

### Batch Video2Video Example
```python
# Generate 10 different videos from one video
scaffold.generate_batch_videos(
  video_path,
  10,
  prompt
)
```

### Prompts that change at Keyframes using PromptGenerator
```python
# Make a bunch of videos with different subjects and the same sequence of scenes
map = {
  'aspect': ['hairy', 'hairless', 'suspicious looking', 'happy'],
  'creature': ['chinchilla', 'armadillo', 'cockatil', 'ferret', 'rooster']
}

prompt = PromptGenerator({
  0: 'a $aspect $creature walking on a tightrope. wide angle shot from the side.',
  122: 'a $aspect $creature falling in the air tumbling. wide angle shot from below.',
  184: 'a $aspect $creature falling into a small drinking glass.',
  192: 'a $aspect $creature squished inside a small drinking glass.'
}, map)

scaffold.generate_batch_videos(
  video_path,
  100,
  prompt
)
```

## Notes about Video2Video and getting it just right

If you use the strength override as arguments to the scaffold.generate_video and scaffold.generate_batch_videos functions, you can test around for the right `strength` for your set of prompt possibilities. This should help you find a good tradeoff between matching your prompt set more and being a choppy animation.

For example: if you do strength 0.1 or around there, you can get really smooth video, but not much dreaming toward the prompt, whereas if you do 0.7 you can get a pretty choppy but still good video that matches your prompt much better.

My suggestion is to use a video that approximates the same style and actions as you want to recreate with your prompts, AND to make the prompt possibilities mostly include things that are going to be very different, using the !! and (( syntax to aid this. That will allow you to keep your strength relatively down so that you get unique enough videos that are also not so choppy.

## Coming Soon
* K_Euler sampler reversal trick for Video2Video consistency
* Image/Video in-painting and out-painting

