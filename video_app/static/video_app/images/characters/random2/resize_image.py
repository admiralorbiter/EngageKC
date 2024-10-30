from PIL import Image

# Load the image
img_path = 'annabeth.png'
img = Image.open(img_path)

# Define the padding size
padding = 25  # Adjust as needed

# Create a new image with padding
new_width = img.width + padding * 2
new_height = img.height + padding * 2
new_img = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))  # Transparent background

# Paste the original image onto the center of the new image
new_img.paste(img, (padding, padding))

# Save the modified image
new_img.save(img_path)
