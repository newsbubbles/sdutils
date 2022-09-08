# sdutils
Stable Diffusion Video to Video, Image to Image, Template Prompt Generation system and more, for use with any stable diffusion model


Scaffold holds all the util functions and takes a (device, scheduler, pipe) from the torch environment thus wrapping the initial Stable Diffusion functionality and utility functions into one class, and expanding on that functionality with a Video2Video function, and batching



Takes just a map of possible attributes and a prompt template including those attribute variables into a prompt.

scaffold = Scaffold(device, scheduler, pipe)

Prompt Generation and data setup

map = {
  'attribute1': ['possibility1', 'possibility2', 'possibility3'],
  'attribute2': ['possibility1', 'possibility2', 'possibility3'],
  ...
}
prompt = PromptGenerator('A $attribute1 $attribute2 person', map)

Image2Image Example

scaffold.generate(

)

Image2Image Generate Many Images with different seeds from one Image

scaffold.generate(

)

Video2Video Example

scaffold.generate_video(

)

Batch Video2Video Example

scaffold.generate_batch_videos(

)
