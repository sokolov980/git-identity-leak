import imageio
import os

def animate(frames_dir, out="timeline.gif"):
    images = []
    for f in sorted(os.listdir(frames_dir)):
        images.append(imageio.imread(os.path.join(frames_dir, f)))
    imageio.mimsave(out, images, duration=0.15)
