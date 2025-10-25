# JCL Test Generator

A web application for generating random 50-question tests from JCL (Junior Classical League) mock test data across multiple years and subjects.

## Features

- **Random Test Generation**: Creates 50-question tests by randomly selecting questions from all available years (2009-2019)
- **Multiple Subjects**: Supports 10 different JCL subjects including Classical Art, Mythology, Derivatives, History, and more
- **Cross-Year Scrambling**: Questions are mixed from different years to create unique test experiences
- **Timer**: 50-minute timer for realistic test conditions
- **Score Tracking**: Automatic scoring and results display
- **Responsive Design**: Works on desktop and mobile devices

## Available Subjects

1. **Classical Art** - Questions about classical art, architecture, and visual culture
2. **Classical Geography** - Questions about ancient geography, locations, and places  
3. **Derivatives I** - Basic Latin derivative questions and word formation
4. **Derivatives II** - Advanced Latin derivative questions and etymology
5. **History of the Empire** - Questions about Roman Empire history and events
6. **History of Monarchy and Republic** - Questions about early Roman history
7. **Mottoes, Abbreviations, and Quotations** - Latin sayings, abbreviations, and famous quotations
8. **Mythology** - Greek and Roman mythology, gods, heroes, and stories
9. **Vocabulary I** - Basic Latin vocabulary and word meanings
10. **Vocabulary II** - Advanced Latin vocabulary and specialized terms

## Data Statistics

- **Total Questions**: Over 5,000 questions across all subjects
- **Years Covered**: 2009-2019 (11 years of data)
- **Questions per Subject**: 400-550 questions each
- **Questions per Test**: 50 randomly selected questions

## Local Testing

To test the website locally:

1. Make sure you have Python 3 installed
2. Run the test server:
   ```bash
   python3 test_server.py
   ```
3. Open your browser to `http://localhost:8000`

## GitHub Pages Deployment

To deploy this website to GitHub Pages:

### Method 1: Direct Repository (Recommended)

1. Create a new GitHub repository (e.g., `jcl-test-generator`)
2. Copy all files from this directory to your repository
3. Go to repository Settings → Pages
4. Select "Deploy from a branch" → "main" branch → "/ (root)"
5. Your site will be available at `https://yourusername.github.io/jcl-test-generator`

### Method 2: GitHub Pages with Custom Domain

1. Follow Method 1 steps
2. In repository Settings → Pages, add your custom domain
3. Update DNS settings as instructed by GitHub

## File Structure

```
JCL_AT_Buddy/
├── website/                # JCL Test Generator Website
│   ├── index.html          # Main website page
│   ├── styles.css          # CSS styling
│   ├── script.js           # JavaScript functionality
│   ├── data/               # Consolidated test data
│   │   ├── Classical_Art.json
│   │   ├── Classical_Geography.json
│   │   ├── Derivatives_I.json
│   │   ├── Derivatives_II.json
│   │   ├── History_of_the_Empire.json
│   │   ├── History_of_the_Monarchy_and_Republic.json
│   │   ├── Mottoes_Abbreviations_and_Quotations.json
│   │   ├── Mythology.json
│   │   ├── Vocabulary_I.json
│   │   ├── Vocabulary_II.json
│   │   └── index.json
│   ├── consolidate_data.py # Script to consolidate raw data
│   ├── test_server.py      # Local testing server
│   └── README.md            # This file
└── data/raw-data/          # Original JCL test data (2009-2019)
```

## Data Processing

The `consolidate_data.py` script processes raw JCL test data from the `JCL_AT_Buddy` project and creates consolidated JSON files for the web application. This script:

- Combines questions from all years (2009-2019) for each subject
- Adds metadata (source year, subject) to each question
- Creates individual subject files for efficient loading
- Generates a data index for the application

## Usage

1. **Select a Subject**: Choose from the 10 available test subjects
2. **Start Test**: The system randomly selects 50 questions from all years for that subject
3. **Answer Questions**: Navigate through questions using Previous/Next buttons
4. **Submit Test**: Complete the test or let the timer expire
5. **View Results**: See your score and percentage
6. **Take Another Test**: Generate a new random test

## Technical Details

- **Frontend**: Pure HTML, CSS, and JavaScript (no frameworks required)
- **Data Format**: JSON files with structured question data
- **Randomization**: Fisher-Yates shuffle algorithm for question selection
- **Timer**: Client-side JavaScript timer with automatic submission
- **Storage**: No server-side storage required (perfect for GitHub Pages)

## Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## Contributing

To add new test data:

1. Add new JSON files to the `data/` directory following the existing format
2. Update the subject list in `script.js` if adding new subjects
3. Test locally using `test_server.py`
4. Deploy to GitHub Pages

## License

This project is for educational use with JCL test data.
