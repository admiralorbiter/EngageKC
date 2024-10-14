# Contributing New Characters

This guide will help you add new character sets to the application.

## Steps to Add a New Character Set

1. Create a new CSV file
   - Navigate to `video_app/static/video_app/characters/`
   - Create a new CSV file named after your character set (e.g., `starwars.csv`)
   - Follow this format for each character:
     ```
     name,description,filename
     Character Name,A brief description of the character,image_filename.jpg
     ```

2. Add character images
   - Create a new folder in `video_app/static/video_app/characters/` named after your character set (e.g., `starwars`)
   - Add all character images to this folder
   - Ensure image filenames match those specified in the CSV file

3. Update available character sets (optional)
   - The `get_available_character_sets()` function in `video_app/utils.py` automatically detects new character sets
   - No code changes are required unless you want to modify how character sets are detected or displayed

## Example: Adding a Star Wars Character Set

1. Create `video_app/static/video_app/characters/starwars.csv`:
   ```
   name,description,filename
   Luke Skywalker,A Jedi Knight and hero of the Rebel Alliance,luke.jpg
   Darth Vader,A powerful Sith Lord and father of Luke Skywalker,vader.jpg
   ```

2. Add images:
   - Create folder: `video_app/static/video_app/characters/starwars/`
   - Add images: `luke.jpg` and `vader.jpg` to this folder

3. The new character set will be automatically available in the application

## Best Practices

- Use high-quality, appropriately sized images (recommended: 300x300 pixels)
- Provide concise but informative character descriptions
- Ensure consistency in naming conventions across CSV files and image folders
- Test the new character set in a development environment before deploying

## Need Help?

If you encounter any issues or have questions about contributing new characters, please open an issue in the project repository or contact the development team.