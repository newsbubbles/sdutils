# sdutils: Stable Diffusion Utility Wrapper

Stable Diffusion General utilities wrapper including: Video to Video, Image to Image, Template Prompt Generation system and more, for use with any stable diffusion model.

Note, this is by far not a finished technology and it will be continously improved upon. This was kept as modular as possible save for including torch code in the `genutils.generate` function.

## Features
* Image2Image generation witih seed control
* Video2Video generation with seed control and overrides
* Batch Processing for Image2Image and Video2Video - Get as many as you want from one input
* Outputs all seeds, strengths and prompts generated into a file called vidmap.json
* Stores all output videos and images with seed data and index number for easy association with stored map

## Coming Soon
* Keyframes for video2video and prompt changes
* Image/Video in-painting and out-painting
* NFT Listing Capabilities for OpeanSea perhaps?

`PromptGenerator` generates prompts based on possibilities you give it so that you can easily change out any word or phrase in your prompt with a random entry from a list of possibilities.  It makes prompt templates re-usable, just change the data to get different prompts

`Scaffold` holds all the util functions and takes a (device, scheduler, pipe) from the torch environment thus wrapping the initial Stable Diffusion functionality and utility functions into one class, and expanding on that functionality with a Video2Video function, and batching

Takes just a map of possible attributes and a prompt template including those attribute variables into a prompt.

```
# make sure to have your device, scheduler and pipe declare in your torch code, then put them in the scaffold ...

scaffold = Scaffold(device, scheduler, pipe)
```

## Prompt Generation and data setup
Setting up a new Prompt with different possible outputs
```
map = {
  'attribute1': ['tall', 'short', 'lumpy'],
  'attribute2': ['headed', 'framed', 'legged'],
  ...
}
prompt = PromptGenerator('A self portrait of a $attribute1 $attribute2 person', map)
```
What about getting a text prompt from this?
```
text_prompt = prompt.generate()

# would output from above example:
#   A self portrait of a tall legged person
#   A self portrait of a lumpy headed person
#   ...
# for every time you call the generate function you get a different result based on values from the map
```

## Examples

### Image2Image Example generating 1 image with a random seed
```
img_path = 'path_to_some_image.jpg'

scaffold.generate(
  img_path,
  prompt,
  num_seeds = 1
)
```

### Image2Image Generate Many Images with different seeds from one Image
```
scaffold.generate(
  img_path,
  prompt,
  num_seeds = 100
)
```

### Video2Video Example
```
video_path = 'path_to_some_video.mp4'
map = { ... }
prompt = PromptGenerator( ... )

scaffold.generate_video(
  video_path,
  prompt
)
```

### Batch Video2Video Example
```
# Generate 10 different videos from one video
scaffold.generate_batch_videos(
  video_path,
  10,
  prompt
)
```
